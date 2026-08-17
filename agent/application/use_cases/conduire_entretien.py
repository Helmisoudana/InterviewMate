import json
from agent.domain.entities.interview import Interview, Question, Reponse, Echange
from agent.domain.ports.llm_port import LLMPort, Message
from agent.domain.ports.session_repository_port import SessionRepositoryPort
from agent.domain.ports.scoring_notifier_port import ScoringNotifierPort

MAX_TENTATIVES_REGENERATION = 3


class ConduireEntretienUseCase:
    def __init__(self, llm: LLMPort, session_repo: SessionRepositoryPort, scoring_notifier: ScoringNotifierPort):
        self.llm = llm
        self.session_repo = session_repo
        self.scoring_notifier = scoring_notifier

    async def _appeler_llm(self, messages: list[Message]) -> dict:
        texte = ""
        async for token in self.llm.stream_completion(messages):
            texte += token
        try:
            return json.loads(texte)
        except json.JSONDecodeError:
            return {"qualite": "correcte", "comportement_inapproprie": False, "question": texte.strip()}

    async def _generer_reponse_valide(self, interview: Interview, messages: list[Message]) -> dict:
        for _ in range(MAX_TENTATIVES_REGENERATION):
            resultat = await self._appeler_llm(messages)
            if interview.peut_poser_question(resultat.get("question", "")):
                return resultat
        raise ValueError(f"Impossible de generer une question inedite apres {MAX_TENTATIVES_REGENERATION} tentatives")

    async def traiter_reponse_candidat(self, session_id: str, texte_reponse: str) -> tuple[str, bool]:
        interview = await self.session_repo.get(session_id)

        prompt_systeme = interview.vers_prompt_systeme()
        messages = [
            Message(role="system", content=prompt_systeme),
            Message(role="user", content=texte_reponse),
        ]

        resultat = await self._generer_reponse_valide(interview, messages)

        qualite = resultat.get("qualite", "correcte")
        comportement_inapproprie = resultat.get("comportement_inapproprie", False)
        nouvelle_question_texte = resultat.get("question", "")

        if interview.echanges:
            interview.echanges[-1].reponse = Reponse(texte=texte_reponse, qualite_percue=qualite)
            interview.ajuster_difficulte(qualite)
            await self.scoring_notifier.notifier_echange_termine(session_id, interview.echanges[-1])

        if comportement_inapproprie:
            interview.signaler_refus()
        else:
            interview.reinitialiser_refus()

        if interview.doit_arreter_anticipativement():
            await self.session_repo.save(session_id, interview)
            return "Entretien interrompu suite a un comportement inapproprie repete.", True

        if interview.doit_changer_de_phase():
            interview.passer_phase_suivante()

        if interview.est_terminee():
            await self.session_repo.save(session_id, interview)
            return "", True

        nouvelle_question = Question(texte=nouvelle_question_texte, phase=interview.phase_actuelle)
        interview.echanges.append(Echange(question=nouvelle_question))

        await self.session_repo.save(session_id, interview)

        return nouvelle_question_texte, False
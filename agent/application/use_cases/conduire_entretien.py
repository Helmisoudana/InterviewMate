from agent.domain.entities.interview import Interview, Question, Reponse, Echange
from agent.domain.ports.llm_port import LLMPort, Message
from agent.domain.ports.session_repository_port import SessionRepositoryPort
from agent.domain.ports.scoring_notifier_port import ScoringNotifierPort


class ConduireEntretienUseCase:
    def __init__(
        self,
        llm: LLMPort,
        session_repo: SessionRepositoryPort,
        scoring_notifier: ScoringNotifierPort,
    ):
        self.llm = llm
        self.session_repo = session_repo
        self.scoring_notifier = scoring_notifier

    async def traiter_reponse_candidat(self, session_id: str, texte_reponse: str) -> str:
        interview = await self.session_repo.get(session_id)

        if interview.echanges:
            interview.echanges[-1].reponse = Reponse(texte=texte_reponse)
            await self.scoring_notifier.notifier_echange_termine(
                session_id, interview.echanges[-1]
            )

        if interview.doit_changer_de_phase():
            interview.passer_phase_suivante()

        prompt_systeme = interview.vers_prompt_systeme()
        messages = [
            Message(role="system", content=prompt_systeme),
            Message(role="user", content=texte_reponse),
        ]

        nouvelle_question_texte = ""
        async for token in self.llm.stream_completion(messages):
            nouvelle_question_texte += token

        if not interview.peut_poser_question(nouvelle_question_texte):
            raise ValueError("Question deja posee, regeneration necessaire")

        nouvelle_question = Question(texte=nouvelle_question_texte, phase=interview.phase_actuelle)
        interview.echanges.append(Echange(question=nouvelle_question))

        await self.session_repo.save(session_id, interview)

        return nouvelle_question_texte
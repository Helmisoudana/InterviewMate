import json
from shared.domain.value_objects import EchangeEvalue, SessionID, Message
from scoring.domain.entities.evaluation import Evaluation
from scoring.domain.ports.notifier_echange_port import NotifierEchangeUseCasePort
from scoring.domain.ports.llm_port import LLMPort
from scoring.domain.services.evaluation_prompt_builder import construire_prompt_evaluation, GRILLE_PAR_DEFAUT


class EvaluerEchangeUseCase(NotifierEchangeUseCasePort):
    def __init__(self, llm: LLMPort, grille_competences: list[str] | None = None):
        self._llm = llm
        self._grille = grille_competences or GRILLE_PAR_DEFAUT
        self._evaluations_par_session: dict[str, list[Evaluation]] = {}

    async def _appeler_llm(self, echange: EchangeEvalue) -> dict:
        prompt = construire_prompt_evaluation(echange, self._grille)
        messages = [Message(role="system", content=prompt)]

        texte = ""
        async for token in self._llm.stream_completion(messages):
            texte += token

        try:
            return json.loads(texte)
        except json.JSONDecodeError:
            return {"competence": self._grille[0], "score": 0.5, "justification": "Reponse LLM non parsable."}

    async def executer(self, echange: EchangeEvalue) -> Evaluation:
        resultat = await self._appeler_llm(echange)

        competence = resultat.get("competence", self._grille[0])
        if competence not in self._grille:
            competence = self._grille[0]

        score = float(resultat.get("score", 0.5))
        score = max(0.0, min(1.0, score))

        evaluation = Evaluation(
            competence=competence,
            score=score,
            justification=resultat.get("justification", ""),
        )

        sid = str(echange.session_id)
        self._evaluations_par_session.setdefault(sid, []).append(evaluation)
        return evaluation

    def evaluations_pour(self, session_id: SessionID) -> list[Evaluation]:
        return self._evaluations_par_session.get(str(session_id), [])
from typing import List
from scoring.domain.ports.llm_scorer_port import LLMScorerPort
from scoring.domain.entities.rapport_score import RapportScore, EvaluationEchange


class FakeLLMScorerAdapter(LLMScorerPort):
    """Fake sans appel reseau, pour tester GenererRapportSessionUseCase sans cle Groq."""

    async def generer_rapport(self, session_id: str, echanges: List[dict]) -> RapportScore:
        evaluations = [
            EvaluationEchange(
                ordre=e.get("ordre", i + 1),
                question=e.get("question_agent", ""),
                reponse=e.get("reponse_candidat", ""),
                qualite_percue=e.get("qualite_percue") or "correcte",
                score_technique=6.0,
                remarque="Evaluation factice (fake adapter).",
            )
            for i, e in enumerate(echanges)
        ]
        return RapportScore(
            session_id=session_id,
            score_global=6.5,
            score_technique=6.0,
            score_communication=7.0,
            points_forts=["Communication claire"],
            points_faibles=["Manque de profondeur technique"],
            recommandations=["Approfondir les structures de donnees"],
            evaluations=evaluations,
        )
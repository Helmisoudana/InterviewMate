import json
import os
from typing import Any, Dict
from groq import AsyncGroq
from scoring.domain.ports.scoring_llm_port import ScoringLLMPort


class GroqScoringAdapter(ScoringLLMPort):
    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        self._client = AsyncGroq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self._model = model

    async def evaluer_transcription(self, transcription: str) -> Dict[str, Any]:
        prompt = f"""
        Tu es un recruteur expert. Analyse la transcription d'entretien suivante et génère une évaluation au format JSON strict.

        Structure du JSON attendu :
        {{
            "score_global": float (entre 0 et 20),
            "score_technique": float (entre 0 et 20),
            "score_communication": float (entre 0 et 20),
            "points_forts": "string détaillant les points forts",
            "points_faibles": "string détaillant les points faibles",
            "recommandations": "string décrivant les conseils"
        }}

        TRANSCRIPTION DE L'ENTRETIEN :
        {transcription}
        """

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Tu réponds uniquement avec un objet JSON valide."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            data = json.loads(response.choices[0].message.content)
            return data
        except Exception as e:
            # Fallback en cas d'erreur de parsing ou d'appel API
            return {
                "score_global": 0.0,
                "score_technique": 0.0,
                "score_communication": 0.0,
                "points_forts": f"Erreur lors de l'évaluation : {str(e)}",
                "points_faibles": "N/A",
                "recommandations": "Relancer l'évaluation ultérieurement.",
            }
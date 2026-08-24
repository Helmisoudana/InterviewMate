import os
import json
from typing import List
from groq import AsyncGroq

from scoring.domain.ports.llm_scorer_port import LLMScorerPort
from scoring.domain.entities.rapport_score import RapportScore, EvaluationEchange

PROMPT_SYSTEME = """Tu es un recruteur technique senior. Analyse l'entretien suivant et genere un rapport JSON structure.

ECHELLE DE NOTATION (0 a 10, utilise-la strictement pour tous les scores) :
- 0-2 : Insuffisant — reponse absente, hors sujet, ou refus de repondre.
- 3-4 : Faible — reponse vague, non structuree, ou revelant une lacune importante.
- 5-6 : Correct — reponse acceptable mais manquant de profondeur ou de precision.
- 7-8 : Bon — reponse claire, structuree, avec des exemples concrets et pertinents.
- 9-10 : Excellent — reponse exhaustive, precise, avec une maitrise demontree du sujet.

METHODE DE PONDERATION (ne fais jamais une simple moyenne arithmetique) :
1. Progression : valorise une amelioration au fil de l'entretien, notamment quand la difficulte augmente.
2. Profondeur technique : une reponse solide sur une question complexe pese plus qu'une bonne reponse sur une question simple.
3. Coherence globale : penalise les contradictions entre les reponses ; valorise la coherence du discours.
4. Communication : evalue la clarte et la structure du discours independamment du contenu technique (score_communication distinct de score_technique).

CONSIGNES DE REDACTION :
- Base chaque remarque et chaque point fort/faible sur un element concret du transcript (cite la question ou la reponse concernee), jamais une formule generique du type "bonne communication" sans justification.
- Si le transcript est trop court ou trop pauvre pour juger un critere, dis-le explicitement dans la remarque correspondante plutot que d'inventer une appreciation.
- Les recommandations doivent etre actionnables (ex: "approfondir la gestion des exceptions en Python"), jamais vagues (ex: "ameliorer ses competences").

Reponds EXCLUSIVEMENT avec un objet JSON valide, sans aucun texte avant ou apres, respectant exactement ce schema :
{
    "score_global": <nombre entre 0 et 10, selon l'echelle ci-dessus>,
    "score_technique": <nombre entre 0 et 10>,
    "score_communication": <nombre entre 0 et 10>,
    "points_forts": [<liste de phrases courtes, chacune justifiee par un element du transcript>],
    "points_faibles": [<liste de phrases courtes, chacune justifiee par un element du transcript>],
    "recommandations": [<liste de conseils actionnables et specifiques>],
    "evaluations": [
        {
            "ordre": <numero du tour, entier>,
            "question": "<question posee, telle quelle>",
            "reponse": "<reponse du candidat, telle quelle>",
            "qualite_percue": "<un mot parmi: insuffisante, vague, correcte, bonne, excellente>",
            "score_technique": <nombre entre 0 et 10 pour CET echange precis>,
            "remarque": "<justification courte et specifique de ce score>"
        }
    ]
}
"""


class GroqScorerAdapter(LLMScorerPort):

    def __init__(self, api_key: str | None = None, model: str = "openai/gpt-oss-120b"):
        cle = api_key or os.getenv("GROQ_API_KEY")
        if not cle:
            raise ValueError("GROQ_API_KEY manquante : definis-la dans ton .env")
        self._client = AsyncGroq(api_key=cle)
        self._model = model

    async def generer_rapport(self, session_id: str, echanges: List[dict]) -> RapportScore:
        transcript = "\n".join(
            f"Tour {e['ordre']} - Question: {e['question_agent']} | "
            f"Reponse: {e['reponse_candidat']} | Qualite percue en direct: {e.get('qualite_percue') or 'non evaluee'}"
            for e in echanges
        )

        messages = [
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": f"TRANSCRIPT DE L'ENTRETIEN:\n{transcript}"},
        ]

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content)

        evaluations = [
            EvaluationEchange(
                ordre=ev.get("ordre", 0),
                question=ev.get("question", ""),
                reponse=ev.get("reponse", ""),
                qualite_percue=ev.get("qualite_percue", ""),
                score_technique=ev.get("score_technique", 0.0),
                remarque=ev.get("remarque", ""),
            )
            for ev in data.get("evaluations", [])
        ]

        return RapportScore(
            session_id=session_id,
            score_global=data.get("score_global", 0.0),
            score_technique=data.get("score_technique"),
            score_communication=data.get("score_communication"),
            points_forts=data.get("points_forts", []),
            points_faibles=data.get("points_faibles", []),
            recommandations=data.get("recommandations", []),
            evaluations=evaluations,
        )
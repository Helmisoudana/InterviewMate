import asyncio
from dotenv import load_dotenv
load_dotenv()
from scoring.infrastructure.adapters.groq_scorer_adapter import GroqScorerAdapter
from scoring.infrastructure.adapters.pdf_rapport_adapter import generer_pdf_rapport

ECHANGES_FACTICES = [
    {
        "ordre": 1,
        "question_agent": "Peux-tu m'expliquer la différence entre une liste et un tuple en Python ?",
        "reponse_candidat": "Une liste est mutable, un tuple est immutable. On utilise une liste quand on doit modifier les éléments, un tuple pour des données fixes.",
        "qualite_percue": "correcte",
    },
    {
        "ordre": 2,
        "question_agent": "Comment gérerais-tu une fuite mémoire dans une application Python long-running ?",
        "reponse_candidat": "Euh, je sais pas trop, peut-être redémarrer le serveur ?",
        "qualite_percue": "faible",
    },
]


async def main():
    session_id = "session_dev_test_simple"

    scorer = GroqScorerAdapter()
    rapport = await scorer.generer_rapport(session_id, ECHANGES_FACTICES)

    print(f"Rapport genere pour {session_id}")
    print(f" - Score global       : {rapport.score_global}")
    print(f" - Score technique    : {rapport.score_technique}")
    print(f" - Score communication: {rapport.score_communication}")
    print(f" - Points forts       : {rapport.points_forts}")
    print(f" - Points faibles     : {rapport.points_faibles}")
    print(f" - Recommandations    : {rapport.recommandations}")
    print(f" - Nb evaluations     : {len(rapport.evaluations)}")

    chemin_pdf = generer_pdf_rapport(rapport, f"rapport_{session_id}.pdf")
    print(f" - PDF genere ici     : {chemin_pdf}")


if __name__ == "__main__":
    asyncio.run(main())
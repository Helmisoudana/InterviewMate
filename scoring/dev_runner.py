"""
Point d'entree LOCAL pour tester le module scoring seul, en isolation.
Jamais utilise en production -- uniquement pour dev/debug.
"""
import asyncio

from shared.domain.value_objects import SessionID, EchangeEvalue, InterviewStage
from scoring.application.use_cases.evaluer_echange import EvaluerEchangeUseCase
from scoring.application.use_cases.generer_rapport_final import GenererRapportFinalUseCase
from scoring.infrastructure.adapters.in_process_scoring_client import InProcessScoringClient
from scoring.infrastructure.fakes.fake_storage_client_adapter import FakeStorageClientAdapter

# Passe a True pour utiliser le vrai Ollama, False pour le FakeLLMAdapter (rapide, pas besoin d'Ollama lance)
UTILISER_VRAI_LLM = True

if UTILISER_VRAI_LLM:
    from scoring.infrastructure.adapters.groq_adapter import OllamaAdapter
    llm = OllamaAdapter(model="llama3:latest")
else:
    from scoring.infrastructure.fakes.fake_llm_adapter import FakeLLMAdapter
    llm = FakeLLMAdapter()


async def main():
    session_id = SessionID.generate()

    evaluer_uc = EvaluerEchangeUseCase(llm=llm)
    storage_fake = FakeStorageClientAdapter()
    generer_rapport_uc = GenererRapportFinalUseCase(storage_client=storage_fake)

    client = InProcessScoringClient(evaluer_uc, generer_rapport_uc)

    # Simulation de 3 echanges d'entretien
    echanges_test = [
        ("Peux-tu expliquer la difference entre une liste et un tuple ?",
         "Une liste est mutable, un tuple est immutable en Python."),
        ("Comment gererais-tu une exception dans une API REST ?",
         "Je ne sais pas trop, peut-etre avec un try/except."),
        ("Parle-moi d'un bug difficile que tu as resolu.",
         "J'ai eu un bug de concurrence sur un compteur partage entre threads. "
         "J'ai identifie la race condition avec des logs horodates, puis corrige "
         "avec un verrou (lock) autour de la section critique."),
    ]

    print(f"=== Test scoring, session {session_id} ===\n")

    for question, reponse in echanges_test:
        echange = EchangeEvalue(
            session_id=session_id,
            question=question,
            reponse=reponse,
            phase=InterviewStage.TECHNIQUE,
        )
        print(f"Q: {question}")
        print(f"R: {reponse}")

        await client.notifier_echange_termine(echange)
        derniere_eval = evaluer_uc.evaluations_pour(session_id)[-1]
        print(f"-> Evaluation : competence={derniere_eval.competence}, "
              f"score={derniere_eval.score:.2f}, justification={derniere_eval.justification!r}\n")

    rapport = await client.cloturer_session(session_id)
    print("=== RAPPORT FINAL ===")
    print(f"Score global : {rapport.score_global:.2f}")
    print(f"Nombre d'evaluations : {len(rapport.evaluations)}")


if __name__ == "__main__":
    asyncio.run(main())
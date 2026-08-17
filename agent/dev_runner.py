"""
Point d'entrée LOCAL du module `agent`.

Ce fichier n'est PAS un point d'entrée de production (celui-ci est unique
et se trouve à la racine du projet : main.py). Il sert uniquement à faire
tourner ou tester ce module de façon isolée, pendant le développement,
sans dépendre des autres modules ni du container.py global.

Utilise les adapters "Fake" du module (infrastructure/fakes/) plutôt que
les vrais adapters externes, pour rester rapide et indépendant.

Lancer avec :
    python -m agent.dev_runner
"""
import asyncio

from agent.infrastructure.adapters.ollama_adapter import OllamaAdapter
from agent.infrastructure.fakes.fake_session_repository_adapter import FakeSessionRepositoryAdapter
from agent.infrastructure.fakes.fake_scoring_notifier_adapter import FakeScoringNotifierAdapter
from agent.application.use_cases.conduire_entretien import ConduireEntretienUseCase


async def run():
    use_case = ConduireEntretienUseCase(
        llm=OllamaAdapter(),
        session_repo=FakeSessionRepositoryAdapter(),
        scoring_notifier=FakeScoringNotifierAdapter(),
    )

    session_id = "session-interactive-001"

    print("=== Simulation d'entretien InterviewMate ===")
    print("Tape tes reponses comme si tu etais le candidat. L'entretien s'arrete automatiquement a la fin.\n")

    reponse_candidat = "Bonjour, je suis pret a commencer."

    while True:
        question, est_termine = await use_case.traiter_reponse_candidat(session_id, reponse_candidat)

        interview_actuelle = await use_case.session_repo.get(session_id)
        print(f"\n[DEBUG] Phase actuelle : {interview_actuelle.phase_actuelle.value}")
        print(f"[DEBUG] Difficulte actuelle : {interview_actuelle.difficulte_actuelle.value}")
        print(f"[DEBUG] Nombre d'echanges : {len(interview_actuelle.echanges)}")

        if est_termine:
            print("\n=== Entretien termine. Merci d'avoir participe. ===")
            break

        print(f"\nRecruteur : {question}")

        try:
            reponse_candidat = input("Ta reponse : ")
        except (EOFError, KeyboardInterrupt):
            print("\n=== Saisie interrompue, fin de la simulation. ===")
            break


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
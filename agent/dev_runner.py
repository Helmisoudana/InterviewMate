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

from agent.infrastructure.fakes.fake_llm_adapter import FakeLLMAdapter
from agent.infrastructure.fakes.fake_session_repository_adapter import FakeSessionRepositoryAdapter
from agent.infrastructure.fakes.fake_scoring_notifier_adapter import FakeScoringNotifierAdapter
from agent.application.use_cases.conduire_entretien import ConduireEntretienUseCase


async def run():
    use_case = ConduireEntretienUseCase(
        llm=FakeLLMAdapter(),
        session_repo=FakeSessionRepositoryAdapter(),
        scoring_notifier=FakeScoringNotifierAdapter(),
    )

    question = await use_case.traiter_reponse_candidat("session-test-001", "Bonjour, je suis pret")
    print(f"Question generee : {question}")


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
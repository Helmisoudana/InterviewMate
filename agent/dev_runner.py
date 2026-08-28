import asyncio
from agent.infrastructure.adapters.ollama_adapter import OllamaAdapter
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry
from agent.application.use_cases.start_session import StartAgentSessionUseCase
from agent.application.use_cases.conduire_entretien import ConduireEntretienUseCase
from agent.domain.value_objects.interview_phase import DureeEntretien, DifficultyLevel
from shared.domain import SessionID


async def run() -> None:
    llm = OllamaAdapter()
    registry = AgentSessionRegistry()
    start_uc = StartAgentSessionUseCase(llm=llm, registry=registry)
    conduire_uc = ConduireEntretienUseCase(llm=llm, registry=registry)

    session_id = SessionID("session-test")

    question = await start_uc.executer(
        session_id=session_id,
        poste="Développeur backend",
        langue="français",
        duree=DureeEntretien.COURTE,
        difficulte=DifficultyLevel.MOYEN,
    )
    print(f"\nRecruteur : {question}")

    while True:
        try:
            reponse = input("Ta réponse : ")
        except (EOFError, KeyboardInterrupt):
            break

        question, termine = await conduire_uc.traiter_reponse_candidat(session_id, reponse)

        interview = registry.obtenir(session_id.value)
        print(f"[DEBUG] phase={interview.phase_actuelle.value} "
              f"difficulte={interview.difficulte_actuelle.value} "
              f"echanges={len(interview.echanges)}")

        if termine:
            print("\n=== Entretien terminé. ===")
            break

        print(f"\nRecruteur : {question}")


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
from shared.domain import SessionID
from session.infrastructure.adapters.in_memory_session_store import InMemorySessionStore
from session.application.use_cases.create_session import CreateSessionUseCase
from session.application.use_cases.update_session_state import UpdateSessionStateUseCase
from session.application.use_cases.get_session_state import GetSessionStateUseCase
from session.application.use_cases.expire_sessions import ExpireSessionsUseCase
from session.domain.value_objects.session_config import SessionConfig


def construire_session_module(ttl_secondes: int = 1800):
    store = InMemorySessionStore()
    return {
        "store": store,
        "create": CreateSessionUseCase(store),
        "update": UpdateSessionStateUseCase(store),
        "get": GetSessionStateUseCase(store),
        "expire": ExpireSessionsUseCase(store, ttl_secondes),
    }


def main():
    module = construire_session_module()
    session_id = SessionID.generate()
    config = SessionConfig(
        type_entretien="technique",
        niveau="junior",
        poste_vise="Développeur backend",
        duree_max_minutes=30,
    )

    print("--- Création de session ---")
    module["create"].executer(session_id, config)
    print(module["get"].executer(session_id))

    print("\n--- Ajout d'un échange ---")
    module["update"].executer(
        session_id,
        question="Parlez-moi de votre expérience.",
        reponse="J'ai 2 ans d'expérience en développement backend.",
    )
    print(module["get"].executer(session_id))


if __name__ == "__main__":
    main()

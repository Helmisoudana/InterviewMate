from session.infrastructure.adapters.in_memory_session_store import InMemorySessionStore
from session.application.use_cases.create_session import CreateSessionUseCase
from session.application.use_cases.update_session_state import UpdateSessionStateUseCase
from session.application.use_cases.get_session_state import GetSessionStateUseCase
from session.application.use_cases.expire_sessions import ExpireSessionsUseCase


def construire_session_module(ttl_secondes: int = 1800):
    store = InMemorySessionStore()
    return {
        "store": store,
        "create": CreateSessionUseCase(),
        "update": UpdateSessionStateUseCase(),
        "get": GetSessionStateUseCase(store),
        "expire": ExpireSessionsUseCase(store, ttl_secondes),
    }
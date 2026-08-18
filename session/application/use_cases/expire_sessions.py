class ExpireSessionsUseCase:
    def __init__(self, store, ttl_secondes: int = 1800) -> None:
        self._store = store
        self._ttl_secondes = ttl_secondes

    def executer(self) -> list:
        expirees = [
            sid for sid, session in self._store.tout_lister()
            if session.est_expiree(self._ttl_secondes)
        ]
        for sid in expirees:
            self._store.retirer(sid)
        return expirees
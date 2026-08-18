# shared/domain/exceptions.py

class DomainException(Exception):
    """Exception de base pour toutes les erreurs métier du système."""
    def __init__(self, message: str = "Une erreur domaine est survenue."):
        self.message = message
        super().__init__(self.message)


class SessionNotFoundException(DomainException):
    """Levée lorsqu'une session est introuvable."""
    def __init__(self, session_id: str):
        super().__init__(f"La session '{session_id}' n'existe pas.")


class InvalidSessionStateException(DomainException):
    """Levée lorsqu'une opération est effectuée dans un état invalide."""
    pass
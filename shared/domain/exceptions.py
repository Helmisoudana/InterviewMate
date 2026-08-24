
class DomainException(Exception):
    def __init__(self, message: str = "Une erreur domaine est survenue."):
        self.message = message
        super().__init__(self.message)


class SessionNotFoundException(DomainException):
    def __init__(self, session_id: str):
        super().__init__(f"La session '{session_id}' n'existe pas.")


class InvalidSessionStateException(DomainException):
    pass

class ReponseLLMInvalide(Exception):
    pass
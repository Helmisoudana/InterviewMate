class GatewayException(Exception):
    """Exception de base pour le module Gateway."""
    pass


class SessionFermeeError(GatewayException):
    """Levée lorsque la session est déjà fermée."""
    pass


class SessionNonActiveError(GatewayException):
    """Levée lorsque la session n'est pas active."""
    pass


class SessionInvalideError(GatewayException):
    """Levée lorsque la session est invalide."""
    pass

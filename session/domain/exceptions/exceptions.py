class SessionInconnueError(Exception):
    """Exception levée lorsqu'une session demandée n'existe pas dans le magasin de sessions."""
    pass

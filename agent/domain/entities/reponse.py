from dataclasses import dataclass


@dataclass
class Reponse:
    texte: str
    qualite_percue: str | None = None
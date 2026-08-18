from dataclasses import dataclass


@dataclass(frozen=True)
class SessionConfig:
    type_entretien: str      # "technique" | "comportemental" | "system_design"
    niveau: str               # "junior" | "confirme" | "senior"
    poste_vise: str
    duree_max_minutes: int
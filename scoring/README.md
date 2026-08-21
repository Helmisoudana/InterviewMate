# Module Scoring

## Rôle
Analyse chaque échange (question/réponse) de l'entretien pour en évaluer la qualité,
puis produit un rapport final structuré une fois la session terminée.
Fonctionne en tâche de fond, ne doit jamais ralentir la conversation en direct.

## Ports exposés (entrants)
- `NotifierEchangeUseCasePort` : reçoit un échange terminé à évaluer (appelé par AGENT)
- `GenererRapportFinalUseCase` : déclenche la génération du rapport final (appelé en fin d'entretien)

## Ports requis (sortants)
- `StorageClientPort` : pour envoyer le rapport final à STORAGE

## Statut
- Grille d'évaluation : PLACEHOLDER, à définir en équipe avant mise en prod
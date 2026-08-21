# Module Storage

## Rôle
Conserve de façon permanente tout ce qui doit survivre après la fin d'une session :
transcripts, rapports d'évaluation, historique par utilisateur.

## Ports exposés (entrants)
- `TranscriptRepositoryPort` : sauvegarde/lecture des transcripts
- `RapportRepositoryPort` : sauvegarde/lecture des rapports

## Ports requis (sortants)
- Aucun (module terminal / feuille)

## Statut
- Implémentation actuelle : InMemoryStorageAdapter (fake, non persistant)
- À faire : vrai adapter SQLAlchemy/Postgres
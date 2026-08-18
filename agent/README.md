# Module `agent`

## Rôle

Le "cerveau" de l'entretien. Décide quelle question poser, comment relancer
le candidat, quand changer de phase, et quand conclure l'entretien.

## Architecture

Suit l'architecture hexagonale (ports & adapters) :
- `domain/entities/` : objets métier (Question, Reponse, Echange, Interview)
- `domain/value_objects/` : valeurs figées (phases, difficulté, Message)
- `domain/ports/` : contrats (interfaces) — ce dont ce module a besoin de l'extérieur
- `domain/services/` : logique de construction (prompt système)
- `application/use_cases/` : orchestre le domaine via les ports
- `infrastructure/adapters/` : implémentations réelles (Ollama, registry de sessions)
- `infrastructure/fakes/` : implémentations factices pour tester sans dépendance externe

## Ports exposés

`AgentGatewayEngineAdapter` (infrastructure/adapters/gateway_engine_adapter.py) :
point d'entrée que le module `gateway` utilisera pour piloter un entretien
(démarrer, traiter une réponse, terminer).

## Ports requis (ce dont ce module a besoin des autres modules)

- `LLMPort` : génération de texte (implémenté par `OllamaAdapter`)
- `SessionRepositoryPort` : lecture/écriture de l'état de session
  (à implémenter par le module `session/`, actuellement `FakeSessionRepositoryAdapter`)
- `ScoringNotifierPort` : notification d'un échange terminé
  (à implémenter par le module `scoring/`, actuellement `FakeScoringNotifierAdapter`)

## Utilisation en développement

```bash
python -m agent.dev_runner
```

Simulation interactive d'un entretien complet en CLI, avec affichage
de l'état interne (phase, difficulté, nombre d'échanges) à chaque tour.

## Adapters LLM disponibles

- `OllamaAdapter` : LLM local via Ollama, gratuit, nécessite Ollama installé
  et un modèle téléchargé (`ollama pull llama3`). Utilise `format="json"`
  pour fiabiliser la sortie structurée.

## Règles métier principales

- Anti-répétition : une question déjà posée n'est jamais reposée
  (avec 3 tentatives de régénération avant échec)
- Progression des phases : intro (1 question) → technique (4) →
  comportemental (2) → clôture (1)
- Ajustement de difficulté : baisse si réponse vague, augmente si excellente
  (qualité déterminée directement par le LLM, pas par heuristique locale)
- Détection de comportement inapproprié par le LLM ; arrêt anticipé après
  2 détections consécutives
- Arrêt automatique si le temps maximum de session est dépassé
  (30 minutes par défaut, configurable via `duree_max_minutes`)
- Langue de l'entretien fixée au démarrage (français par défaut), non
  modifiable en cours
- Ton/persona configurable (bienveillant, exigeant, neutre) sans toucher
  à la logique de déroulé

## Statut

Développé et testé avec les fakes et avec Ollama en conditions réelles
(entretien interactif complet, ajustement de difficulté et arrêt anticipé
sur comportement inapproprié vérifiés). Deuxième fournisseur LLM (API
cloud) non implémenté à ce stade — module actuellement mono-fournisseur
(Ollama local).
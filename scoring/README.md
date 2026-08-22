# Module `scoring`

## Rôle
<!-- TODO: décrire le rôle fonctionnel du module (voir docs/modules_specification.md) -->

## Structure

```
scoring/
├── domain/            # Entités, value objects, règles métier pures (aucune dépendance externe)
├── application/
│   ├── ports/          # Interfaces (contrats) — ce dont le module a besoin de l'extérieur
│   └── use_cases/       # Orchestrent le domaine via les ports
├── infrastructure/
│   ├── adapters/         # Implémentations concrètes des ports (API externes, DB...)
│   └── fakes/            # Implémentations factices pour les tests / dev_runner
└── dev_runner.py        # Point d'entrée LOCAL pour tester ce module isolément
```

## Ports exposés (in)
<!-- TODO: lister les cas d'usage que ce module expose aux autres -->

## Ports requis (out)
<!-- TODO: lister les dépendances externes attendues (LLM, DB, etc.) -->

## Tester ce module isolément
```bash
python -m scoring.dev_runner
```

## Exceptions
Ce module utilise les exceptions communes définies dans `common/exceptions.py`.
Ne pas créer d'exceptions locales dupliquées — étendre `common/exceptions.py`
si un nouveau type d'erreur métier générique est nécessaire.

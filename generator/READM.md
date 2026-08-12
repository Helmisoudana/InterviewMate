# Générateur de module — InterviewMate

Ce dossier contient le script `generate_module.py`, qui crée automatiquement
le squelette hexagonal d'un nouveau module (`domain/`, `application/`,
`infrastructure/`) directement à la racine du projet.

## Différence avec un générateur de microservices

Ce projet est un **monolithe modulaire** (un seul process, un seul
déploiement), pas une architecture microservices. En conséquence, ce
générateur **ne crée ni `main.py`, ni `container.py`, ni `Dockerfile`, ni
fichier d'exceptions** dans le module généré :

| Élément | Microservices (générateur d'origine) | Ici (monolithe modulaire) |
|---|---|---|
| `main.py` | Un par service | **Un seul, à la racine du projet** |
| `container.py` | Un par service | **Un seul, à la racine du projet** |
| Exceptions | Dupliquées dans chaque service | **Un seul fichier partagé : `common/exceptions.py`** |
| Dockerfile / port | Un par service | Un seul conteneur pour toute l'application |
| Point d'entrée du module | — | `dev_runner.py` (test/dev isolé uniquement, jamais utilisé en prod) |

## Prérequis

- Python 3.10+
- Être lancé depuis la racine du projet, ou depuis le dossier `generator/`
  (le script détecte automatiquement la racine du projet)

## Utilisation

Créer un nouveau module :
```bash
python generator/generate_module.py agent
```

Créer un module qui a besoin de ses propres routes REST (cas rare — voir
note ci-dessous) :
```bash
python generator/generate_module.py scoring --with-api
```

Créer un module sans `domain/services/` (utile si le module n'a pas de
règle métier complexe à isoler, ex: `session/`, `storage/`) :
```bash
python generator/generate_module.py storage --no-domain-services
```

## Ce qui est généré

```
<nom_du_module>/
├── __init__.py
├── README.md                        # à compléter : rôle, ports exposés/requis
├── dev_runner.py                     # point d'entrée LOCAL, pour tester le module seul
├── domain/
│   ├── __init__.py
│   ├── entities/
│   ├── value_objects/
│   └── services/                     # omis si --no-domain-services
├── application/
│   ├── __init__.py
│   ├── ports/                        # interfaces (contrats)
│   │   └── inbound/
│   └── use_cases/
├── infrastructure/
│   ├── __init__.py
│   ├── adapters/                     # implémentations concrètes (Ollama, Deepgram, Redis...)
│   └── fakes/                        # implémentations factices, pour tests et dev_runner
└── api/                              # uniquement si --with-api
    └── <nom>_router.py
```

## Note sur `--with-api`

Dans la majorité des cas, **ne pas utiliser ce flag**. Le module `api/`
racine du projet centralise les routes REST et appelle les use cases des
autres modules via le `container.py` global. N'utiliser `--with-api` que
si un module a un besoin justifié d'exposer ses propres routes de façon
autonome.

## Comportement en cas de module déjà existant

Le script ne supprime ni n'écrase jamais un fichier existant. S'il est
relancé sur un module déjà généré, il complète uniquement les fichiers
manquants (utile si la structure standard évolue) et affiche
`(ignoré, existe déjà)` pour chaque fichier déjà présent.

## Après la génération

1. Compléter le `README.md` du module (rôle, ports exposés/requis) — voir
   `docs/modules_specification.md` pour la spécification fonctionnelle
   déjà validée en équipe
2. Définir les fichiers `application/ports/*.py` (interfaces) **avant**
   d'écrire la logique métier — c'est le contrat que le reste de l'équipe
   utilisera pour développer en parallèle
3. Étendre `common/exceptions.py` si le module a besoin d'un nouveau type
   d'exception métier générique (ne pas créer d'exceptions locales)
4. Brancher les adapters réels du module dans `common/container.py`
   (composition root globale) une fois prêts

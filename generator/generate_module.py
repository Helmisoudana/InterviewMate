#!/usr/bin/env python3
"""
generate_module.py — génère le squelette d'un module en architecture
hexagonale (domain / application / infrastructure / api) pour le projet
InterviewMate.

Différence importante avec un générateur de microservices :
    - Ce projet est un MONOLITHE MODULAIRE, pas des microservices
      indépendamment déployables. Il n'y a donc :
        * qu'UN SEUL main.py et UN SEUL container.py, à la racine du
          projet — on n'en génère jamais dans le module lui-même.
        * qu'UN SEUL fichier d'exceptions partagé (common/exceptions.py),
          jamais dupliqué dans chaque module.
        * pas de Dockerfile ni de port par module (le monolithe entier
          tourne dans un seul process/conteneur).
    - Chaque module généré reçoit en revanche un dev_runner.py : un point
      d'entrée LOCAL qui permet de faire tourner/tester ce module seul,
      avec des adapters "Fake", sans dépendre du reste de l'application.
      Ce n'est PAS un point d'entrée de production.
    - Le dossier api/ d'un module est OPTIONNEL (flag --with-api) : il ne
      sert que si le module expose lui-même des routes REST propres. La
      plupart des modules (agent, asr, tts, scoring, session) n'en ont pas
      besoin — c'est le module api/ racine qui centralise les routes HTTP
      et appelle les use cases des autres modules.

Usage:
    python generator/generate_module.py agent
    python generator/generate_module.py asr
    python generator/generate_module.py scoring --with-api
    python generator/generate_module.py storage --no-domain-services
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # racine du projet (parent de generator/)

# ---------------------------------------------------------------------------
# Contenu FIXE, identique pour tous les modules
# ---------------------------------------------------------------------------

DEV_RUNNER_PY = '''"""
Point d'entrée LOCAL du module `{name}`.

Ce fichier n'est PAS un point d'entrée de production (celui-ci est unique
et se trouve à la racine du projet : main.py). Il sert uniquement à faire
tourner ou tester ce module de façon isolée, pendant le développement,
sans dépendre des autres modules ni du container.py global.

Utilise les adapters "Fake" du module (infrastructure/fakes/) plutôt que
les vrais adapters externes, pour rester rapide et indépendant.

Lancer avec :
    python -m {name}.dev_runner
"""


def main():
    # TODO: instancier ici les Fakes du module et le(s) use case(s) à tester
    # Exemple :
    #   from {name}.infrastructure.fakes.fake_adapter import Fake...Adapter
    #   from {name}.application.use_cases.... import ...UseCase
    #
    #   use_case = ...UseCase(dependency=Fake...Adapter())
    #   result = use_case.execute(...)
    #   print(result)
    print("dev_runner de '{name}' — à compléter au fil du développement du module.")


if __name__ == "__main__":
    main()
'''

MODULE_README = '''# Module `{name}`

## Rôle
<!-- TODO: décrire le rôle fonctionnel du module (voir docs/modules_specification.md) -->

## Structure

```
{name}/
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
python -m {name}.dev_runner
```

## Exceptions
Ce module utilise les exceptions communes définies dans `common/exceptions.py`.
Ne pas créer d'exceptions locales dupliquées — étendre `common/exceptions.py`
si un nouveau type d'erreur métier générique est nécessaire.
'''

ROUTER_PY = '''"""
Routes REST propres au module `{name}` (optionnel).

Ce module n'est généré que si le module a besoin d'exposer ses propres
routes HTTP directement. Dans la majorité des cas, c'est le module `api/`
racine qui centralise les routes et appelle les use cases des autres
modules — préférer cette approche sauf besoin justifié.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/{name}", tags=["{name}"])

# TODO: brancher les routes sur les use cases de application/use_cases/
# En cas d'erreur métier, lever une exception de common/exceptions.py
# (NotFoundException, ValidationException, ...) — le container.py racine
# s'occupe de les transformer en réponses HTTP.
'''


def w(path: Path, content: str = ""):
    """Crée le fichier (et ses dossiers parents) avec le contenu donné.
    Ne fait rien si le fichier existe déjà, pour ne jamais écraser du code déjà écrit."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"  (ignoré, existe déjà) {path.relative_to(ROOT)}")
        return
    path.write_text(content, encoding="utf-8")
    print(f"  créé  {path.relative_to(ROOT)}")


def generate(name: str, with_api: bool, with_domain_services: bool):
    base = ROOT / name

    if base.exists():
        print(f"⚠️  {base} existe déjà. Le générateur ne supprime rien : "
              f"les fichiers manquants seront ajoutés, les existants ignorés.")

    print(f"Génération du module '{name}' (hexagonale, monolithe modulaire)...\n")

    # --- structure hexagonale du module ------------------------------------
    dirs = [
        base / "domain" / "entities",
        base / "domain" / "value_objects",
        base / "domain" / "ports",
        base / "application" / "use_cases",
        base / "infrastructure" / "adapters",
        base / "infrastructure" / "fakes",
    ]
    if with_domain_services:
        dirs.append(base / "domain" / "services")
    if with_api:
        dirs.append(base / "api")

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        w(d / "__init__.py")

    for pkg in [base, base / "domain", base / "application", base / "infrastructure"]:
        w(pkg / "__init__.py")

    # --- dev_runner.py : point d'entrée LOCAL, pour tester le module seul ---
    w(base / "dev_runner.py", DEV_RUNNER_PY.format(name=name))

    # --- README propre au module --------------------------------------------
    w(base / "README.md", MODULE_README.format(name=name))

    # --- api/ optionnel --------------------------------------------------
    if with_api:
        w(base / "api" / f"{name}_router.py", ROUTER_PY.format(name=name))

    # --- rappel : PAS de main.py, PAS de container.py, PAS d'exceptions.py --
    # dans le module. Ces éléments sont uniques et vivent à la racine du
    # projet (main.py, container.py, common/exceptions.py).

    print(f"\n✅ Module '{name}' généré dans {base.relative_to(ROOT)}/")
    print("   Rappel : pas de main.py ni de container.py ici (uniques, à la racine).")
    print("   Rappel : utiliser common/exceptions.py, ne pas dupliquer d'exceptions locales.")


def main():
    parser = argparse.ArgumentParser(
        description="Générateur de module hexagonal pour le monolithe InterviewMate "
                     "(pas un générateur de microservices)."
    )
    parser.add_argument("name", help="nom du module (ex: agent, asr, tts, scoring, session, storage)")
    parser.add_argument(
        "--with-api", action="store_true",
        help="ajoute un dossier api/ local au module (à réserver aux cas où le module "
             "doit exposer ses propres routes REST, sinon préférer le module api/ racine)"
    )
    parser.add_argument(
        "--no-domain-services", dest="with_domain_services", action="store_false",
        help="ne pas créer domain/services/ (utile si le module n'a pas de règle métier "
             "complexe nécessitant un service de domaine séparé, ex: session/, storage/)"
    )
    parser.set_defaults(with_domain_services=True)
    args = parser.parse_args()

    generate(args.name, args.with_api, args.with_domain_services)


if __name__ == "__main__":
    main()

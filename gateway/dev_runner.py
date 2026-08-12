"""
Point d'entrée LOCAL du module `gateway`.

Ce fichier n'est PAS un point d'entrée de production (celui-ci est unique
et se trouve à la racine du projet : main.py). Il sert uniquement à faire
tourner ou tester ce module de façon isolée, pendant le développement,
sans dépendre des autres modules ni du container.py global.

Utilise les adapters "Fake" du module (infrastructure/fakes/) plutôt que
les vrais adapters externes, pour rester rapide et indépendant.

Lancer avec :
    python -m gateway.dev_runner
"""


def main():
    # TODO: instancier ici les Fakes du module et le(s) use case(s) à tester
    # Exemple :
    #   from gateway.infrastructure.fakes.fake_adapter import Fake...Adapter
    #   from gateway.application.use_cases.... import ...UseCase
    #
    #   use_case = ...UseCase(dependency=Fake...Adapter())
    #   result = use_case.execute(...)
    #   print(result)
    print("dev_runner de 'gateway' — à compléter au fil du développement du module.")


if __name__ == "__main__":
    main()

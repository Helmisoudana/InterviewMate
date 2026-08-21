"""
Point d'entrée LOCAL du module `storage`.

Ce fichier n'est PAS un point d'entrée de production (celui-ci est unique
et se trouve à la racine du projet : main.py). Il sert uniquement à faire
tourner ou tester ce module de façon isolée, pendant le développement,
sans dépendre des autres modules ni du container.py global.

Utilise les adapters "Fake" du module (infrastructure/fakes/) plutôt que
les vrais adapters externes, pour rester rapide et indépendant.

Lancer avec :
    python -m storage.dev_runner
"""
import asyncio

from shared.domain.value_objects import SessionID
from storage.infrastructure.fakes.in_memory_storage_adapter import InMemoryStorageAdapter


async def main():
    storage = InMemoryStorageAdapter()
    session_id = SessionID.generate()

    print(f"=== Test storage, session {session_id} ===\n")

    # 1. Sauvegarde d'un transcript
    transcript = {
        "user_id": "user-test-001",
        "echanges": [
            {"question": "Peux-tu expliquer la difference entre une liste et un tuple ?",
             "reponse": "Une liste est mutable, un tuple est immutable en Python."},
            {"question": "Comment gererais-tu une exception dans une API REST ?",
             "reponse": "Je ne sais pas trop, peut-etre avec un try/except."},
        ],
    }
    await storage.sauvegarder_transcript(session_id, transcript)
    print("Transcript sauvegarde.")

    # 2. Sauvegarde d'un rapport
    rapport = {
        "score_global": 0.5,
        "points_forts": ["Bonne comprehension des bases Python"],
        "points_faibles": ["Manque de precision sur la gestion d'erreurs"],
        "recommandations": ["Approfondir les patterns de gestion d'exception en API REST"],
    }
    await storage.sauvegarder_rapport(session_id, rapport)
    print("Rapport sauvegarde.\n")

    # 3. Relecture du transcript
    historique = await storage.recuperer_historique("user-test-001")
    print(f"Historique recupere ({len(historique)} entree(s)) :")
    print(historique)
    print()

    # 4. Relecture du rapport
    rapport_relu = await storage.recuperer_rapport(session_id)
    print("Rapport relu :")
    print(rapport_relu)
    print()

    # 5. Verification d'une session inexistante
    rapport_absent = await storage.recuperer_rapport(SessionID.generate())
    print(f"Rapport pour session inexistante : {rapport_absent}")

    assert historique, "ECHEC : l'historique devrait contenir le transcript"
    assert rapport_relu == rapport, "ECHEC : le rapport relu ne correspond pas a l'original"
    assert rapport_absent is None, "ECHEC : une session inexistante devrait renvoyer None"

    print("\n=== TOUS LES TESTS PASSENT ===")


if __name__ == "__main__":
    asyncio.run(main())
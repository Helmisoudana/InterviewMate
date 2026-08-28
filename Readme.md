<p align="center">
  <img src="Docs/logo.webp" width="2000" alt="Logo Interview Mate">
</p>

<h1 align="center">Interview Mate</h1>

<p align="center">
  <img src="https://img.shields.io/badge/licence-Tous%20droits%20r%C3%A9serv%C3%A9s-critical" alt="Licence">
  <img src="https://img.shields.io/badge/projet-Professionnel-blueviolet" alt="Projet pro">
  <img src="https://img.shields.io/badge/backend-Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/frontend-Angular-DD0031?logo=angular&logoColor=white" alt="Angular">
  <img src="https://img.shields.io/badge/temps%20r%C3%A9el-WebSocket-000000?logo=websocket&logoColor=white" alt="WebSocket">
  <img src="https://img.shields.io/badge/statut-En%20d%C3%A9veloppement-yellow" alt="Statut">
</p>

<p align="center">
  <em>« Le meilleur moment pour rater un entretien, c'est avant le vrai. »</em>
  <br>— Interview Mate
</p>

---

## C'est quoi Interview Mate ?

**Interview Mate** est une application de **simulation d'entretien d'embauche assistée par IA**, en conditions réelles et en temps réel : le candidat parle à voix haute, un agent IA l'écoute, lui pose des questions, rebondit sur ses réponses, ajuste la difficulté et le clôture comme le ferait un vrai recruteur.

Concrètement, le candidat :
- choisit un **poste**, une **langue** et une **durée** d'entretien,
- **parle** dans son micro, comme dans un vrai entretien,
- **entend** les questions et relances de l'agent IA en voix synthétisée,
- reçoit à la fin un **retour structuré** sur sa prestation.

Tout se passe en flux continu (audio → texte → décision → voix), sans rupture, grâce à une architecture modulaire connectée en temps réel.

## Démo

<p align="center">
  <img src="Docs/demo.webp" width="720" alt="Démo Interview Mate">
</p>

## Les modules

Chaque module est indépendant, testable isolément, et documenté dans son propre README — clique sur une carte pour l'ouvrir.

![Liste des modules](/Docs/modules.webp)

## Architecture globale

![Liste des modules](/Docs/Global.webp)


> Chaque flèche entre le Gateway et un module correspond à une liaison **in-process** via un adapter qui implémente un port — voir le [README du Gateway](gateway/README.md) pour le détail.

---

<p align="center">
  <b>Tu veux tester Interview Mate ?</b>
</p>

<p align="center">
  <a href="docs/GETTING_STARTED.md">
    <img src="https://img.shields.io/badge/Oui%2C%20je%20veux%20tester-🚀-brightgreen?style=for-the-badge" alt="Oui, tester Interview Mate">
  </a>
</p>

---

<p align="center"><sub>© Interview Mate — Tous droits réservés.</sub></p>
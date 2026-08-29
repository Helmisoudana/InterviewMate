<p align="center">
  <img src="Docs/assets/logo.webp" width="1000" alt="Logo Interview Mate">
</p>

<h1 align="center">Interview Mate</h1>

<p align="center">
  Simulation d'entretien d'embauche assistée par IA, en conditions réelles et en temps réel.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/backend-Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/frontend-Angular-DD0031?logo=angular&logoColor=white" alt="Angular">
  <img src="https://img.shields.io/badge/temps%20réel-WebSocket-000000?logo=websocket&logoColor=white" alt="WebSocket">
  <img src="https://img.shields.io/badge/architecture-Hexagonale-4a5568" alt="Architecture hexagonale">
  <img src="https://img.shields.io/badge/statut-En%20développement-yellow" alt="Statut">
  <img src="https://img.shields.io/badge/licence-Tous%20droits%20réservés-critical" alt="Licence">
</p>

---

## Sommaire

- [C'est quoi Interview Mate ?](#cest-quoi-interview-mate-)
- [Fonctionnalités](#fonctionnalités)
- [Démo](#démo)
- [Aperçu de l'interface](#aperçu-de-linterface)
- [Stack technique](#stack-technique)
- [Architecture](#architecture)
- [Les modules](#les-modules)
- [Exemple de rapport de scoring](#exemple-de-rapport-de-scoring)
- [Installation](#installation)
- [Statut du projet](#statut-du-projet)
- [Auteur](#auteur)
- [Licence](#licence)

---

## C'est quoi Interview Mate ?

**Interview Mate** est une application de simulation d'entretien d'embauche assistée par IA. Le candidat parle à voix haute, un agent IA l'écoute, lui pose des questions, rebondit sur ses réponses, ajuste la difficulté et clôture l'entretien comme le ferait un vrai recruteur.

Concrètement, le candidat :

- choisit un **poste**, une **langue** et une **durée** d'entretien,
- **parle** dans son micro, comme dans un vrai entretien,
- **entend** les questions et relances de l'agent IA en voix synthétisée,
- reçoit à la fin un **retour structuré** sur sa prestation.

Tout se passe en flux continu (audio → texte → décision → voix), sans rupture, grâce à une [architecture hexagonale](Docs/architecture-hexagonale.md) et modulaire connectée en temps réel.

## Fonctionnalités

- Entretien vocal en temps réel, sans rupture de flux
- Choix du poste, de la langue et de la durée de l'entretien
- Agent IA qui adapte ses questions et relances aux réponses du candidat
- Transcription et synthèse vocale intégrées
- Rapport de scoring structuré généré en fin d'entretien
- Historique des entretiens passés

## Démo

<p align="center">
  <img src="Docs/assets/demo.webp" width="720" alt="Démo d'un entretien simulé avec Interview Mate : candidat en visioconférence face à l'agent IA">
</p>

## Aperçu de l'interface

> Interface en cours de finalisation — les captures ci-dessous reflètent l'état actuel du développement.

<table align="center">
  <tr>
    <td align="center">
      <img src="Docs/assets/screenshot-accueil.png" width="360" alt="Page d'accueil Interview Mate : démarrer un nouvel entretien, consulter l'historique et les rapports de scoring"><br>
      <sub>Page d'accueil</sub>
    </td>
    <td align="center">
      <img src="Docs/assets/screenshot-entretien.png" width="360" alt="Écran d'entretien en cours façon visioconférence, avec contrôles caméra et micro"><br>
      <sub>Entretien en cours</sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="Docs/assets/screenshot-fin.png" width="360" alt="Écran de fin d'entretien avec options rejoindre à nouveau ou retourner à l'accueil"><br>
      <sub>Fin d'entretien</sub>
    </td>
    <td align="center">
      <img src="Docs/assets/screenshot-historique.png" width="360" alt="Écran d'historique listant les entretiens passés et leurs rapports de scoring"><br>
      <sub>Historique des entretiens</sub>
    </td>
  </tr>
</table>

## Stack technique

| Composant | Techno |
| :--- | :--- |
| Backend | Python |
| Frontend | Angular |
| Communication temps réel | WebSocket |
| Transcription (ASR) | faster-whisper |
| Agent IA | Ollama (LLM local) |
| Synthèse vocale (TTS) | Piper |
| Architecture | Hexagonale (ports & adapters), monolithe modulaire |

## Architecture Hexagonale

<p align="center">
  <img src="Docs/assets/Global.webp" alt="Schéma d'architecture globale d'Interview Mate : le Gateway route les échanges WebSocket vers les modules ASR, Agent, TTS, Scoring, Session et Storage via des ports et adapters">
</p>

Chaque flèche entre le Gateway et un module correspond à une liaison **in-process** via un adapter qui implémente un port — voir le [README du Gateway](gateway/README.md) pour le détail.

Le détail complet du pattern ports & adapters est documenté dans [`Docs/architecture-hexagonale.md`](Docs/architecture-hexagonale.md).

## Les modules

Chaque module est indépendant, testable isolément et documenté séparément :

<p align="center">
  <img src="Docs/assets/modules.webp" alt="Vue d'ensemble des sept modules d'Interview Mate : Gateway, ASR, Agent, TTS, Scoring, Session Manager, Storage">
</p>

| Module | Description | Documentation |
| :--- | :--- | :---: |
| **Gateway** | Point d'entrée WebSocket & routage | [`README`](gateway/README.md) |
| **ASR** | Transcription Audio → Texte | [`README`](asr/README.md) |
| **Agent** | Agent IA & gestion du dialogue | [`README`](agent/README.md) |
| **TTS** | Synthèse vocale Texte → Audio | [`README`](tts/README.md) |
| **Scoring** | Analyse & rapport post-entretien | [`README`](scoring/README.md) |
| **Session Manager** | Gestion des états & cycles de vie | [`README`](session/README.md) |
| **Storage** | Persistance des données & stockage | [`README`](storage/README.md) |

## Exemple de rapport de scoring

À la fin de chaque entretien, le candidat reçoit un rapport structuré généré automatiquement par le module Scoring.

<p align="center" style="display: flex; justify-content: center; gap: 20px;">
  <img src="Docs/assets/page1.jpg" width="45%" alt="Exemple de rapport de scoring généré en fin d'entretien : notes par critère, points forts, axes d'amélioration">
  <img src="Docs/assets/page2.jpg" width="45%" alt="Deuxième image exemple">
</p>

## Installation

Deux tutoriels détaillés selon ton système :

<p align="center">
  <a href="Docs/TutoWindows.md">
    <img src="https://img.shields.io/badge/Windows-0078D4?style=for-the-badge&logo=windows11&logoColor=white" alt="Tutoriel installation Windows">
  </a>
&nbsp;&nbsp;
  <a href="Docs/tutoLinux.md">
    <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Tutoriel installation Linux">
  </a>
</p>

# Statut du projet

Interview Mate est un projet **Open Source** en développement actif. Les modules backend (Gateway, ASR, Agent, TTS, Session, Storage) et le pipeline temps réel sont fonctionnels. Les contributions de la communauté sont vivement encouragées !

## Contribution

Les contributions à Interview Mate sont les bienvenues ! Que ce soit pour signaler un bug, proposer une amélioration ou ajouter une nouvelle fonctionnalité :

1. Forkez le projet
2. Créez votre branche d'action (`git checkout -b feature/SuperFonctionnalite`)
3. Commitez vos changements (`git commit -m 'Ajout d'une SuperFonctionnalite'`)
4. Pushez sur la branche (`git push origin feature/SuperFonctionnalite`)
5. Ouvrez une **Pull Request**

Voici le bloc mis à jour pour la section Auteurs & Contact, avec Helmi Soudana et Ahmed Naoui, incluant leurs icônes GitHub, LinkedIn et Email respectives.

Tu peux remplacer la section ## Auteur & Contact de ton README par ce fragment :
Markdown

## Auteurs & Contact

Projet développé avec passion par **Helmi Soudana** et **Ahmed Naoui**.

<table align="center">
  <tr>
    <td align="center" width="300">
      <b>Helmi Soudana</b><br><br>
      <a href="https://github.com/Helmisoudana" target="_blank">
        <img src="https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white&logoOnly=true" height="28" alt="GitHub Helmi" />
      </a>
      &nbsp;&nbsp;
      <a href="https://www.linkedin.com/in/helmi-soudana/" target="_blank">
        <img src="https://img.shields.io/badge/-LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white&logoOnly=true" height="28" alt="LinkedIn Helmi" />
      </a>
      &nbsp;&nbsp;
      <a href="helmi.soudana@eniso.u-sousse.tn">
        <img src="https://img.shields.io/badge/-Gmail-EA4335?style=flat-square&logo=gmail&logoColor=white&logoOnly=true" height="28" alt="Email Helmi" />
      </a>
    </td>
    <td align="center" width="300">
      <b>Ahmed Naoui</b><br><br>
      <a href="https://github.com/ahmednaoui23" target="_blank">
        <img src="https://img.shields.io/badge/-GitHub-181717?style=flat-square&logo=github&logoColor=white&logoOnly=true" height="28" alt="GitHub Ahmed" />
      </a>
      &nbsp;&nbsp;
      <a href="https://www.linkedin.com/in/ahmed-naoui-6b0a54348/" target="_blank">
        <img src="https://img.shields.io/badge/-LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white&logoOnly=true" height="28" alt="LinkedIn Ahmed" />
      </a>
      &nbsp;&nbsp;
      <a href="ahmed.soudana@eniso.u-sousse.tn">
        <img src="https://img.shields.io/badge/-Gmail-EA4335?style=flat-square&logo=gmail&logoColor=white&logoOnly=true" height="28" alt="Email Ahmed" />
      </a>
    </td>
  </tr>
</table>

## Licence

Ce projet est distribué sous la **licence MIT**. Vous êtes libre de l'utiliser, le modifier et le distribuer.

---

<p align="center">
  <em>« Le meilleur moment pour rater un entretien, c'est avant le vrai. »</em>
  <br>— Interview Mate
</p>

<p align="center"><sub>© Interview Mate — Open Source</sub></p>
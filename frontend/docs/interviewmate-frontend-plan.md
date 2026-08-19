# InterviewMate — Plan Frontend Angular

## 1. Rappel du besoin

Un frontend type **call Google Meet** qui simule un entretien avec un agent IA :
- Appel en direct (webcam/micro) avec un "interviewer" (l'agent vocal du backend)
- Contrôles identiques à Google Meet : caméra on/off, micro on/off, quitter l'appel
- Écran de fin d'entretien (façon "Vous avez quitté l'appel") avec choix : revenir / accueil
- Page d'accueil : lancer un entretien, historique des entretiens, rapport de scoring

Le backend (vu dans le PDF) expose déjà la frontière fonctionnelle :
- **API** (REST) : auth, config de session, historique, rapports
- **GATEWAY** (WebSocket) : flux audio candidat ⇄ flux audio agent, transcript, signaux (fin de tour, fin d'entretien)
- **SCORING / STORAGE** : rapport final (consommé via API, pas directement)

Le frontend n'a donc que **deux points d'entrée réseau** : l'API REST et le WebSocket du GATEWAY. Tout le reste (ASR, AGENT, TTS, SESSION) est invisible côté client.

---

## 2. Notions Angular à maîtriser avant de commencer

| Notion | Pourquoi tu en as besoin ici |
|---|---|
| **Standalone components** (pas de NgModules) | Structure moderne recommandée depuis Angular 17+, plus simple à organiser en feature-based |
| **Signals** (`signal`, `computed`, `effect`) | Gérer l'état réactif de l'appel (micro on/off, statut connexion, phase entretien) sans RxJS partout |
| **RxJS de base** (`Observable`, `Subject`, `BehaviorSubject`, `switchMap`, `takeUntil`) | Le flux WebSocket (audio, transcript, événements) est fondamentalement un flux asynchrone continu |
| **Angular Router** : lazy loading (`loadComponent`/`loadChildren`), **Guards** (`CanActivate`, `CanDeactivate`) | Lazy load par feature, et bloquer la sortie accidentelle de la page d'appel en cours |
| **Resolvers** | Précharger l'historique ou un rapport avant d'afficher la page |
| **HttpClient + Interceptors** | Appels REST vers l'API (auth token, gestion erreurs centralisée) |
| **Dependency Injection** (`inject()`, services `providedIn: 'root'`) | Services partagés : Auth, Session API, WebSocket Gateway, Media |
| **Reactive Forms** | Formulaire de configuration d'entretien (type, niveau, poste, durée) avec validation |
| **Lifecycle hooks** (`ngOnInit`, `ngOnDestroy`, `DestroyRef`/`takeUntilDestroyed`) | Nettoyer proprement les abonnements WebSocket et les streams média en quittant la page |
| **Environments** (`environment.ts`) | URLs API/WS différentes en dev/prod |
| **API navigateur (pas Angular mais indispensable)** : `MediaDevices.getUserMedia`, `MediaRecorder`, `Web Audio API`, `WebSocket` natif | Capturer/couper caméra-micro, découper l'audio en chunks, jouer l'audio streamé du TTS |

Tu n'as **pas besoin de NgRx** pour démarrer — un service à base de `signal()` fait très bien l'affaire pour ce niveau de complexité. Si le projet grossit (multi-appels, replay, etc.), tu migreras vers NgRx/NgRx-Signals plus tard.

---

## 3. Architecture des dossiers (feature-based, standalone)

```
src/app/
├── core/                        # Singleton, chargé une seule fois
│   ├── auth/
│   │   ├── auth.service.ts
│   │   ├── auth.guard.ts
│   │   └── auth.interceptor.ts
│   ├── api/
│   │   └── session-api.service.ts     # appels REST vers module API backend
│   ├── gateway/
│   │   ├── gateway-socket.service.ts  # WebSocket vers module GATEWAY
│   │   └── gateway.types.ts           # types des messages échangés
│   ├── media/
│   │   ├── media-devices.service.ts   # accès caméra/micro (getUserMedia)
│   │   └── audio-stream.service.ts    # chunking micro + lecture audio TTS
│   └── layout/
│       └── app-shell.component.ts
│
├── shared/                      # Réutilisable, pas de logique métier
│   ├── ui/
│   │   ├── call-control-button/      # bouton style Meet (icône + toggle)
│   │   ├── avatar/
│   │   ├── modal-confirm/
│   │   └── badge-status/
│   └── pipes/ , directives/
│
├── features/
│   ├── auth/
│   │   ├── login/
│   │   └── register/
│   │
│   ├── home/
│   │   └── home.component.ts          # accueil : CTA "Nouvel entretien" + aperçu historique
│   │
│   ├── interview-setup/
│   │   └── interview-setup.component.ts   # formulaire config avant démarrage
│   │
│   ├── interview-room/                # LE cœur : la salle d'appel façon Meet
│   │   ├── interview-room.component.ts
│   │   ├── interview-room.store.ts    # état signals : mic/cam on-off, phase, transcript
│   │   ├── components/
│   │   │   ├── video-tile/            # self-view caméra locale
│   │   │   ├── agent-tile/            # avatar/onde audio de l'agent (pas de vraie vidéo agent)
│   │   │   ├── control-bar/           # mic / cam / end-call
│   │   │   ├── live-transcript/       # texte partiel/final affiché en direct
│   │   │   └── phase-indicator/       # intro / technique / comportemental / clôture
│   │   └── interview-room.guard.ts    # CanDeactivate : confirmation avant de quitter
│   │
│   ├── interview-end/
│   │   └── interview-end.component.ts # écran "Entretien terminé" (façon post-Meet)
│   │
│   ├── interview-history/
│   │   └── interview-history.component.ts
│   │
│   └── interview-report/
│       └── interview-report.component.ts  # rapport détaillé (scores, points forts/faibles)
│
├── app.routes.ts
├── app.config.ts
└── environments/
    ├── environment.ts
    └── environment.prod.ts
```

**Principe clé** : `interview-room` est isolé et ne connaît que `interview-room.store.ts` + les services `core/gateway` et `core/media`. Aucun autre feature ne doit connaître le détail du protocole WebSocket — ça évite de disperser la logique temps réel partout.

---

## 4. Le store de la salle d'appel (`interview-room.store.ts`)

C'est le point qui va te faire gagner le plus de temps si tu le penses bien dès le départ. Exemple de forme (avec signals) :

```ts
export class InterviewRoomStore {
  micEnabled = signal(true);
  camEnabled = signal(true);
  connectionStatus = signal<'connecting' | 'connected' | 'reconnecting' | 'ended'>('connecting');
  phase = signal<'intro' | 'technical' | 'behavioral' | 'closing'>('intro');
  partialTranscript = signal('');
  finalTranscriptHistory = signal<TranscriptEntry[]>([]);
  agentSpeaking = signal(false);
  elapsedSeconds = signal(0);
}
```

Chaque composant de `interview-room/components/*` ne fait que **lire** ce store (via `computed`) et déclencher des actions (`toggleMic()`, `endCall()`) qui, elles, appellent le service `gateway-socket.service.ts`.

---

## 5. Mapping fonctionnalités demandées → composants

| Fonctionnalité demandée | Composant / service responsable |
|---|---|
| Simulation réelle d'un appel avec l'interviewer | `interview-room` + `agent-tile` (visualisation audio de l'agent, pas de vraie vidéo) + `gateway-socket.service` |
| Ouvrir/fermer caméra | `control-bar` → `media-devices.service.toggleCamera()` → met à jour `video-tile` |
| Ouvrir/fermer micro | `control-bar` → `media-devices.service.toggleMic()` → coupe l'envoi de chunks audio au WebSocket sans couper la connexion |
| Terminer l'appel (bouton rouge) | `control-bar` → `interview-room.store.endCall()` → ferme le WebSocket proprement → navigue vers `interview-end` |
| Contrôles identiques à Google Meet | `shared/ui/call-control-button` réutilisable, thème sombre, barre flottante en bas |
| Écran de fin façon Meet | `interview-end` avec deux CTA : "Revoir le rapport" / "Retour à l'accueil" |
| Page d'accueil : lancer un entretien | `home` → CTA vers `interview-setup` |
| Page d'accueil : historique | `home` (aperçu) + `interview-history` (liste complète) |
| Page d'accueil : scoring / rapport | `interview-history` → clic sur une session → `interview-report` |

---

## 6. Séquence technique de l'appel (ce que le frontend doit orchestrer)

1. `interview-setup` : l'utilisateur choisit type/niveau/poste/durée → `POST` API → reçoit `session_id`
2. Navigation vers `interview-room` avec `session_id`
3. `interview-room` : ouverture WebSocket vers GATEWAY, demande permission caméra/micro (`getUserMedia`)
4. Micro actif → capture audio → découpage en chunks → envoi continu au WebSocket
5. Réception en continu :
   - `transcript.partial` → mise à jour `live-transcript` (affichage temps réel)
   - `transcript.final` → ajouté à l'historique affiché
   - `audio.chunk` (voix TTS de l'agent) → lecture streamée via `audio-stream.service` + `agentSpeaking = true`
   - `phase.update` → mise à jour `phase-indicator`
   - `session.ended` → déclenche automatiquement la transition vers `interview-end`
6. Bouton "Terminer l'appel" → fermeture propre du WebSocket + arrêt des tracks média (`getTracks().forEach(t => t.stop())`) — **important pour éteindre vraiment la caméra/micro physiquement**
7. `interview-end` → propose de voir le rapport (qui peut ne pas être prêt tout de suite si SCORING travaille en asynchrone côté backend → prévoir un état "rapport en cours de génération")

---

## 7. Points d'attention spécifiques (souvent oubliés)

- **CanDeactivate guard** sur `interview-room` : empêcher de fermer l'onglet ou naviguer par erreur sans confirmation (comme Meet le fait)
- **Reconnexion WebSocket** : si le réseau tombe, afficher un état "reconnexion..." plutôt que de perdre l'appel (le GATEWAY backend est censé gérer ça côté serveur, le frontend doit juste gérer l'UI de statut)
- **Libération des devices** : toujours arrêter les `MediaStreamTrack` à la sortie de la page, sinon le voyant caméra reste allumé
- **Latence perçue** : démarrer la lecture audio TTS dès les premiers chunks reçus (streaming), ne pas attendre la fin du flux
- **État "rapport pas encore prêt"** : le SCORING backend travaille en tâche de fond, donc `interview-report` doit savoir afficher un état de chargement/polling si le rapport n'est pas encore disponible juste après la fin de l'appel

---

## 8. Roadmap suggérée (par étapes livrables)

1. **Setup projet** : Angular standalone, routing, layout de base, thème sombre façon Meet
2. **Auth + Home + Historique** (REST simple, pas de temps réel) — permet de valider vite l'architecture API
3. **Interview-setup** (formulaire réactif + validation)
4. **Interview-room en mode maquette** : UI complète (video-tile, control-bar, transcript) avec données mockées, sans WebSocket réel
5. **Intégration WebSocket réelle** avec le GATEWAY : audio capturé/envoyé, TTS reçu/joué
6. **Transcript live + indicateur de phase**
7. **Écran de fin + page rapport** (avec gestion de l'état "en cours de génération")
8. **Polish** : reconnexion, responsive, accessibilité des contrôles (clavier, aria-labels sur les boutons mic/cam)

---

## 9. Une remarque sur l'architecture backend

Le PDF précise que l'AGENT ne parle jamais de vidéo — il n'y a pas de vraie vidéo de "l'interviewer" générée par le backend. Le frontend devra donc simuler la présence de l'interviewer autrement qu'avec un flux vidéo (avatar animé, onde sonore réactive au TTS, etc.) plutôt que d'attendre un flux vidéo qui n'existera jamais côté backend.

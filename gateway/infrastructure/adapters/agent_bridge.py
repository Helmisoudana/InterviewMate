
from  domain.value_objects.session_id import SessionId
from  application.use_cases.request_voice_response import RequestVoiceResponseUseCase
from  infrastructure.adapters.session_registry import SessionRegistry


class AgentBridge:
    def __init__(self, registry: SessionRegistry, request_voice: RequestVoiceResponseUseCase) -> None:
        self._registry = registry
        self._request_voice = request_voice

    async def demander_reponse_vocale(self, session_id: SessionId, texte: str) -> None:
        connexion = self._registry.obtenir(session_id)
        if connexion is None:
            raise ValueError(f"Aucune session active pour {session_id.value}")
        await self._request_voice.executer(connexion.session, texte, broadcaster=connexion.broadcaster)
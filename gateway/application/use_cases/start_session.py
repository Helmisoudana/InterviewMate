from domain.entities.entities import GatewaySession
from domain.ports.session_client_port import SessionClientPort
from domain.ports.asr_client_port import ASRClientPort
from domain.ports.tts_client_port import TTSClientPort
from domain.exceptions.exceptions import SessionInvalideError




class StartSessionUseCase:
    def __init__(
        self,
        session_client: SessionClientPort,
        asr_client: ASRClientPort,
        tts_client: TTSClientPort,
        default_voice: str = "fr_FR-siwis-medium",
    ) -> None:
        self._session_client = session_client
        self._asr_client = asr_client
        self._tts_client = tts_client
        self._default_voice = default_voice

    async def executer(self, session: GatewaySession, language: str = "fr") -> None:
        valide = await self._session_client.valider_session(session.session_id)
        if not valide:
            session.invalider()
            raise SessionInvalideError(f"Session {session.session_id.value} invalide ou expirée")
        session.activer()
        await self._asr_client.demarrer_session(session.session_id, language)
        await self._tts_client.demarrer_session(session.session_id, self._default_voice)
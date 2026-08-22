from typing import Optional
from gateway.domain.entities.entities import GatewaySession
from gateway.domain.ports.session_client_port import SessionClientPort
from gateway.domain.ports.asr_client_port import ASRClientPort
from gateway.domain.ports.tts_client_port import TTSClientPort
from gateway.domain.ports.agent_client_port import AgentClientPort
from gateway.domain.ports.storage_client_port import StorageClientPort
from gateway.domain.exceptions.exceptions import SessionInvalideError

from agent.domain.value_objects.interview_phase import DureeEntretien, DifficultyLevel


class StartSessionUseCase:
    def __init__(
        self,
        session_client: SessionClientPort,
        asr_client: ASRClientPort,
        tts_client: TTSClientPort,
        agent_client: AgentClientPort,
        storage_client: Optional[StorageClientPort] = None,
        default_voice: str = "fr_FR-siwis-medium",
    ) -> None:
        self._session_client = session_client
        self._asr_client = asr_client
        self._tts_client = tts_client
        self._agent_client = agent_client
        self._storage_client = storage_client
        self._default_voice = default_voice

    async def executer(
        self,
        session: GatewaySession,
        language: str = "fr",
        poste: str = "Poste non spécifié",
        duree: DureeEntretien = DureeEntretien.MOYENNE,
        difficulte: DifficultyLevel = DifficultyLevel.MOYEN,
    ) -> str:
        valide = await self._session_client.valider_session(session.session_id)
        if not valide:
            session.invalider()
            raise SessionInvalideError(f"Session {session.session_id.value} invalide ou expirée")
        session.activer()

        if self._storage_client:
            await self._storage_client.demarrer_session(session.session_id , poste , language , difficulte , duree)

        await self._asr_client.demarrer_session(session.session_id , language)
        await self._tts_client.demarrer_session(session.session_id, self._default_voice)

        return await self._agent_client.demarrer_session(
            session.session_id,
            poste=poste,
            langue=language,
            duree=duree,
            difficulte=difficulte,
        )
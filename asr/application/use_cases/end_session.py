from asr.domain.entities.asr_session import ASRSession


class EndASRSessionUseCase:
    def executer(self, session: ASRSession) -> None:
        session.reinitialiser_buffer()
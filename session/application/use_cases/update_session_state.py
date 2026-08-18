from domain.entities.interview_session import InterviewSession
from domain.value_objects.phase import Phase


class UpdateSessionStateUseCase:
    def executer(self, session: InterviewSession, question: str, reponse: str, nouvelle_phase: Phase | None = None) -> None:
        session.ajouter_echange(question, reponse)
        if nouvelle_phase is not None:
            session.changer_phase(nouvelle_phase)
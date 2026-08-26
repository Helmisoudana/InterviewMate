from dataclasses import asdict
from scoring.domain.entities.rapport_score import RapportScore
from scoring.domain.ports.llm_scorer_port import LLMScorerPort
from storage.application.use_cases.get_session_transcript import GetSessionTranscriptUseCase
from storage.application.use_cases.save_final_report import SaveFinalReportUseCase
from storage.domain.entities.rapport import RapportScorePersiste
from storage.application.use_cases.update_status import UpdateStatusUseCase

class GenererRapportSessionUseCase:

    def __init__(
        self,
        llm_scorer: LLMScorerPort,
        get_transcript_uc: GetSessionTranscriptUseCase,
        save_report_uc: SaveFinalReportUseCase,
        update_status_uc: UpdateStatusUseCase
    ):
        self._llm_scorer = llm_scorer
        self._get_transcript_uc = get_transcript_uc
        self._save_report_uc = save_report_uc
        self._update_status_uc = update_status_uc

    async def executer(self, session_id: str) -> RapportScorePersiste:
        echanges_persistes = await self._get_transcript_uc.executer(session_id)
        
        if not echanges_persistes:
            rapport_a_persister = RapportScorePersiste(
                session_id=session_id,
                score_global=0.0,
                points_forts=[],
                points_faibles=[],
                recommandations=[],
                evaluations=[],
                score_technique=0.0,
                score_communication=0.0,
            )
            await self._save_report_uc.executer(rapport_a_persister)
            
            statut_score = f"{int(rapport_a_persister.score_global)}/10"
            await self._update_status_uc.executer(session_id, statut_score)
            
            return rapport_a_persister
            
        echanges_bruts = [
            {
                "ordre": e.ordre,
                "question_agent": e.question_agent,
                "reponse_candidat": e.reponse_candidat,
                "qualite_percue": e.qualite_percue,
            }
            for e in echanges_persistes
        ]

        rapport: RapportScore = await self._llm_scorer.generer_rapport(session_id, echanges_bruts)

        rapport_a_persister = RapportScorePersiste(
            session_id=session_id,
            score_global=rapport.score_global,
            points_forts=rapport.points_forts,
            points_faibles=rapport.points_faibles,
            recommandations=rapport.recommandations,
            evaluations=[asdict(ev) for ev in rapport.evaluations],
            score_technique=rapport.score_technique,
            score_communication=rapport.score_communication,
        )
        
        await self._save_report_uc.executer(rapport_a_persister)
        
        statut_score = f"{int(rapport_a_persister.score_global)}/10"
        await self._update_status_uc.executer(session_id, statut_score)
        
        return rapport_a_persister
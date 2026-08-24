from dataclasses import asdict
from scoring.domain.entities.rapport_score import RapportScore, EvaluationEchange
from scoring.domain.ports.llm_scorer_port import LLMScorerPort
from storage.application.use_cases.get_session_transcript import GetSessionTranscriptUseCase
from storage.application.use_cases.get_report import GetReportUseCase
from storage.application.use_cases.save_final_report import SaveFinalReportUseCase
from storage.domain.entities.rapport import RapportScorePersiste
from storage.application.use_cases.update_status import UpdateStatusUseCase

class GenererRapportSessionUseCase:
   

    def __init__(
        self,
        llm_scorer: LLMScorerPort,
        get_transcript_uc: GetSessionTranscriptUseCase,
        get_report_uc: GetReportUseCase,
        save_report_uc: SaveFinalReportUseCase,
        update_status_uc : UpdateStatusUseCase
    ):
        self._llm_scorer = llm_scorer
        self._get_transcript_uc = get_transcript_uc
        self._get_report_uc = get_report_uc
        self._save_report_uc = save_report_uc
        self._update_status_uc = update_status_uc

    async def executer(self, session_id: str) -> RapportScore:
        rapport_existant = await self._get_report_uc.executer(session_id)
        if rapport_existant is not None:
            return self._vers_domaine(rapport_existant)

        echanges_persistes = await self._get_transcript_uc.executer(session_id)
        if not echanges_persistes:
            raise ValueError(f"Aucun echange trouve pour la session {session_id}, impossible de generer un rapport.")

        echanges_bruts = [
            {
                "ordre": e.ordre,
                "question_agent": e.question_agent,
                "reponse_candidat": e.reponse_candidat,
                "qualite_percue": e.qualite_percue,
            }
            for e in echanges_persistes
        ]

        rapport = await self._llm_scorer.generer_rapport(session_id, echanges_bruts)

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
        await self._update_status_uc.executer(session_id  , rapport.score_global)
        return rapport

    @staticmethod
    def _vers_domaine(rapport_persiste: RapportScorePersiste) -> RapportScore:
        evaluations = [
            EvaluationEchange(
                ordre=ev.get("ordre", 0),
                question=ev.get("question", ""),
                reponse=ev.get("reponse", ""),
                qualite_percue=ev.get("qualite_percue", ""),
                score_technique=ev.get("score_technique", 0.0),
                remarque=ev.get("remarque", ""),
            )
            for ev in rapport_persiste.evaluations
        ]
        return RapportScore(
            session_id=rapport_persiste.session_id,
            score_global=rapport_persiste.score_global,
            score_technique=rapport_persiste.score_technique,
            score_communication=rapport_persiste.score_communication,
            points_forts=rapport_persiste.points_forts,
            points_faibles=rapport_persiste.points_faibles,
            recommandations=rapport_persiste.recommandations,
            evaluations=evaluations,
        )
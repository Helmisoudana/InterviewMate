from scoring.domain.entities.rapport_score import RapportScore, EvaluationEchange
from scoring.domain.ports.generer_pdf import GenererPDF
from storage.application.use_cases.get_report import GetReportUseCase
from storage.domain.entities.rapport import RapportScorePersiste



class GenererPDF :

    def __init__( 
            self, 
            get_report_uc : GetReportUseCase
    ):
        self._get_report_uc = get_report_uc

    async def executer(self, session_id : str):
            rapport_existant = await self._get_report_uc.executer(session_id)
            if rapport_existant is not None:
                        return self._vers_domaine(rapport_existant)

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



        
        



        
        
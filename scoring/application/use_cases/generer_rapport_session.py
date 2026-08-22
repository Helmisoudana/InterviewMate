from scoring.domain.ports.scoring_llm_port import ScoringLLMPort
from scoring.domain.entities.rapport_score import RapportScore, EvaluationDetail
from storage.domain.entities.rapport import RapportScorePersiste
from storage.domain.ports.storage_repository_port import StorageRepositoryPort


class GenererRapportSessionUseCase:
    def __init__(self, storage_repo: StorageRepositoryPort, llm_adapter: ScoringLLMPort):
        self._storage_repo = storage_repo
        self._llm = llm_adapter

    async def executer(self, session_id: str) -> RapportScore:
        # 1. Récupération des échanges de la session depuis Postgres
        echanges = await self._storage_repo.recuperer_echanges_par_session(session_id)

        if not echanges:
            texte_discussion = "Aucun échange enregistré pour cet entretien."
        else:
            echanges_tries = sorted(echanges, key=lambda x: getattr(x, "ordre", 0))
            texte_discussion = "\n".join([
                f"Agent: {e.question_agent}\nCandidat: {e.reponse_candidat}"
                for e in echanges_tries
            ])

        # 2. Analyse via LLM (Groq)
        res = await self._llm.evaluer_transcription(texte_discussion)

        # 3. Préparation et sauvegarde dans Postgres via le StorageRepository
        score_global = float(res.get("score_global", 0.0))
        score_tech = float(res.get("score_technique", 0.0))
        score_comm = float(res.get("score_communication", 0.0))
        pts_forts = str(res.get("points_forts", ""))
        pts_faibles = str(res.get("points_faibles", ""))
        recomms = str(res.get("recommandations", ""))

        rapport_persiste = RapportScorePersiste(
            session_id=session_id,
            score_global=score_global,
            score_technique=score_tech,
            score_communication=score_comm,
            points_forts=pts_forts,
            points_faibles=pts_faibles,
            recommandations=recomms,
        )
        await self._storage_repo.sauvegarder_rapport(rapport_persiste)

        # 4. Construction des détails d'évaluation pour le log / Gateway
        details_evaluations = [
            EvaluationDetail(critere="Technique", note=score_tech, commentaire=pts_forts),
            EvaluationDetail(critere="Communication", note=score_comm, commentaire=pts_faibles),
        ]

        # 5. Retour de l'entité du Domaine Scoring attendue par InProcessScoringClient
        return RapportScore(
            session_id=session_id,
            score_global=score_global,
            score_technique=score_tech,
            score_communication=score_comm,
            points_forts=pts_forts,
            points_faibles=pts_faibles,
            recommandations=recomms,
            evaluations=details_evaluations,
        )
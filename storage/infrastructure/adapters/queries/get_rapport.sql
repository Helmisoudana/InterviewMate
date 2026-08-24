SELECT r.id, r.entretien_id, r.score_global, r.score_technique, r.score_communication,
       r.points_forts, r.points_faibles, r.recommandations, r.evaluations, r.date_creation
FROM rapports_scoring r
JOIN entretiens ent ON ent.id = r.entretien_id
WHERE ent.session_id = $1::text
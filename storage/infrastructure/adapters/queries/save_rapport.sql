INSERT INTO rapports_scoring (
    entretien_id, score_global, score_technique, score_communication,
    points_forts, points_faibles, recommandations
)
SELECT id, $2, $3, $4, $5, $6, $7
FROM entretiens
WHERE session_id = $1::text
RETURNING id, entretien_id, score_global, score_technique, score_communication,
          points_forts, points_faibles, recommandations, date_creation

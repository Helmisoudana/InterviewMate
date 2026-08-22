WITH next_ordre AS (
    SELECT COALESCE(MAX(e.ordre), 0) + 1 AS num
    FROM echanges e
    JOIN entretiens ent ON ent.id = e.entretien_id
    WHERE ent.session_id = $1::text
)
INSERT INTO echanges (entretien_id, ordre, question_agent, reponse_candidat, qualite_percue)
SELECT ent.id, next_ordre.num, $2, $3, $4
FROM entretiens ent, next_ordre
WHERE ent.session_id = $1::text
RETURNING id, entretien_id, ordre, horodatage
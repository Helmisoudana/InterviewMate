WITH inserted_entretien AS (
    INSERT INTO entretiens (session_id, statut)
    SELECT $1::text, 'EN_COURS'
    WHERE NOT EXISTS (SELECT 1 FROM entretiens WHERE session_id = $1::text)
    RETURNING id
),
target_entretien AS (
    SELECT id FROM inserted_entretien
    UNION ALL
    SELECT id FROM entretiens WHERE session_id = $1::text
    LIMIT 1
),
next_ordre AS (
    SELECT COALESCE(MAX(ordre), 0) + 1 AS num
    FROM echanges
    WHERE entretien_id = (SELECT id FROM target_entretien)
)
INSERT INTO echanges (entretien_id, ordre, question_agent, reponse_candidat, qualite_percue)
VALUES (
    (SELECT id FROM target_entretien),
    (SELECT num FROM next_ordre),
    $2, $3, $4
)
RETURNING id, entretien_id, ordre, horodatage
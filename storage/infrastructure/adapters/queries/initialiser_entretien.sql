INSERT INTO entretiens (session_id, statut)
VALUES ($1::text, 'EN_COURS')
ON CONFLICT (session_id) DO NOTHING
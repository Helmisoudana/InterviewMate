INSERT INTO entretiens (session_id,
 poste, langue, 
 difficulte,
  timestamp)
VALUES ($1::text, $2::text, $3::text, $4::text, $5::timestamp)
ON CONFLICT (session_id) DO NOTHING;
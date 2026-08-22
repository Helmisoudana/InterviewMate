UPDATE entretiens 
SET statut = $2 
WHERE session_id = $1;
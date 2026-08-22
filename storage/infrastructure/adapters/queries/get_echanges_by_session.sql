SELECT e.id, e.entretien_id, e.ordre, e.question_agent, e.reponse_candidat, e.qualite_percue, e.horodatage
FROM echanges e
JOIN entretiens ent ON ent.id = e.entretien_id
WHERE ent.session_id = $1::text
ORDER BY e.ordre ASC

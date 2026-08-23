SELECT * 
FROM entretiens 
ORDER BY timestamp DESC 
LIMIT $1;
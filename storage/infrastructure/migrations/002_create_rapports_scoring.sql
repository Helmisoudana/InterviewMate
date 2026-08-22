-- Table du rapport final de scoring, une ligne unique par entretien.
-- Créée en plus de 'entretiens' et 'echanges' (déjà existantes).
CREATE TABLE IF NOT EXISTS rapports_scoring (
    id SERIAL PRIMARY KEY,
    entretien_id UUID UNIQUE REFERENCES entretiens(id) ON DELETE CASCADE,
    score_global NUMERIC(4, 2) NOT NULL,
    score_technique NUMERIC(4, 2),
    score_communication NUMERIC(4, 2),
    points_forts TEXT[],
    points_faibles TEXT[],
    recommandations TEXT[],
    date_creation TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

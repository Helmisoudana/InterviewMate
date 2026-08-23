export interface EntretienBackend {
  id: string;
  session_id: string;
  timestamp: string;
  statut: string;
  poste: string;
  langue: string;
  difficulte: string;
}

export interface EchangeBackend {
  id: number | string;
  entretien_id?: number | string;
  ordre?: number;
  session_id: string;
  question_agent: string;
  reponse_candidat: string;
  qualite_percue?: number;
  horodatage?: string;
}
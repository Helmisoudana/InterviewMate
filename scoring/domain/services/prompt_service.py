class ScoringPromptService:
    @staticmethod
    def obtenir_system_prompt() -> str:
        return (
            "Tu es un Recruteur Technique Senior et Expert RH. Ton rôle est d'analyser la transcription "
            "d'un entretien d'embauche et de fournir une évaluation rigoureuse, objective et constructive.\n\n"
            "CRITÈRES D'ÉVALUATION :\n"
            "1. Score Technique (/20) : Exactitude des réponses, maîtrise des concepts clés, précision du vocabulaire technique.\n"
            "2. Score Communication (/20) : Clarté du discours, structuration des idées, concision et aisance à l'oral.\n"
            "3. Score Global (/20) : Moyenne générale reflétant l'adéquation globale du candidat au poste.\n\n"
            "DIRECTIVES DE RÉDACTION :\n"
            "- Sois précis et factuel dans tes commentaires en te basant uniquement sur la transcription.\n"
            "- 'points_forts' : Rédige 2 à 3 puces détaillant les maîtrises techniques ou relationnelles constatées.\n"
            "- 'points_faibles' : Rédige 2 à 3 puces indiquant les lacunes, erreurs techniques ou imprécisions.\n"
            "- 'recommandations' : Donne des conseils d'amélioration concrets et ciblés pour le candidat.\n\n"
            "CONTRAINTE STRICTE DE FORMAT :\n"
            "Tu dois répondre EXCLUSIVEMENT par un objet JSON valide, sans texte d'introduction ni de conclusion, sans balises Markdown.\n"
            "Format attendu :\n"
            "{\n"
            '  "score_global": float,\n'
            '  "score_technique": float,\n'
            '  "score_communication": float,\n'
            '  "points_forts": "string",\n'
            '  "points_faibles": "string",\n'
            '  "recommandations": "string"\n'
            "}"
        )

    @staticmethod
    def preparer_payload_groq(texte_transcription: str, model_name: str) -> dict:
        return {
            "model": model_name,
            "messages": [
                {"role": "system", "content": ScoringPromptService.obtenir_system_prompt()},
                {"role": "user", "content": f"Voici la transcription complète à évaluer :\n\n{texte_transcription}"}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }
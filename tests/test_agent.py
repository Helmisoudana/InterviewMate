import json
import pytest
from agent.domain.entities.interview import Interview
from agent.domain.entities.question import Question
from agent.domain.entities.echange import Echange
from agent.domain.value_objects.interview_phase import InterviewPhase, DifficultyLevel
from agent.domain.value_objects.message import Message
from agent.application.use_cases.conduire_entretien import ConduireEntretienUseCase
from agent.domain.ports.llm_port import LLMPort
from agent.domain.ports.session_repository_port import SessionRepositoryPort
from agent.domain.ports.scoring_notifier_port import ScoringNotifierPort
from agent.infrastructure.adapters.gateway_engine_adapter import AgentGatewayEngineAdapter
from agent.infrastructure.adapters.session_registry import AgentSessionRegistry


@pytest.mark.asyncio
async def test_gateway_adapter_cycle_de_vie_complet():
    adapter = AgentGatewayEngineAdapter(
        registry=AgentSessionRegistry(),
        llm=FakeLLM([{"qualite": "correcte", "comportement_inapproprie": False, "question": "Premiere question"}]),
        session_repo=FakeSessionRepo(),
        scoring_notifier=FakeScoringNotifier(),
    )

    await adapter.demarrer_session("session-gw-1")
    question, termine = await adapter.traiter_reponse("session-gw-1", "Bonjour")

    assert question == "Premiere question"
    assert termine is False

    await adapter.terminer_session("session-gw-1")


@pytest.mark.asyncio
async def test_gateway_adapter_refuse_session_inconnue():
    adapter = AgentGatewayEngineAdapter(
        registry=AgentSessionRegistry(),
        llm=FakeLLM([{"qualite": "correcte", "comportement_inapproprie": False, "question": "Question"}]),
        session_repo=FakeSessionRepo(),
        scoring_notifier=FakeScoringNotifier(),
    )

    with pytest.raises(ValueError):
        await adapter.traiter_reponse("session-jamais-demarree", "Bonjour")

class FakeLLM(LLMPort):
    def __init__(self, reponses: list[dict]):
        self._reponses = reponses
        self._index = 0

    async def stream_completion(self, messages: list[Message]):
        resultat = self._reponses[self._index % len(self._reponses)]
        self._index += 1
        yield json.dumps(resultat)


class FakeSessionRepo(SessionRepositoryPort):
    def __init__(self):
        self._store = {}

    async def get(self, session_id):
        return self._store.get(session_id, Interview())

    async def save(self, session_id, interview):
        self._store[session_id] = interview


class FakeScoringNotifier(ScoringNotifierPort):
    async def notifier_echange_termine(self, session_id, echange):
        pass


def test_interview_anti_repetition():
    interview = Interview()
    assert interview.peut_poser_question("Question A") is True
    interview.echanges.append(Echange(question=Question(texte="Question A", phase=InterviewPhase.INTRO)))
    assert interview.peut_poser_question("Question A") is False


def test_ajuster_difficulte_baisse_si_vague():
    interview = Interview(difficulte_actuelle=DifficultyLevel.MOYEN)
    interview.ajuster_difficulte("vague")
    assert interview.difficulte_actuelle == DifficultyLevel.FACILE


def test_ajuster_difficulte_monte_si_excellente():
    interview = Interview(difficulte_actuelle=DifficultyLevel.MOYEN)
    interview.ajuster_difficulte("excellente")
    assert interview.difficulte_actuelle == DifficultyLevel.DIFFICILE


def test_arret_anticipe_apres_deux_refus():
    interview = Interview()
    assert interview.doit_arreter_anticipativement() is False
    interview.signaler_refus()
    assert interview.doit_arreter_anticipativement() is False
    interview.signaler_refus()
    assert interview.doit_arreter_anticipativement() is True


def test_refus_reinitialise_si_reponse_normale():
    interview = Interview()
    interview.signaler_refus()
    interview.reinitialiser_refus()
    assert interview.nb_refus_consecutifs == 0


@pytest.mark.asyncio
async def test_premiere_question_generee():
    use_case = ConduireEntretienUseCase(
        llm=FakeLLM([{"qualite": "correcte", "comportement_inapproprie": False, "question": "Question de test unique"}]),
        session_repo=FakeSessionRepo(),
        scoring_notifier=FakeScoringNotifier(),
    )
    question, termine = await use_case.traiter_reponse_candidat("session-1", "Bonjour")
    assert question == "Question de test unique"
    assert termine is False


@pytest.mark.asyncio
async def test_difficulte_ajustee_apres_reponse_vague():
    use_case = ConduireEntretienUseCase(
        llm=FakeLLM([
            {"qualite": "correcte", "comportement_inapproprie": False, "question": "Question 1"},
            {"qualite": "vague", "comportement_inapproprie": False, "question": "Question 2"},
        ]),
        session_repo=FakeSessionRepo(),
        scoring_notifier=FakeScoringNotifier(),
    )
    await use_case.traiter_reponse_candidat("session-2", "Bonjour")
    await use_case.traiter_reponse_candidat("session-2", "je ne sais pas")

    interview = await use_case.session_repo.get("session-2")
    assert interview.difficulte_actuelle == DifficultyLevel.FACILE


@pytest.mark.asyncio
async def test_arret_apres_deux_comportements_inappropries():
    use_case = ConduireEntretienUseCase(
        llm=FakeLLM([
            {"qualite": "vague", "comportement_inapproprie": True, "question": "Reponse 1"},
            {"qualite": "vague", "comportement_inapproprie": True, "question": "Reponse 2"},
        ]),
        session_repo=FakeSessionRepo(),
        scoring_notifier=FakeScoringNotifier(),
    )
    await use_case.traiter_reponse_candidat("session-3", "propos deplaces")
    _, termine = await use_case.traiter_reponse_candidat("session-3", "encore des propos deplaces")

    assert termine is True
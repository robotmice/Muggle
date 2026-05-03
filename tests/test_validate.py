import unittest
from unittest.mock import MagicMock

from langgraph.constants import END

from muggle.core.guard import IntentCheckNode
from muggle.core.state import WorkflowState, ValidationRouter
from muggle.core.validation import ValidationNode, ValidationResult
from muggle.infra.registry import PromptRegistry
from muggle.shared.constants import STR_NODE_SUMMARIZATION, STR_NODE_FALLBACK


class TestValidationNode(unittest.TestCase):
    def setUp(self):
        self.mock_model = MagicMock()
        self.mock_prompt_registry = MagicMock(spec=PromptRegistry)
        self.mock_prompt_registry.get_system_prompt.return_value = "Validate this."

        self.mock_structured_model = MagicMock()
        self.mock_model.with_structured_output.return_value = self.mock_structured_model

        self.node = ValidationNode(self.mock_model, self.mock_prompt_registry, threshold=0.8)
        self.state = WorkflowState()

    def test_validation_pass(self):
        self.mock_structured_model.invoke.return_value = ValidationResult(
            pass_validation=True, score=0.9, critical_flaws=[]
        )
        result = self.node(self.state, config={})
        self.assertTrue(result["pass_validation"])
        self.assertEqual(result["attempt_count"], 0)

    def test_validation_fail_increments_attempt_count(self):
        self.state.attempt_count = 2
        self.mock_structured_model.invoke.return_value = ValidationResult(
            pass_validation=False, score=0.3, critical_flaws=["Missing disclaimer"]
        )
        result = self.node(self.state, config={})
        self.assertFalse(result["pass_validation"])
        self.assertEqual(result["attempt_count"], 3)

    def test_validation_fail_from_zero(self):
        self.mock_structured_model.invoke.return_value = ValidationResult(
            pass_validation=False, score=0.3, critical_flaws=["Inaccurate deduction"]
        )
        result = self.node(self.state, config={})
        self.assertFalse(result["pass_validation"])
        self.assertEqual(result["attempt_count"], 1)


class TestValidationRouter(unittest.TestCase):
    def setUp(self):
        self.router = ValidationRouter(max_attempts=5)

    def test_router_pass_goes_to_end(self):
        state = WorkflowState(pass_validation=True)
        self.assertEqual(self.router(state), END)

    def test_router_pass_even_with_high_attempts(self):
        state = WorkflowState(pass_validation=True, attempt_count=10)
        self.assertEqual(self.router(state), END)

    def test_router_fail_under_limit_goes_to_summarization(self):
        state = WorkflowState(pass_validation=False, attempt_count=3)
        self.assertEqual(self.router(state), STR_NODE_SUMMARIZATION)

    def test_router_fail_zero_attempts_goes_to_summarization(self):
        state = WorkflowState(pass_validation=False, attempt_count=0)
        self.assertEqual(self.router(state), STR_NODE_SUMMARIZATION)

    def test_router_fail_at_limit_goes_to_fallback(self):
        state = WorkflowState(pass_validation=False, attempt_count=5)
        self.assertEqual(self.router(state), STR_NODE_FALLBACK)

    def test_router_fail_above_limit_goes_to_fallback(self):
        state = WorkflowState(pass_validation=False, attempt_count=7)
        self.assertEqual(self.router(state), STR_NODE_FALLBACK)

    def test_router_respects_configured_max(self):
        router = ValidationRouter(max_attempts=3)
        state = WorkflowState(pass_validation=False, attempt_count=3)
        self.assertEqual(router(state), STR_NODE_FALLBACK)


class TestIntentCheckCounterReset(unittest.TestCase):
    def test_intent_check_resets_attempt_count(self):
        mock_model = MagicMock()
        mock_prompt_registry = MagicMock(spec=PromptRegistry)
        mock_prompt_registry.get_system_prompt.return_value = "Check intent."

        mock_structured = MagicMock()
        mock_model.with_structured_output.return_value = mock_structured

        from muggle.core.guard.intent_check import IntentCheckResult
        mock_structured.invoke.return_value = IntentCheckResult(pass_intent_check=True)

        node = IntentCheckNode(mock_model, mock_prompt_registry)
        state = WorkflowState(attempt_count=5)

        result = node(state, config={})
        self.assertEqual(result["attempt_count"], 0)
        self.assertTrue(result["pass_intent_check"])

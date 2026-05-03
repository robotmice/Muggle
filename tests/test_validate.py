import unittest
from unittest.mock import MagicMock

from langgraph.constants import END

from muggle.core.guard import IntentCheckNode
from muggle.core.state import WorkflowState, validation_router
from muggle.core.validate import ValidateNode, ValidationResult
from muggle.infra.registry import PromptRegistry
from muggle.shared.constants import STR_NODE_SUMMARIZE, STR_NODE_UNHANDLED


class TestValidateNode(unittest.TestCase):
    def setUp(self):
        self.mock_model = MagicMock()
        self.mock_prompt_registry = MagicMock(spec=PromptRegistry)
        self.mock_prompt_registry.get_system_prompt.return_value = "Validate this."

        self.mock_structured_model = MagicMock()
        self.mock_model.with_structured_output.return_value = self.mock_structured_model

        self.node = ValidateNode(self.mock_model, self.mock_prompt_registry, threshold=0.8)
        self.state = WorkflowState()

    def test_validation_pass(self):
        self.mock_structured_model.invoke.return_value = ValidationResult(
            pass_validation=True, score=0.9, critical_flaws=[]
        )
        result = self.node(self.state, config={})
        self.assertTrue(result["pass_validation"])
        self.assertEqual(result["retry_count"], 0)

    def test_validation_fail_increments_retry_count(self):
        self.state.retry_count = 2
        self.mock_structured_model.invoke.return_value = ValidationResult(
            pass_validation=False, score=0.3, critical_flaws=["Missing disclaimer"]
        )
        result = self.node(self.state, config={})
        self.assertFalse(result["pass_validation"])
        self.assertEqual(result["retry_count"], 3)

    def test_validation_fail_from_zero(self):
        self.mock_structured_model.invoke.return_value = ValidationResult(
            pass_validation=False, score=0.3, critical_flaws=["Inaccurate deduction"]
        )
        result = self.node(self.state, config={})
        self.assertFalse(result["pass_validation"])
        self.assertEqual(result["retry_count"], 1)


class TestValidationRouter(unittest.TestCase):
    def test_router_pass_goes_to_end(self):
        state = WorkflowState(pass_validation=True)
        self.assertEqual(validation_router(state), END)

    def test_router_pass_even_with_high_retry(self):
        state = WorkflowState(pass_validation=True, retry_count=10)
        self.assertEqual(validation_router(state), END)

    def test_router_fail_under_limit_goes_to_summarize(self):
        state = WorkflowState(pass_validation=False, retry_count=3)
        self.assertEqual(validation_router(state), STR_NODE_SUMMARIZE)

    def test_router_fail_zero_retries_goes_to_summarize(self):
        state = WorkflowState(pass_validation=False, retry_count=0)
        self.assertEqual(validation_router(state), STR_NODE_SUMMARIZE)

    def test_router_fail_at_limit_goes_to_unhandled(self):
        state = WorkflowState(pass_validation=False, retry_count=5)
        self.assertEqual(validation_router(state), STR_NODE_UNHANDLED)

    def test_router_fail_above_limit_goes_to_unhandled(self):
        state = WorkflowState(pass_validation=False, retry_count=7)
        self.assertEqual(validation_router(state), STR_NODE_UNHANDLED)


class TestIntentCheckCounterReset(unittest.TestCase):
    def test_intent_check_resets_retry_count(self):
        mock_model = MagicMock()
        mock_prompt_registry = MagicMock(spec=PromptRegistry)
        mock_prompt_registry.get_system_prompt.return_value = "Check intent."

        mock_structured = MagicMock()
        mock_model.with_structured_output.return_value = mock_structured

        from muggle.core.guard.intent_check import IntentCheckResult
        mock_structured.invoke.return_value = IntentCheckResult(pass_intent_check=True)

        node = IntentCheckNode(mock_model, mock_prompt_registry)
        state = WorkflowState(retry_count=5)

        result = node(state, config={})
        self.assertEqual(result["retry_count"], 0)
        self.assertTrue(result["pass_intent_check"])

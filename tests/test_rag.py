import unittest
from unittest.mock import MagicMock, patch
from langchain_core.messages import AIMessage, HumanMessage
from muggle.core.graph_processor import GraphProcessor, WorkflowState
from muggle.infra.registry import ModelRegistry, PromptRegistry, VectorStoreManager
from muggle.shared.constants import STR_LLM_DEFAULT

class TestRAGFlow(unittest.TestCase):
    @patch('muggle.infra.registry.model.init_chat_model')
    @patch('muggle.core.graph_processor.create_agent')
    def test_full_rag_pipeline(self, mock_create_agent, mock_init_model):
        # 1. Setup Mock Registries
        model_registry = ModelRegistry()
        model_registry.register(STR_LLM_DEFAULT, provider="test", model_id="test", temperature=0)
        
        prompt_registry = MagicMock(spec=PromptRegistry)
        prompt_registry.get_system_prompt.side_effect = lambda name, variables=None: f"Prompt for {name} with context {variables.get('context') if variables else None}"
        
        vector_store = MagicMock(spec=VectorStoreManager)
        vector_store.search.return_value = [{"header": "Test Header", "text": "Test Content"}]
        
        # 2. Setup Mock Agent Instances for different nodes
        mock_agent_instance = MagicMock()
        mock_create_agent.return_value = mock_agent_instance
        
        # Sequence of LLM responses: Intent Check -> Query Rewrite -> Inquiry
        mock_agent_instance.invoke.side_effect = [
            # 1. Intent Check
            {"structured_response": {"pass_intent_check": True}, "messages": []},
            # 2. Query Rewrite
            {"structured_response": {"vector_store_query": "rewritten query"}, "messages": []},
            # 3. Inquiry
            {"structured_response": {"response": "Final grounded answer"}, "messages": [AIMessage(content="Final grounded answer")]}
        ]
        
        # 3. Initialize Processor
        processor = GraphProcessor(registry=model_registry, prompt_registry=prompt_registry, vector_store=vector_store)
        processor.warm_up()
        
        # 4. Execute
        response = processor.get_response("Hello, tell me more about insurance", thread_id="rag_test")
        
        # 5. Assertions
        self.assertEqual(response, "Final grounded answer")
        
        # Verify Vector Store was called with rewritten query
        vector_store.search.assert_called_once_with(query_text="rewritten query")
        
        # Verify Inquiry prompt was rendered with context
        inquiry_call = prompt_registry.get_system_prompt.call_args_list[-1]
        self.assertIn("Test Header", inquiry_call[1]["variables"]["context"])
        self.assertIn("Test Content", inquiry_call[1]["variables"]["context"])

if __name__ == '__main__':
    unittest.main()

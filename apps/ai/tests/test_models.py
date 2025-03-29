from django.test import TestCase

from apps.ai.models.prompt_template import PromptTemplate
from apps.ai.models.ai_completion import AICompletion
from apps.ai.models.agent import Agent


class PromptTemplateModelTest(TestCase):
    """
    Test case for the PromptTemplate model.
    """

    def test_prompt_template_creation(self):
        """Test creating a new prompt template."""
        template = PromptTemplate.objects.create(
            name="Test Template",
            template_text="Hello, {{name}}! How can I help you today?",
            description="A test prompt template",
            version="1.0",
        )
        self.assertEqual(template.name, "Test Template")
        self.assertEqual(
            template.template_text, "Hello, {{name}}! How can I help you today?"
        )
        self.assertTrue(hasattr(template, 'created_at'))
        self.assertTrue(hasattr(template, 'modified_at'))


class AICompletionModelTest(TestCase):
    """
    Test case for the AICompletion model.
    """

    def test_ai_completion_creation(self):
        """Test creating a new AI completion."""
        template = PromptTemplate.objects.create(
            name="Test Template",
            template_text="Hello, {{name}}! How can I help you today?",
        )

        completion = AICompletion.objects.create(
            prompt_template=template,
            prompt_input="Hello, AI!",
            prompt_variables={"name": "User"},
            completion_text="Hello, User! How can I help you today?",
            provider="openai",
            model="gpt-4",
            usage_tokens=50,
        )

        self.assertEqual(completion.prompt_input, "Hello, AI!")
        self.assertEqual(
            completion.completion_text, "Hello, User! How can I help you today?"
        )
        self.assertEqual(completion.provider, "openai")
        self.assertEqual(completion.model, "gpt-4")
        self.assertEqual(completion.usage_tokens, 50)
        self.assertTrue(hasattr(completion, 'created_at'))


class AgentModelTest(TestCase):
    """
    Test case for the Agent model.
    """

    def test_agent_creation(self):
        """Test creating a new agent."""
        agent = Agent.objects.create(
            name="Support Agent",
            description="A customer support agent",
            default_provider="openai",
            default_model="gpt-4",
            system_prompt="You are a helpful customer support agent.",
            is_active=True,
        )

        self.assertEqual(agent.name, "Support Agent")
        self.assertEqual(agent.description, "A customer support agent")
        self.assertEqual(agent.default_provider, "openai")
        self.assertEqual(agent.default_model, "gpt-4")
        self.assertEqual(
            agent.system_prompt, "You are a helpful customer support agent."
        )
        self.assertTrue(agent.is_active)
        self.assertTrue(hasattr(agent, 'created_at'))
        self.assertTrue(hasattr(agent, 'modified_at'))

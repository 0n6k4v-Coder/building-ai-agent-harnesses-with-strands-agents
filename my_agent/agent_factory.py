from strands import Agent
from my_agent.models.custom_openai_model import CustomOpenAIModel
from my_agent.provider_manager import ProviderManager
from my_agent.ui.terminal import RealTimeStateStreamer
from my_agent.config import AVAILABLE_TOOLS, SYSTEM_INSTRUCTION, PROVIDER_CONTEXT_WINDOW_LIMITS, DEFAULT_CONTEXT_WINDOW_LIMIT

class AgentFactory:
    @staticmethod
    def create_agent(manager: ProviderManager, provider_id: str, model_id: str = None) -> Agent:
        config = manager.get_provider(provider_id)
        if not config:
            raise ValueError(f"Provider '{provider_id}' not found in registry.")

        target_model = model_id or config.get("default_model")
        if not target_model:
            detected = manager.fetch_available_models(provider_id)
            target_model = detected[0] if detected else "gpt-4o"

        manager.set_active_provider(provider_id)
        manager.set_active_model(target_model)

        context_window_limit = PROVIDER_CONTEXT_WINDOW_LIMITS.get(
            provider_id, DEFAULT_CONTEXT_WINDOW_LIMIT
        )

        model = CustomOpenAIModel(
            client_args={
                "api_key": config.get("api_key"),
                "base_url": config.get("base_url"),
                "default_headers": {"User-Agent": "Mozilla/5.0"}
            },
            model_id=target_model,
            context_window_limit=context_window_limit,
        )

        state_streamer = RealTimeStateStreamer()

        agent_kwargs = {
            "model": model,
            "tools": AVAILABLE_TOOLS,
            "system_prompt": SYSTEM_INSTRUCTION,
            "context_manager": "agentic",
            "callback_handler": state_streamer,
        }

        try:
            return Agent(**agent_kwargs, max_iterations=8)
        except TypeError:
            try:
                from strands.types.agent import Limits
                return Agent(**agent_kwargs, limits=Limits(turns=8, total_tokens=20000))
            except (ImportError, TypeError):
                return Agent(**agent_kwargs)
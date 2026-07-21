from strands import Agent
from my_agent.models.custom_openai_model import CustomOpenAIModel
from my_agent.provider_manager import ProviderManager
from my_agent.ui.terminal import RealTimeStateStreamer
from my_agent.config import AVAILABLE_TOOLS, SYSTEM_INSTRUCTION, PROVIDER_CONTEXT_WINDOW_LIMITS, DEFAULT_CONTEXT_WINDOW_LIMIT
from strands.hooks import HookProvider, HookRegistry
from strands.hooks.events import BeforeToolCallEvent

class LimitToolCallsHook(HookProvider):
    def __init__(self, max_tool_calls: int = 8):
        self.max_tool_calls = max_tool_calls
        self.tool_call_count = 0

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.check_limit)

    def check_limit(self, event: BeforeToolCallEvent) -> None:
        self.tool_call_count += 1
        if self.tool_call_count > self.max_tool_calls:
            event.cancel_tool = (
                f"Tool call limit reached ({self.max_tool_calls}). "
                "STOP calling tools immediately and summarize what you have so far."
            )

class AgentFactory:
    @staticmethod
    def create_agent(manager: ProviderManager, provider_id: str, model_id: str = None, mcp_tools: list = None, mcp_info: str = "") -> Agent:
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

        all_tools = AVAILABLE_TOOLS + (mcp_tools or [])

        dynamic_system_prompt = SYSTEM_INSTRUCTION
        if mcp_info:
            dynamic_system_prompt += "\n\n" + mcp_info

        agent_kwargs = {
            "model": model,
            "tools": all_tools,
            "system_prompt": dynamic_system_prompt,
            "context_manager": "agentic",
            "callback_handler": state_streamer,
            "hooks": [LimitToolCallsHook(max_tool_calls=8)]
        }

        return Agent(**agent_kwargs)
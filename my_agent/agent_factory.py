import os
from strands import Agent
from my_agent.models.custom_openai_model import CustomOpenAIModel
from my_agent.provider_manager import ProviderManager
from my_agent.ui.terminal import RealTimeStateStreamer
from strands_tools import calculator, current_time
from my_agent.tools.file_ops import list_dir, read_file, write_file, edit_file_patch
from my_agent.tools.git_ops import git_inspector, git_committer, git_pusher

AVAILABLE_TOOLS = [
    calculator,
    current_time,
    git_inspector,
    git_committer,
    git_pusher,
    list_dir,
    read_file,
    write_file,
    edit_file_patch
]

PROVIDER_CONTEXT_WINDOW_LIMITS = {
    "thaillm": 16384,
}

DEFAULT_CONTEXT_WINDOW_LIMIT = 16384

class AgentFactory:
    @staticmethod
    def auto_seed_registry(manager: ProviderManager) -> None:
        if not manager.list_all_providers():
            print("📦 Registry is empty. Auto-seeding from your actual .env variables...")
            
            if os.getenv("THAILLM_BASE_URL"):
                manager.save_provider(
                    provider_id="thaillm",
                    base_url=os.getenv("THAILLM_BASE_URL"),
                    api_key=os.getenv("THAILLM_API_KEY")
                )
                if "thaillm" in manager.providers:
                    manager.providers["thaillm"]["default_model"] = os.getenv("THAILLM_MODEL_ID")
                    
            if os.getenv("NVIDIA_BASE_URL"):
                manager.save_provider(
                    provider_id="nvidia",
                    base_url=os.getenv("NVIDIA_BASE_URL"),
                    api_key=os.getenv("NVIDIA_API_KEY")
                )
                if "nvidia" in manager.providers:
                    manager.providers["nvidia"]["default_model"] = os.getenv("NVIDIA_MODEL_ID")
                    
            manager._save_to_storage()

    @staticmethod
    def create_agent(manager: ProviderManager, provider_id: str, model_id: str = None) -> Agent:
        config = manager.get_provider(provider_id)
        if not config:
            raise ValueError(f"Provider '{provider_id}' not found in registry.")

        target_model = model_id or config.get("default_model")
        if not target_model:
            detected = manager.fetch_available_models(provider_id)
            target_model = detected[0] if detected else "gpt-4o"

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

        if "active_model" not in config:
            config["active_model"] = target_model
        else:
            config["active_model"] = target_model

        system_instruction = (
            "You are an expert, highly precise terminal-based software engineering assistant.\n"
            "You have full capabilities to explore, read, create, and modify files in the current workspace directory.\n\n"
            "Guidelines:\n"
            "1. Always inspect directory content using 'list_dir' or file content using 'read_file' before assuming code layout.\n"
            "2. Prefer using 'edit_file_patch' for targeted code updates over rewriting entire files with 'write_file'.\n"
            "3. For Git operations: You have 3 tools: `git_inspector` (read-only), `git_committer` (to add and commit), and `git_pusher` (to push to remote).\n"
            "   - If the user asks for a draft or suggestion, provide the commands as text.\n"
            "   - If the user says 'approve', 'execute', 'run', 'commit', or 'push', you MUST use the corresponding git tool to perform the action. Do NOT tell the user to run it manually.\n"
            "4. Execute multi-step workflows sequentially without asking for permission between steps.\n"
            "5. Learn from tool errors and adapt your approach without repeating failed actions."
        )

        state_streamer = RealTimeStateStreamer()

        return Agent(
            model=model,
            tools=AVAILABLE_TOOLS,
            system_prompt=system_instruction,
            context_manager="agentic",
            callback_handler=state_streamer,
        )
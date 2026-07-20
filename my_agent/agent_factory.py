import os
from strands import Agent
from my_agent.models.custom_openai_model import CustomOpenAIModel
from my_agent.provider_manager import ProviderManager
from my_agent.ui.terminal import RealTimeStateStreamer
from strands_tools import calculator, current_time
from my_agent.tools.file_ops import list_dir, read_file, write_file, edit_file_patch
from my_agent.tools.git_ops import git_status, git_diff, git_log, git_commit, git_push

AVAILABLE_TOOLS = [
    calculator,
    current_time,
    git_status,
    git_diff,
    git_log,
    git_commit,
    git_push,
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
            "3. For Git operations: Map user intent to tools using this table — do NOT improvise:\n"
            "   | User intent        | Tool       | Required arguments                          |\n"
            "   |--------------------|------------|---------------------------------------------|\n"
            "   | 'check status'     | git_status | (none)                                      |\n"
            "   | 'show diff'        | git_diff   | (none)                                      |\n"
            "   | 'show log'         | git_log    | (none)                                      |\n"
            "   | 'commit' / 'approve' | git_commit | files=[...], commit_message=<descriptive> |\n"
            "   | 'push'             | git_push   | (none)                                      |\n"
            "4. The commit_message MUST be a human-readable description of the change. NEVER pass the words 'push', 'commit', or 'approve' as the commit_message.\n"
            "5. If the user says 'commit and push', call git_commit FIRST, wait for its result, then call git_push. Do not skip either step.\n"
            "6. After EVERY tool result, write one sentence summarizing what happened before deciding the next action.\n"
            "7. If a tool returns an error, do NOT retry with the same arguments. Stop and report the error to the user."
        )

        state_streamer = RealTimeStateStreamer()

        agent_kwargs = {
            "model": model,
            "tools": AVAILABLE_TOOLS,
            "system_prompt": system_instruction,
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
# my_agent/agent_factory.py
import os
from strands import Agent
from my_agent.models.custom_openai_model import CustomOpenAIModel
from my_agent.provider_manager import ProviderManager
from my_agent.ui.terminal import RealTimeStateStreamer
from strands_tools import calculator, current_time
from my_agent.tools.file_ops import list_dir, read_file, write_file, edit_file_patch
from my_agent.tools.git_ops import git_inspector, git_committer

AVAILABLE_TOOLS = [
    calculator,
    current_time,
    git_inspector,
    git_committer,
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
                manager.providers["thaillm"]["default_model"] = os.getenv("THAILLM_MODEL_ID")
            if os.getenv("NVIDIA_BASE_URL"):
                manager.save_provider(
                    provider_id="nvidia",
                    base_url=os.getenv("NVIDIA_BASE_URL"),
                    api_key=os.getenv("NVIDIA_API_KEY")
                )
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

        config["active_model"] = target_model

        system_instruction = (
            "You are an expert, highly precise terminal-based software engineering assistant.\n"
            "You have full capabilities to explore, read, create, and modify files in the current workspace directory.\n\n"
            "Operating Rules:\n"
            "1. Always inspect directory content using 'list_dir' or file content using 'read_file' before assuming code layout.\n"
            "2. When modifying existing source code, always prefer using 'edit_file_patch' for targeted search-and-replace updates "
            "rather than using 'write_file' to overwrite the whole file. This saves performance and avoids breaking clean code.\n"
            "3. ONE TASK = ONE OUTPUT FILE. If the user specifies a filename, always use exactly that filename for the "
            "entire task. Before calling 'write_file' to create a new file, ALWAYS call 'list_dir' first to check whether "
            "a file for this task already exists. If it does, you MUST use 'read_file' + 'edit_file_patch' on that existing "
            "file — NEVER create a second file with a different name for the same task.\n"
            "4. You have two git tools available:\n"
            "   - `git_inspector`: Use this to check what files have changed (e.g., command='diff --stat' or 'status'). This is READ-ONLY.\n"
            "   - `git_committer`: Use this to stage files and create a commit.\n"
            "   IMPORTANT DUAL-MODE RULE:\n"
            "   - If the user asks to 'generate', 'prepare', or 'draft' a commit: Use `git_inspector` to check changes, then STOP calling tools. Output the `git add` and `git commit` commands as text blocks for the user to copy-paste.\n"
            "   - If the user explicitly asks to 'execute', 'run', or 'commit it for me': Use `git_inspector` to check changes, then use `git_committer` to execute the commit directly.\n"
            "   - Commit messages MUST follow Conventional Commits format (feat:, fix:, chore:, refactor:, docs:).\n"
            "5. When the user gives a multi-step workflow, execute them sequentially. You don't need to ask for permission, "
            "just proceed to the next step automatically after receiving the result of the previous tool call.\n"
            "6. If a tool returns an error, read the error message carefully and fix your approach. Do NOT repeat the same broken request."
        )

        state_streamer = RealTimeStateStreamer()

        return Agent(
            model=model,
            tools=AVAILABLE_TOOLS,
            system_prompt=system_instruction,
            context_manager="agentic",
            callback_handler=state_streamer,
        )
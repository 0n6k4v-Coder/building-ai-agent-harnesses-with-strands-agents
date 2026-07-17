# building-ai-agent-harnesses-with-strands-agents

A collection of AI agent harnesses and implementations built using the Strands Agents SDK. This repository explores core concepts like context management, tool integration, agent loops, and orchestration patterns to build resilient AI agents.

## 🚀 Getting Started

To get your environment set up and ready for development, follow these steps:

### Prerequisites

* Ensure you have `python3` and `pip` installed on your system.
* If you are using GitHub Codespaces, the environment should already be configured.

### Configuration

Before running the agent, make sure to set up your environment variables at the root level:

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Open the `.env` file and configure your active provider and API keys:

```env
# Choose your active provider: "thaillm" or "nvidia"
ACTIVE_PROVIDER=thaillm

# 1. ThaiLLM Configuration
OPENAI_API_KEY=your_thaillm_api_key_here
OPENAI_BASE_URL=https://api.yourprovider.com/v1
THAI_MODEL_ID=Pathumma-ThaiLLM-qwen3-8b-think-3.0.0

# 2. NVIDIA NIM Configuration
NVIDIA_API_KEY=your_nvidia_api_key_here
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_MODEL_ID=meta/llama-3.1-8b-instruct
```

### Quick Setup

We provide a `setup.sh` script at the root level to automate the installation of dependencies and ensure your environment is ready.

1. **Make the script executable:**

```bash
chmod +x setup.sh
```

2. **Run the setup script:**

```bash
./setup.sh
```

This script will:

* Create a virtual environment inside the `my_agent/` directory (`my_agent/.venv`).
* Upgrade `pip` to the latest version.
* Install all necessary dependencies (including `uv` for MCP support) from `my_agent/requirements.txt`.

---

## 💻 Usage

After running `./setup.sh` successfully, activate the virtual environment and run the agent:

1. **Activate the Virtual Environment:**

```bash
# macOS / Linux:
source my_agent/.venv/bin/activate

# Windows (CMD):
my_agent\.venv\Scripts\activate.bat

# Windows (PowerShell):
my_agent\.venv\Scripts\Activate.ps1
```

2. **Run the Agent:**

```bash
python my_agent/agent.py
```

---

## 🛠️ Project Structure

```text
├── .agents/              # Agent settings and runtime configurations (Git ignored)
│   └── settings/
│       └── mcp.json      # Local Model Context Protocol configuration
├── .env                  # Local environment variables (API Keys, Base URLs, Providers)
├── .env.example          # Template example for environment variables
├── .gitignore            # Git exclusion settings
├── README.md             # Project documentation (Root)
├── setup.sh              # Automated multi-platform environment setup script
└── my_agent/             # Main working directory for the AI Agent
    ├── .venv/            # Local isolated Python virtual environment (Git ignored)
    ├── agent.py          # Main script executing the Strands Agent loop & tools
    └── requirements.txt  # Explicit Python dependencies (including uv for MCP)
```

---

## 📚 Key Concepts Covered

* **Agent Harness Engineering**: Orchestrating models, managing context, and enforcing boundaries.
* **Multi-Provider Configurations**: Hot-swapping backends dynamically between local/regional models like **ThaiLLM** and high-performance inference endpoints like **NVIDIA NIM**.
* **Agent Loops**: Building stateful loops that allow agents to reason, call tools dynamically, and recover from errors.
* **Tool Integration**: Connecting custom deterministic tools (e.g., `calculator`, `current_time`, `letter_counter`) to empower LLM execution.
* **MCP (Model Context Protocol) Support**: Ready-to-go setup integrating MCP servers utilizing [uv](https://github.com/astral-sh/uv) for lightning-fast server invocation and package management.
* **Context Management**: Proactive context handling for long-running and multi-step workflows.

---

## 🔗 Resources

* [How AI Agents Really Work](https://www.google.com/search?q=http://www.youtube.com/watch%3Fv%3DZpXWGjISMs8) - The foundational course driving this repository.

---

*Built with ❤️ and the Strands Agents SDK.*

```
---
Associated Course Reference Material: http://googleusercontent.com/youtube_content/1
```
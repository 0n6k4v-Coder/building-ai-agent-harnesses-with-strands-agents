# 🏗️ AI Agent Harness — Index

> **Version:** 1.3.0        
> **Last Updated:** 2024-07-24      
> **Source:** Local Workspace       
> **Prerequisite:** Python 3.10+, Strands Agents SDK

## Overview
โปรเจกต์นี้เป็น AI Agent Harness แบบ Clean Architecture ที่แยกหน้าที่ (SoC) ชัดเจน ใช้สำหรับรันและจัดการ AI Agent ผ่าน Terminal (CLI) รองรับการสลับ Provider/Model แบบ Interactive, เชื่อมต่อ MCP Servers แบบ Dynamic, กรอง Tools (Tool Filtering) เพื่อลด Context Bloat และปรับ Limit การเรียก Tools ตามขนาดโมเดลอัตโนมัติ (Dynamic Tool Limits)

## Contents
| # | Component | File | Description |
|---|-----------|------|-------------|
| 1 | Controller | `main.py` | จุดเริ่มต้นระบบ CLI REPL Loop, Route คำสั่ง และกรอง MCP Tools ตาม Allowlist |
| 2 | Configuration | `my_agent/config.py` | เก็บ System Prompt, Context Limits, Built-in Tools และ `MCP_TOOL_ALLOWLIST` |
| 3 | Factory | `my_agent/agent_factory.py` | ประกอบร่าง Agent จาก Model, Tools, Prompt และกำหนด Dynamic Tool Limits |
| 4 | State Management | `my_agent/provider_manager.py` | จัดการ API Keys, Active State และ Storage |
| 5 | MCP Manager | `my_agent/mcp_manager.py` | อ่าน Config และสร้าง MCPClient instances |
| 6 | UI - Input | `my_agent/ui/cli_input.py` | จัดการ PromptSession, Auto-completion, Interactive Menu |
| 7 | UI - Output | `my_agent/ui/terminal.py` | สตรีมและแสดงผลข้อมูล Real-time (Thinking/Tools/AI) |
| 8 | Custom Model | `models/custom_openai_model.py` | โมเดล OpenAI ที่จัดการ Context Overflow |
| 9 | MCP Config | `.agents/settings/mcp.json` | ไฟล์ตั้งค่าการเชื่อมต่อ MCP Servers |

## Directory Structure
```text
/
├── README.md                 # Project README
├── _index.md                 # This index file
├── main.py                   # Entry point: CLI REPL Loop + Command Router + Tool Filtering
├── setup.sh                  # Setup/installation script
├── providers_config.json     # API Keys, Active Provider/Model state
├── my_agent/                 # Main agent package
│   ├── __init__.py           # Package init
│   ├── __pycache__/          # Python bytecode cache (ignored)
│   ├── agent_factory.py      # Assemble Agent, Dynamic Tool Limits
│   ├── config.py             # System Prompt, Context Limits, Tools, MCP Allowlist
│   ├── mcp_manager.py        # Read config, create MCPClient instances
│   ├── provider_manager.py   # Manage API Keys, Active State, Storage
│   ├── requirements.txt      # Package dependencies
│   ├── models/
│   │   ├── __pycache__/      # Python bytecode cache (ignored)
│   │   └── custom_openai_model.py  # Custom OpenAI model with context overflow handling
│   └── ui/
│       ├── __pycache__/      # Python bytecode cache (ignored)
│       ├── cli_input.py      # PromptSession, Auto-completion, Interactive Menu
│       └── terminal.py       # Real-time streaming output (Thinking/Tools/AI)
├── repl_state/               # REPL state storage (empty, ignored)
├── slack_events/             # Slack events storage (empty, ignored)
└── .agents/                  # Agent settings (gitignored)
    └── settings/
        └── mcp.json          # MCP Servers config (e.g., MDN HTTP streamable)
```

## Search Strategy (When to Read / Edit)
| สถานการณ์ (User asks about...) | ไปที่ไฟล์ (Go to) |
|-----------------------------|-------------------|
| ต้องการแก้ไขพฤติกรรม AI หรือ System Prompt | `my_agent/config.py` |
| ต้องการเพิ่ม/ลด Built-in Tools | `my_agent/config.py` |
| ต้องการกำหนด MCP Tools ที่อนุญาต (Allowlist) | `my_agent/config.py` |
| ต้องการเชื่อมต่อ MCP Server ใหม่ | `.agents/settings/mcp.json` |
| ต้องการแก้ไข Logic การรับ Input หรือเมนู | `my_agent/ui/cli_input.py` |
| ต้องการแก้ไขวิธีการแสดงผลใน Terminal | `my_agent/ui/terminal.py` |
| ต้องการจัดการ Provider หรือ API Keys | `my_agent/provider_manager.py` |
| ต้องการปรับวิธีการสร้าง Agent หรือ Limit รอบการเรียก Tool | `my_agent/agent_factory.py` |

## Quick Reference
- **Tools ที่ใช้:** ใช้ Built-in Tools ของ Strands (เช่น `shell`, `file_read`, `editor`) ไม่มี Custom Tools ซ้ำซ้อน
- **MCP Filtering:** ระบบจะดึง Tools จาก MCP Servers มากรองผ่าน `MCP_TOOL_ALLOWLIST` ก่อนส่งเข้า Agent เพื่อลด Context Bloat
- **Dynamic Tool Limits:** ระบบจะปรับจำนวนครั้งที่ AI สามารถเรียก Tool ได้ (Max Iterations) ตามขนาดของโมเดลอัตโนมัติ (เช่น 8B จะได้ 15 รอบ, 70B จะได้ 30 รอบ)
- **State:** บันทึก Active Provider/Model ลง `providers_config.json` อัตโนมัติ

## Related Sections
| หากต้องการ... | ไปที่ |
|--------------|-------|
| เอกสาร Strands SDK | [Strands Agents Docs](https://strandsagents.com/latest/) |
| ตัวอย่างการใช้ MCP | [AWS Samples GitHub](https://github.com/aws-samples/sample-building-with-strands-course) |
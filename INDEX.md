# 🏗️ Project Structure

โปรเจกต์นี้ถูกออกแบบมาเป็นโมดูลาร์แบบ Clean Architecture เพื่อแยกหน้าที่ (Separation of Concerns) ให้ชัดเจน ทำให้สามารถจัดการ Agent, UI, และ Business Logic ได้อย่างยืดหยุ่นและดูแลรักษาง่าย:

## 🏗️ Directory Structure

```text
/
├── .agents/                  # การตั้งค่าเอเจนต์ (รวม mcp.json)
├── my_agent/                 # โมดูลหลักของเอเจนต์
│   ├── ui/                   # โมดูลจัดการ UI (Presentation Layer)
│   │   ├── cli_input.py      # จัดการ PromptSession, Auto-completion และ Interactive Menu
│   │   └── terminal.py       # สตรีมข้อความและแสดงผลข้อมูล Real-time (Thinking/Tools/AI)
│   ├── tools/                # รวมเครื่องมือ (Tools)
│   │   ├── file_ops.py       # จัดการไฟล์ (read/write/patch)
│   │   └── git_ops.py        # จัดการ Git (แยกเป็น Atomic Tools: status, diff, commit, push)
│   ├── agent_factory.py      # โรงงานประกอบร่างเอเจนต์ (รับผิดชอบเฉพาะการสร้าง Instance)
│   ├── config.py             # เก็บค่าคงที่, System Prompt, และการลงทะเบียน Tools
│   └── provider_manager.py   # ตัวจัดการ Provider, State (Active Model), และ Storage
├── models/                   # โมดูลโมเดลส่วนขยาย
│   └── custom_openai_model.py # โมเดล OpenAI ที่ปรับแต่ง (จัดการ Context Overflow และ Sanitize Messages)
├── .env                      # ตัวแปรสภาพแวดล้อม (API Keys)
├── .env.example              # ตัวอย่างตัวแปรสภาพแวดล้อม
├── .gitignore                # การตั้งค่าไฟล์ที่ไม่ต้องการให้ Git ติดตาม
├── INDEX.md                  # เอกสารคู่มือโครงการ (ไฟล์นี้)
├── main.py                   # จุดเริ่มต้นระบบ (Controller & REPL Loop)
├── README.md                 # รายละเอียดโครงการ
├── requirements.txt          # รายการ dependencies
├── setup.sh                  # สคริปต์ตั้งค่าสภาพแวดล้อม
└── providers_config.json     # การตั้งค่าและบันทึก State ของ Provider
```

## 🚀 Key Components 

* **`main.py` (Controller)**: หัวใจหลักของ Harness ทำหน้าที่เป็น CLI REPL Loop และทำหน้าที่เป็น Controller ในการ Route คำสั่ง (Slash Commands) โดยไม่ยุ่งกับ Logic ของ UI มีระบบ **Auto-Recovery** (Reset Session) เมื่อเกิด Error หรือ Token ล้น
* **`my_agent/config.py` (Configuration)**: ศูนย์กลางการเก็บการตั้งค่า รวมถึง System Prompt ที่ใช้ควบคุมพฤติกรรมของ AI, รายการเครื่องมือ (Tools Registry) และขีดจำกัด Context Window ของแต่ละ Provider
* **`my_agent/agent_factory.py` (Factory)**: ทำหน้าที่เฉพาะการ "ประกอบร่าง" (Assembly) Agent จากส่วนต่างๆ (Model, Tools, Prompt, UI Streamer) โดยไม่มี Logic ยุ่งเกี่ยวกับการจัดการ State หรือการอ่าน Config โดยตรง
* **`my_agent/provider_manager.py` (State Management)**: โมดูลสำหรับจัดการ API Keys, การดึงรายชื่อ Model จาก Provider, การ Auto-seed ข้อมูลจาก `.env` และที่สำคัญคือจัดการบันทึก/อ่าน State (Active Provider/Model) ลง `providers_config.json`
* **`my_agent/ui/cli_input.py` (Presentation Layer)**: จัดการการรับ Input จากผู้ใช้ด้วย `prompt_toolkit` รวมถึงระบบ Auto-completion และ Interactive Menu (เมนูแบบเลื่อนเลือกด้วยปุ่มลูกศร) สำหรับการสลับ Model
* **`my_agent/ui/terminal.py` (View Streamer)**: โมดูลควบคุมการแสดงผลข้อมูลแบบ Real-time แยกส่วนของ "Thinking State" และ "Tool Call State" ออกจาก "AI Answer" ให้อ่านง่ายใน Terminal
* **`my_agent/tools/`**: พื้นที่เก็บเครื่องมือ (Tools) ที่ออกแบบมาเป็น Atomic (หนึ่งฟังก์ชันต่อหนึ่งงาน) เพื่อลดความสับสนของ AI เช่น `git_ops.py` ที่แยก `git_status`, `git_commit`, `git_push` ออกจากกันอย่างชัดเจน
* **`.agents/settings/mcp.json`**: ไฟล์ตั้งค่าการเชื่อมต่อ **Model Context Protocol (MCP)** เพื่อการสื่อสารระหว่าง Agent กับระบบภายนอก
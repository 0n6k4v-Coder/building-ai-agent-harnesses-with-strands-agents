# 🏗️ Project Structure

โปรเจกต์นี้ถูกออกแบบมาเป็นโมดูลาร์เพื่อความยืดหยุ่นในการจัดการ Agent และ Tools:

## 🏗️ Project Structure

```text
/
├── .agents/                  # การตั้งค่าเอเจนต์ (รวม mcp.json)
├── my_agent/                 # โมดูลหลักของเอเจนต์
│   ├── __pycache__/
│   ├── ui/                   # โมดูลจัดการ UI (terminal.py)
│   ├── tools/                # รวมเครื่องมือ (Tools)
│   │   ├── file_ops.py       # จัดการไฟล์ (read/write/patch)
│   │   └── git_ops.py        # จัดการ Git
│   ├── agent_factory.py      # โรงงานสร้างเอเจนต์
│   └── provider_manager.py   # ตัวจัดการ Provider (API/Base URL)
├── models/                   # โมดูลโมเดลส่วนขยาย
│   └── custom_openai_model.py
├── .env                      # ตัวแปรสภาพแวดล้อม (API Keys)
├── .env.example              # ตัวอย่างตัวแปรสภาพแวดล้อม
├── .gitignore                # การตั้งค่าไฟล์ที่ไม่ต้องการให้ Git ติดตาม
├── INDEX.md                  # เอกสารคู่มือโครงการ (ไฟล์นี้)
├── main.py                   # จุดเริ่มต้นระบบ (Harness REPL Loop)
├── README.md                 # รายละเอียดโครงการ
├── requirements.txt          # รายการ dependencies
├── setup.sh                  # สคริปต์ตั้งค่าสภาพแวดล้อม
└── providers_config.json     # การตั้งค่า Config ของ Provider
```

## 🚀 Key Components 

* **`main.py`**: หัวใจหลักของ Harness ทำหน้าที่เป็น **CLI REPL Loop**, จัดการ Context Window, และทำ **Auto-Recovery** (Reset Session) เมื่อเกิด Error หรือ Token ล้น
* **`agent_factory.py`**: ศูนย์กลางการประกอบร่างเอเจนต์ ทำหน้าที่เชื่อมต่อ Provider, จัดการ **Model Configuration**, และลงทะเบียน Tools ทั้งหมดเข้ากับระบบ
* **`my_agent/tools/`**: พื้นที่เก็บเครื่องมือ (Tools) สำหรับเพิ่มขีดความสามารถ เช่น `file_ops.py` (จัดการไฟล์) และ `git_ops.py` (จัดการเวอร์ชันควบคุม)
* **`.agents/settings/mcp.json`**: (ใหม่) ไฟล์ตั้งค่าการเชื่อมต่อ **Model Context Protocol (MCP)** เพื่อการสื่อสารระหว่าง Agent กับโลกภายนอก
* **`my_agent/provider_manager.py`**: (ใหม่) โมดูลสำหรับจัดการ API Keys และการตั้งค่า Provider ต่างๆ (เช่น `thaillm` หรือ `nvidia`) อย่างเป็นระบบ
* **`my_agent/ui/terminal.py`**: (ใหม่) โมดูลควบคุมการแสดงผลข้อมูลแบบ Real-time และการสตรีมข้อความในหน้า Terminal
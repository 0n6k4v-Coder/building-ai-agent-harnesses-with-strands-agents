#!/bin/bash

# สร้าง Virtual Environment ในโฟลเดอร์ my_agent ถ้ายังไม่มี
if [ ! -d "my_agent/.venv" ]; then
    python3 -m venv my_agent/.venv
fi

# Activate environment จากโฟลเดอร์ my_agent
source my_agent/.venv/bin/activate

# Upgrade pip อัตโนมัติ
pip install --upgrade pip

# ติดตั้ง Library จาก my_agent/requirements.txt
if [ -f "my_agent/requirements.txt" ]; then
    pip install -r my_agent/requirements.txt
else
    echo "ไม่พบไฟล์ requirements.txt ในโฟลเดอร์ my_agent"
fi
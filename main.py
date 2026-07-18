# main.py
import os
import sys
import contextlib
from dotenv import load_dotenv

from my_agent.provider_manager import ProviderManager
from my_agent.agent_factory import AgentFactory
from my_agent.ui.terminal import RealTimeStateStreamer

# Load configuration layers
load_dotenv()

def main_repl():
    # 1. โหลดข้อมูลการจัดเก็บผู้ให้บริการ (Registry Manager)
    manager = ProviderManager(config_path="providers_config.json")
    
    # 2. ทำการตรวจสอบและใส่โมเดลตั้งต้นลงไฟล์หากเป็นครั้งแรก
    AgentFactory.auto_seed_registry(manager)

    # 3. ตรวจเช็คค่าผู้ให้บริการปัจจุบันที่เลือกใช้
    active_provider = os.getenv("ACTIVE_PROVIDER", "thaillm").lower()
    if active_provider not in manager.list_all_providers():
        active_provider = manager.list_all_providers()[0] if manager.list_all_providers() else "thaillm"

    # 4. เรียกใช้ Factory ในการประกอบร่าง Agent ขึ้นมาทำงาน
    current_agent = AgentFactory.create_agent(manager, active_provider)
    active_model = manager.get_provider(active_provider).get("active_model", "unknown")

    # 5. แสดงผล Banner หน้าต่างใช้งานในโมเดล Modular คลีน ๆ
    print("\n=======================================================")
    print("🚀 STRANDS CLI INTERACTIVE CHAT RUNNING (Clean Modular Style)")
    print(f"📡 Active Provider: \033[92m{active_provider}\033[0m")
    print(f"🤖 Active Model:    \033[94m{active_model}\033[0m")
    print("=======================================================\n")

    # 6. ลูปหลักสำหรับประมวลผลคำสั่งใน Terminal REPL
    while True:
        try:
            user_input = input("\033[96m👤 You > \033[0m").strip()
            if not user_input:
                continue

            if user_input.startswith("/"):
                command = user_input.lower().split()[0]
                if command in ["/exit", "/quit"]:
                    print("👋 Exiting terminal session. Goodbye!")
                    sys.exit(0)
                continue

            print("\n⌛ \033[90mAgent is processing query...\033[0m")
            
            # 🔥 ดึงคลาส UI Streamer มาช่วยจับ Stream ดิบและจัดการแยกแท็กแบบเรียลไทม์
            streamer = RealTimeStateStreamer()
            with contextlib.redirect_stdout(streamer):
                current_agent(user_input)
                
            print("")  # ขึ้นบรรทัดใหม่หลังตอบจบเทิร์น

        except KeyboardInterrupt:
            print("\n\n⚠️ Session interrupted via terminal trigger. Type /exit to close properly.")
        except Exception as e:
            print(f"\n❌ Runtime execution error encountered: {e}\n")

if __name__ == "__main__":
    main_repl()
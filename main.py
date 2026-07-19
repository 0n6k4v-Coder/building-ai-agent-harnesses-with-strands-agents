import sys
from my_agent.provider_manager import ProviderManager
from my_agent.agent_factory import AgentFactory
from my_agent.ui.cli_input import create_cli_session, get_user_input

COMMAND_MAPPINGS = {
    "/continue": (
        "ทำงานต่อจากขั้นตอนที่ค้างไว้ตาม workflow เดิมที่สั่งไป "
        "ห้ามสร้างไฟล์ใหม่เด็ดขาด ให้ใช้ read_file + edit_file_patch "
        "กับไฟล์ showcase.html ที่มีอยู่แล้วเท่านั้น"
    )
}

class HarnessApp:
    def __init__(self):
        self.provider_manager = ProviderManager()
        AgentFactory.auto_seed_registry(self.provider_manager)
        self.global_agent = AgentFactory.create_agent(self.provider_manager, provider_id="thaillm")
        self.cli_session = create_cli_session()

    def reset_agent_session(self):
        print("\n🔄 [Harness Action] กำลังสร้างอินสแตนซ์เอเจนต์ใหม่เพื่อรีเซ็ตหน่วยความจำ...")
        try:
            self.global_agent = AgentFactory.create_agent(self.provider_manager, provider_id="thaillm")
            print("✨ รีเซ็ตสถานะสำเร็จ! บริบทสะอาดพร้อมรับคำสั่งใหม่")
        except Exception as e:
            print(f"⚠️ ไม่สามารถเคลียร์หน่วยความจำได้: {e}")

    def run(self):
        print("=======================================================")
        print("🚀 STRANDS CLI INTERACTIVE CHAT RUNNING (Fixed Factory Architecture)")
        print("📡 Active Provider: thaillm")
        print("🤖 Active Model:    pathumma-thaillm-qwen3-8b-think-3.0.0")
        print("💡 คำสั่งระบบ: [/clear] เพื่อล้างหน่วยความจำ | [/paste] เพื่อวางข้อความหลายบรรทัด | [/exit] เพื่อออก")
        print("=======================================================")

        while True:
            try:
                user_input = get_user_input(self.cli_session)

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    command = user_input.lower().split()[0]
                    if command in ["/exit", "/quit"]:
                        print("ออกจากระบบ Harness. สวัสดีครับ!")
                        sys.exit(0)
                    elif command in ["/clear", "/reset"]:
                        self.reset_agent_session()
                        continue
                    elif command in COMMAND_MAPPINGS:
                        user_input = COMMAND_MAPPINGS[command]

                print("\n⌛ Agent is processing query...\n")
                self.global_agent(user_input)
                print("\n")

            except Exception as e:
                error_msg = str(e)
                print(f"\n❌ Runtime execution error encountered: {error_msg}")

                if "16384" in error_msg or "context" in error_msg.lower() or "400" in error_msg:
                    print("\n🚨 [Harness Auto-Recovery] Strands ไม่สามารถ auto-compress ได้ กำลังรีเซ็ต session...")
                    self.reset_agent_session()

if __name__ == "__main__":
    try:
        app = HarnessApp()
        app.run()
    except KeyboardInterrupt:
        print("\nSession interrupted by user. Exiting...")
        sys.exit(0)
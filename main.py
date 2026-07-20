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
        
        self.active_provider_id = self.provider_manager.get_active_provider()
        self.active_model_id = self.provider_manager.get_active_model()
        
        self.global_agent = AgentFactory.create_agent(
            self.provider_manager, 
            provider_id=self.active_provider_id,
            model_id=self.active_model_id
        )
        
        provider_config = self.provider_manager.get_provider(self.active_provider_id)
        self.active_model_id = provider_config.get("active_model") if provider_config else self.active_model_id
        
        if self.active_model_id:
            self.provider_manager.set_active_model(self.active_model_id)
            
        self.cli_session = create_cli_session(self.provider_manager)

    def reset_agent_session(self, provider_id=None, model_id=None):
        print("\n🔄 [Harness Action] กำลังสร้างอินสแตนซ์เอเจนต์ใหม่...")
        try:
            p_id = provider_id or self.active_provider_id
            m_id = model_id or self.active_model_id
            
            self.global_agent = AgentFactory.create_agent(
                self.provider_manager, 
                provider_id=p_id,
                model_id=m_id
            )
            self.active_provider_id = p_id
            
            provider_config = self.provider_manager.get_provider(p_id)
            self.active_model_id = provider_config.get("active_model") if provider_config else m_id
            
            self.provider_manager.set_active_provider(p_id)
            self.provider_manager.set_active_model(self.active_model_id)
            
            print("✨ รีเซ็ตสถานะสำเร็จ!")
        except Exception as e:
            print(f"⚠️ ไม่สามารถเคลียร์หน่วยความจำได้: {e}")

    def run(self):
        print("=======================================================")
        print("🚀 STRANDS CLI INTERACTIVE CHAT RUNNING")
        print(f"📡 Active Provider: {self.active_provider_id}")
        print(f"🤖 Active Model:    {self.active_model_id or 'default'}")
        print("💡 คำสั่งระบบ: [/clear] | [/exit]")
        print("💡 เปลี่ยน Model: พิมพ์ /model แล้วกด Enter")
        print("=======================================================")

        while True:
            try:
                user_input = get_user_input(self.cli_session)

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    parts = user_input.split()
                    command = parts[0]
                    
                    if command in ["/exit", "/quit"]:
                        print("ออกจากระบบ Harness. สวัสดีครับ!")
                        sys.exit(0)
                        
                    elif command in ["/clear", "/reset"]:
                        self.reset_agent_session()
                        continue
                        
                    elif command == "/model":
                        if "/back" in parts or "/cancel" in parts:
                            print("\n🚫 ยกเลิกการเปลี่ยนแปลง\n")
                            continue
                            
                        if len(parts) >= 2:
                            target = parts[-1].lstrip("/")
                            
                            if "/" in target:
                                p_id, m_id = target.split("/", 1)
                                print(f"\n🔄 กำลังสลับไปยัง Provider: {p_id}, Model: {m_id}...")
                                self.reset_agent_session(provider_id=p_id, model_id=m_id)
                            else:
                                if self.provider_manager.get_provider(target):
                                    print(f"\n🔄 กำลังสลับไปยัง Provider: {target}...")
                                    self.reset_agent_session(provider_id=target, model_id=None)
                                else:
                                    print(f"\n❌ ไม่พบ Provider '{target}'\n")
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
                    print("\n🚨 [Harness Auto-Recovery] กำลังรีเซ็ต session...")
                    self.reset_agent_session()

if __name__ == "__main__":
    try:
        app = HarnessApp()
        app.run()
    except KeyboardInterrupt:
        print("\nSession interrupted by user. Exiting...")
        sys.exit(0)
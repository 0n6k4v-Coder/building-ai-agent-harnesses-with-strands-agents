import sys
import contextlib
from my_agent.provider_manager import ProviderManager
from my_agent.agent_factory import AgentFactory
from my_agent.mcp_manager import MCPManager
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
        self.provider_manager.auto_seed_registry()
        
        self.active_provider_id = self.provider_manager.get_active_provider()
        self.active_model_id = self.provider_manager.get_active_model()
        
        self.mcp_manager = MCPManager()
        self.mcp_stack = contextlib.ExitStack()
        
        self.mcp_tools = []
        self.mcp_info_text = ""
        
        mcp_clients = self.mcp_manager.get_clients()
        
        if mcp_clients:
            info_lines = ["🧩 CONNECTED MCP SERVERS & TOOLS (EXTERNAL CAPABILITIES):"]
            for name, client in mcp_clients.items():
                try:
                    active_client = self.mcp_stack.enter_context(client)
                    tools = active_client.list_tools_sync()
                    self.mcp_tools.extend(tools)
                    
                    tool_names = []
                    for t in tools:
                        t_name = getattr(t, "tool_name", getattr(t, "name", str(t)))
                        tool_names.append(t_name)
                    
                    info_lines.append(f"- Server '{name}': Provides tools {tool_names}")
                except Exception as e:
                    print(f"⚠️ ไม่สามารถเชื่อมต่อ MCP Server '{name}' ได้: {e}")
            
            if len(self.mcp_tools) > 0:
                self.mcp_info_text = (
                    "\n".join(info_lines) + 
                    "\n\nCRITICAL INSTRUCTION: You are operating inside an AI Agent Harness that has connected you to external MCP Servers. "
                    "If the user asks 'what MCP servers are connected?', 'what tools do you have?', or 'do you see MCP?', "
                    "you MUST answer by listing the servers and tools provided in the section above. "
                    "Do NOT say you cannot see them. You are actively connected to them."
                )

        self.global_agent = AgentFactory.create_agent(
            self.provider_manager, 
            provider_id=self.active_provider_id,
            model_id=self.active_model_id,
            mcp_tools=self.mcp_tools,
            mcp_info=self.mcp_info_text
        )
        
        self.active_model_id = self.provider_manager.get_active_model()
        self.cli_session = create_cli_session(self.provider_manager)

    def reset_agent_session(self, provider_id=None, model_id=None):
        print("\n🔄 [Harness Action] กำลังสร้างอินสแตนซ์เอเจนต์ใหม่...")
        try:
            p_id = provider_id or self.active_provider_id
            m_id = model_id or self.active_model_id
            
            self.global_agent = AgentFactory.create_agent(
                self.provider_manager, 
                provider_id=p_id,
                model_id=m_id,
                mcp_tools=self.mcp_tools,
                mcp_info=self.mcp_info_text
            )
            self.active_provider_id = p_id
            self.active_model_id = self.provider_manager.get_active_model()
            
            print("✨ รีเซ็ตสถานะสำเร็จ!")
        except Exception as e:
            print(f"⚠️ ไม่สามารถเคลียร์หน่วยความจำได้: {e}")

    def handle_slash_command(self, user_input: str) -> bool:
        parts = user_input.split()
        command = parts[0]
        
        if command in ["/exit", "/quit"]:
            print("ออกจากระบบ Harness. สวัสดีครับ!")
            sys.exit(0)
            
        elif command in ["/clear", "/reset"]:
            self.reset_agent_session()
            return True
            
        elif command == "/model":
            if "/cancel" in parts:
                print("\n🚫 ยกเลิกการเปลี่ยนแปลง\n")
                return True
                
            if len(parts) >= 3:
                p_id = parts[1].lstrip("/")
                m_id = parts[2].lstrip("/")
                print(f"\n🔄 กำลังสลับไปยัง Provider: {p_id}, Model: {m_id}...")
                self.reset_agent_session(provider_id=p_id, model_id=m_id)
            return True
            
        elif command in COMMAND_MAPPINGS:
            return COMMAND_MAPPINGS[command]

        return user_input

    def run(self):
        print("=======================================================")
        print("🚀 STRANDS CLI INTERACTIVE CHAT RUNNING")
        print(f"📡 Active Provider: {self.active_provider_id}")
        print(f"🤖 Active Model:    {self.active_model_id or 'default'}")
        if self.mcp_tools:
            print(f"🔌 MCP Tools:       Loaded {len(self.mcp_tools)} tools")
        print("💡 คำสั่งระบบ: [/clear] | [/exit]")
        print("💡 เปลี่ยน Model: พิมพ์ /model แล้วกด Enter")
        print("=======================================================")

        while True:
            try:
                user_input = get_user_input(self.cli_session)
                if not user_input:
                    continue

                if user_input.startswith("/"):
                    processed = self.handle_slash_command(user_input)
                    if processed is True:
                        continue
                    elif processed is False:
                        continue
                    else:
                        user_input = processed

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
    finally:
        if 'app' in locals():
            app.mcp_stack.close()
        sys.exit(0)
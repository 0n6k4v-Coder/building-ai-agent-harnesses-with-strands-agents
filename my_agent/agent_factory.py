# my_agent/agent_factory.py
import os
from strands import Agent
from strands.models.openai import OpenAIModel
from my_agent.provider_manager import ProviderManager

# Import tools (เหลือเฉพาะเครื่องมือมาตรฐานจาก strands_tools)
from strands_tools import calculator, current_time

AVAILABLE_TOOLS = [calculator, current_time]

class AgentFactory:
    @staticmethod
    def auto_seed_registry(manager: ProviderManager) -> None:
        """ตรวจสอบและสร้างโมเดลเริ่มต้นจากตัวแปรสภาพแวดล้อมหาก Registry ว่างเปล่า"""
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
        """ประกอบร่าง OpenAIModel และพ่วง Tools ส่งกลับออกไปเป็น Instance ของ Strands Agent"""
        config = manager.get_provider(provider_id)
        if not config:
            raise ValueError(f"Provider '{provider_id}' not found in registry.")
        
        target_model = model_id or config.get("default_model")
        if not target_model:
            detected = manager.fetch_available_models(provider_id)
            target_model = detected[0] if detected else "gpt-4o"
            
        model = OpenAIModel(
            client_args={
                "api_key": config.get("api_key"),
                "base_url": config.get("base_url"),
                "default_headers": {"User-Agent": "Mozilla/5.0"}
            },
            model_id=target_model
        )
        
        # บันทึกโมเดลหลักที่ถูกเลือกใส่กลับเข้าไปในดิคชันนารีคอนฟิกชั่วคราว
        config["active_model"] = target_model
        
        return Agent(
            model=model,
            tools=AVAILABLE_TOOLS,
            system_prompt="You are a clear and concise terminal AI assistant. Use tools when needed."
        )
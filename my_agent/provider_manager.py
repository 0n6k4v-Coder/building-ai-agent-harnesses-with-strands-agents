import json
import os
import requests

class ProviderManager:
    def __init__(self, config_path="providers_config.json"):
        self.config_path = config_path
        self.providers = self._load_from_storage()

    def _load_from_storage(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_to_storage(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.providers, f, indent=2, ensure_ascii=False)

    def save_provider(self, provider_id: str, base_url: str, api_key: str):
        self.providers[provider_id.lower()] = {
            "base_url": base_url,
            "api_key": api_key
        }
        self._save_to_storage()

    def get_provider(self, provider_id: str) -> dict:
        return self.providers.get(provider_id.lower())

    def list_all_providers(self) -> list:
        return [k for k in self.providers.keys() if not k.startswith("_")]

    def fetch_available_models(self, provider_id: str) -> list:
        config = self.get_provider(provider_id)
        if not config:
            return []

        base_url = config.get("base_url", "").rstrip("/")
        api_key = config.get("api_key", "")

        try:
            response = requests.get(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return [model["id"] for model in data.get("data", [])]
            else:
                print(f"⚠️ Failed to fetch models from API. HTTP Status: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️ Error connection timeout or invalid URL layout: {e}")
            return []

    def get_active_provider(self) -> str:
        return self.providers.get("_active_provider_id", "thaillm")

    def set_active_provider(self, provider_id: str):
        self.providers["_active_provider_id"] = provider_id.lower()
        self._save_to_storage()

    def get_active_model(self) -> str:
        return self.providers.get("_active_model_id", None)

    def set_active_model(self, model_id: str):
        self.providers["_active_model_id"] = model_id
        self._save_to_storage()
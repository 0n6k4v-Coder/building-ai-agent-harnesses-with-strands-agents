import json
import os
import requests

class ProviderManager:
    def __init__(self, config_path="providers_config.json"):
        self.config_path = config_path
        self.providers = self._load_from_storage()

    def _load_from_storage(self):
        """Load registered providers from local JSON file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_to_storage(self):
        """Persist registered providers dictionary to disk."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.providers, f, indent=2, ensure_ascii=False)

    def save_provider(self, provider_id: str, base_url: str, api_key: str):
        """Register or overwrite a user-defined provider mapping."""
        self.providers[provider_id.lower()] = {
            "base_url": base_url,
            "api_key": api_key
        }
        self._save_to_storage()

    def get_provider(self, provider_id: str) -> dict:
        """Get endpoint and credentials for a given provider."""
        return self.providers.get(provider_id.lower())

    def list_all_providers(self) -> list:
        """Return a list of all registered provider names."""
        return list(self.providers.keys())

    def fetch_available_models(self, provider_id: str) -> list:
        """
        Dynamically query the provider's OpenAI-compatible /models endpoint 
        to detect available model IDs in real-time.
        """
        config = self.get_provider(provider_id)
        if not config:
            return []

        base_url = config.get("base_url", "").rstrip("/")
        api_key = config.get("api_key", "")

        try:
            # Send HTTP GET request to standard OpenAI-compatible models layout
            response = requests.get(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                # Extract and return the model ID string from each item in the data array
                return [model["id"] for model in data.get("data", [])]
            else:
                print(f"⚠️ Failed to fetch models from API. HTTP Status: {response.status_code}")
                return []
        except Exception as e:
            print(f"⚠️ Error connection timeout or invalid URL layout: {e}")
            return []
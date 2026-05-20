from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


PROVIDER_DEFAULTS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-haiku-4-5-20251001",
    "gemini": "gemini-1.5-flash",
    "mistral": "mistral-small",
}

PROVIDER_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "mistral": "MISTRAL_API_KEY",
}


class Settings(BaseSettings):
    # Embedding
    embedding_model: str = "all-MiniLM-L6-v2"

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"
    bundled_collection: str = "bundled"
    user_collection: str = "user"

    # Chunking
    chunk_size: int = 800
    chunk_overlap: int = 150

    # Retrieval
    retrieval_top_k: int = 5

    # LLM provider keys (optional — whichever is set gets offered in the UI)
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    mistral_api_key: Optional[str] = Field(default=None, env="MISTRAL_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def available_providers(self) -> dict[str, str]:
        """Returns {provider: default_model} for each provider with a key set."""
        result = {}
        if self.openai_api_key:
            result["openai"] = PROVIDER_DEFAULTS["openai"]
        if self.anthropic_api_key:
            result["anthropic"] = PROVIDER_DEFAULTS["anthropic"]
        if self.gemini_api_key:
            result["gemini"] = PROVIDER_DEFAULTS["gemini"]
        if self.mistral_api_key:
            result["mistral"] = PROVIDER_DEFAULTS["mistral"]
        return result

    def litellm_model_string(self, provider: str, model: Optional[str] = None) -> str:
        """Returns the LiteLLM model string for a given provider."""
        base = model or PROVIDER_DEFAULTS.get(provider, "")
        if provider == "openai":
            return base
        return f"{provider}/{base}"


settings = Settings()

# Export keys into os.environ so LiteLLM can find them
_key_env_map = {
    settings.openai_api_key: "OPENAI_API_KEY",
    settings.anthropic_api_key: "ANTHROPIC_API_KEY",
    settings.gemini_api_key: "GEMINI_API_KEY",
    settings.mistral_api_key: "MISTRAL_API_KEY",
}
for _val, _env_var in [
    (settings.openai_api_key, "OPENAI_API_KEY"),
    (settings.anthropic_api_key, "ANTHROPIC_API_KEY"),
    (settings.gemini_api_key, "GEMINI_API_KEY"),
    (settings.mistral_api_key, "MISTRAL_API_KEY"),
]:
    if _val:
        os.environ[_env_var] = _val

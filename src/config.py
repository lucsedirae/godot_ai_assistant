# src/config.py
"""
Centralized configuration management for Godot AI Development Assistant.
Handles all environment variables and application settings.
"""
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


@dataclass
class APIConfig:
    """Configuration for API providers (Anthropic/OpenAI)"""

    provider: str
    anthropic_key: Optional[str]
    openai_key: Optional[str]

    @classmethod
    def from_env(cls) -> "APIConfig":
        """Create API configuration from environment variables"""
        provider = os.getenv("API_PROVIDER", "anthropic").lower()
        return cls(
            provider=provider,
            anthropic_key=os.getenv("ANTHROPIC_API_KEY"),
            openai_key=os.getenv("OPENAI_API_KEY"),
        )

    def validate(self) -> None:
        """
        Validate that required API keys are present.

        Raises:
                ValueError: If required API key is missing for the selected provider
        """
        if self.provider == "anthropic" and not self.anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        if self.provider == "openai" and not self.openai_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        if self.provider not in ["anthropic", "openai"]:
            raise ValueError(
                f"Invalid API_PROVIDER: {self.provider}. Must be 'anthropic' or 'openai'"
            )


@dataclass
class EmbeddingConfig:
    """Configuration for embedding providers"""

    provider: str

    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        """Create embedding configuration from environment variables"""
        provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
        return cls(provider=provider)

    def validate(self) -> None:
        """
        Validate embedding provider configuration.

        Raises:
                ValueError: If provider is invalid
        """
        if self.provider not in ["local", "openai"]:
            raise ValueError(
                f"Invalid EMBEDDING_PROVIDER: {self.provider}. Must be 'local' or 'openai'"
            )

        if self.provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY required for OpenAI embeddings")


@dataclass
class PathConfig:
    """Configuration for application paths"""

    project_path: Path
    docs_path: Path
    lore_path: Path
    db_path: Path

    @classmethod
    def from_env(cls) -> "PathConfig":
        """Create path configuration from environment variables"""
        return cls(
            project_path=Path(os.getenv("GODOT_PROJECT_PATH", "/app/project")),
            docs_path=Path("/app/godot_docs"),
            lore_path=Path("/app/data/lore"),
            db_path=Path("/app/data/chroma_db"),
        )

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        self.lore_path.mkdir(parents=True, exist_ok=True)
        self.db_path.mkdir(parents=True, exist_ok=True)


@dataclass
class RAGConfig:
    """Configuration for RAG (Retrieval Augmented Generation) settings"""

    chunk_size: int
    chunk_overlap: int
    retrieval_k: int

    @classmethod
    def default(cls) -> "RAGConfig":
        """Create default RAG configuration"""
        return cls(
            chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "200")),
            retrieval_k=int(os.getenv("RAG_RETRIEVAL_K", "6")),
        )


@dataclass
class LLMConfig:
    """Configuration for LLM models"""

    anthropic_model: str
    openai_model: str
    temperature: float

    @classmethod
    def default(cls) -> "LLMConfig":
        """Create default LLM configuration"""
        return cls(
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
        )


@dataclass
class WebConfig:
    """Configuration for web application"""

    host: str
    port: int
    debug: bool

    @classmethod
    def from_env(cls) -> "WebConfig":
        """Create web configuration from environment variables"""
        return cls(
            host=os.getenv("WEB_HOST", "0.0.0.0"),
            port=int(os.getenv("WEB_PORT", "5000")),
            debug=os.getenv("WEB_DEBUG", "True").lower() == "true",
        )


@dataclass
class AppConfig:
    """Main application configuration container"""

    api: APIConfig
    embedding: EmbeddingConfig
    paths: PathConfig
    rag: RAGConfig
    llm: LLMConfig
    web: WebConfig
    language: str

    @classmethod
    def from_env(cls) -> "AppConfig":
        """
        Create complete application configuration from environment variables.

        Returns:
                AppConfig: Fully initialized and validated configuration

        Raises:
                ValueError: If any configuration is invalid
        """
        api_config = APIConfig.from_env()
        api_config.validate()

        embedding_config = EmbeddingConfig.from_env()
        embedding_config.validate()

        paths_config = PathConfig.from_env()
        paths_config.ensure_directories()

        return cls(
            api=api_config,
            embedding=embedding_config,
            paths=paths_config,
            rag=RAGConfig.default(),
            llm=LLMConfig.default(),
            web=WebConfig.from_env(),
            language=os.getenv("LANGUAGE", "en"),
        )

    def print_summary(self) -> None:
        """Print a summary of the current configuration"""
        print("\n" + "=" * 80)
        print("Configuration Summary")
        print("=" * 80)
        print(f"API Provider: {self.api.provider.upper()}")
        print(f"Embedding Provider: {self.embedding.provider.upper()}")
        print(f"LLM Model: {self.get_model_name()}")
        print(f"Project Path: {self.paths.project_path}")
        print(f"Docs Path: {self.paths.docs_path}")
        print(f"Lore Path: {self.paths.lore_path}")
        print(f"Database Path: {self.paths.db_path}")
        print(
            f"RAG Settings: chunk_size={self.rag.chunk_size}, k={self.rag.retrieval_k}"
        )
        print("=" * 80 + "\n")

    def get_model_name(self) -> str:
        """Get the active model name based on API provider"""
        if self.api.provider == "anthropic":
            return self.llm.anthropic_model
        else:
            return self.llm.openai_model


# Convenience function for quick access
def load_config() -> AppConfig:
    """
    Load and validate application configuration.

    Returns:
            AppConfig: Validated application configuration

    Raises:
            ValueError: If configuration is invalid
    """
    return AppConfig.from_env()


# Example usage demonstration
if __name__ == "__main__":
    try:
        config = load_config()
        config.print_summary()
        print("✓ Configuration loaded successfully!")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")

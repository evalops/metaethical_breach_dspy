"""
Configuration management for the Metaethical Breach experiment.

This module encapsulates all tunable parameters in a dataclass and
provides a helper to configure the DSPy runtime accordingly.  It
mirrors the configuration approach of Folie à Deux【327039458444812†L384-L404】
while adapting to the needs of safety guardrail evaluation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExperimentConfig:
    """Configuration parameters loaded from environment variables."""

    # Model configuration
    model: str = os.getenv("MODEL", "gpt-4o-mini")
    api_base: str = os.getenv("API_BASE", "")
    api_key: str = os.getenv("API_KEY", "")
    temperature: float = float(os.getenv("TEMPERATURE", "0.5"))
    max_tokens: int = int(os.getenv("MAX_TOKENS", "512"))

    # Experiment behaviour
    frames_per_item: int = int(os.getenv("FRAMES_PER_ITEM", "3"))
    use_cot: bool = os.getenv("USE_COT", "false").lower() == "true"
    train_rounds: int = int(os.getenv("TRAIN_ROUNDS", "0"))

    # Optimiser settings
    auto_mode: str = os.getenv("AUTO_MODE", "light")
    enable_cache: bool = os.getenv("ENABLE_CACHE", "false").lower() == "true"

    def validate(self) -> None:
        """Validate configuration values and log any errors."""
        if self.frames_per_item < 1:
            raise ValueError("frames_per_item must be >= 1")
        if self.train_rounds < 0:
            raise ValueError("train_rounds must be >= 0")
        if self.temperature < 0:
            raise ValueError("temperature must be non‑negative")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be positive")
        logger.debug("Configuration validated: %s", self)

    def setup_dspy(self) -> None:
        """Configure the DSPy runtime with the selected LLM parameters."""
        try:
            import dspy
        except ImportError as exc:
            raise RuntimeError(
                "dspy is required to run the experiment. Please install dspy-ai"
            ) from exc

        lm = dspy.LM(
            self.model,
            api_base=self.api_base or None,
            api_key=self.api_key or None,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout_s=60,  # Add timeout to prevent hanging
        )
        dspy.configure(lm=lm)
        if self.enable_cache:
            dspy.configure_cache(enable_disk_cache=True, enable_memory_cache=True)
        logger.info(
            "DSPy configured with model=%s, api_base=%s, temperature=%.2f, max_tokens=%d",
            self.model,
            self.api_base or "<default>",
            self.temperature,
            self.max_tokens,
        )


@dataclass
class ModelConfig:
    """Configuration for a single model in multi-model testing."""
    name: str
    model: str
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.5
    max_tokens: int = 512
    family: str = "unknown"  # e.g., "openai", "anthropic", "ollama", "local"
    description: str = ""
    timeout_s: int = 60


@dataclass
class MultiModelConfig:
    """Configuration for multi-model comparison experiments."""

    # Base experiment settings
    frames_per_item: int = int(os.getenv("FRAMES_PER_ITEM", "3"))
    train_rounds: int = int(os.getenv("TRAIN_ROUNDS", "0"))
    use_cot: bool = os.getenv("USE_COT", "false").lower() == "true"

    # Multi-model specific settings
    models: List[ModelConfig] = field(default_factory=list)
    judge_models: List[ModelConfig] = field(default_factory=list)
    parallel_execution: bool = False  # Run models in parallel vs sequentially
    comparison_metrics: List[str] = field(default_factory=lambda: [
        "breach_rate", "vulnerability_score", "consistency", "response_quality"
    ])

    # Statistical settings
    confidence_level: float = 0.95
    min_sample_size_warning: bool = True
    require_power_analysis: bool = True

    def validate(self) -> None:
        """Validate multi-model configuration."""
        if not self.models:
            raise ValueError("At least one model must be configured for testing")

        if not self.judge_models:
            logger.warning("No judge models specified, using first test model as judge")

        for model in self.models + self.judge_models:
            if not model.name or not model.model:
                raise ValueError(f"Model must have both name and model specified: {model}")

        if self.frames_per_item < 1:
            raise ValueError("frames_per_item must be >= 1")

        if self.confidence_level <= 0 or self.confidence_level >= 1:
            raise ValueError("confidence_level must be between 0 and 1")

        logger.debug("Multi-model configuration validated")


# Predefined model configurations for common setups
COMMON_MODEL_CONFIGS = {
    "openai_gpt4o": ModelConfig(
        name="GPT-4o",
        model="gpt-4o",
        family="openai",
        description="OpenAI GPT-4o - latest flagship model"
    ),
    "openai_gpt4o_mini": ModelConfig(
        name="GPT-4o-mini",
        model="gpt-4o-mini",
        family="openai",
        description="OpenAI GPT-4o-mini - cost-effective model"
    ),
    "anthropic_claude_3_5_sonnet": ModelConfig(
        name="Claude-3.5-Sonnet",
        model="anthropic/claude-3-5-sonnet-20241022",
        family="anthropic",
        description="Anthropic Claude 3.5 Sonnet"
    ),
    "anthropic_claude_3_haiku": ModelConfig(
        name="Claude-3-Haiku",
        model="anthropic/claude-3-haiku-20240307",
        family="anthropic",
        description="Anthropic Claude 3 Haiku - fast and efficient"
    ),
    "ollama_dolphin_mistral": ModelConfig(
        name="Dolphin-Mistral-7B",
        model="ollama_chat/dolphin-mistral:7b-v2.6-q4_K_M",
        api_base="http://localhost:11434",
        family="ollama",
        description="Uncensored Dolphin-Mistral model via Ollama"
    ),
    "ollama_llama3_1_8b": ModelConfig(
        name="Llama-3.1-8B",
        model="ollama_chat/llama3.1:8b",
        api_base="http://localhost:11434",
        family="ollama",
        description="Meta Llama 3.1 8B via Ollama"
    ),
    "ollama_qwen2_5_7b": ModelConfig(
        name="Qwen2.5-7B",
        model="ollama_chat/qwen2.5:7b",
        api_base="http://localhost:11434",
        family="ollama",
        description="Alibaba Qwen 2.5 7B via Ollama"
    )
}

# Robust judge model configurations (tested for low vulnerability)
ROBUST_JUDGE_CONFIGS = {
    "gpt4o_mini_judge": ModelConfig(
        name="GPT-4o-mini-Judge",
        model="gpt-4o-mini",
        family="openai",
        temperature=0.1,  # Lower temperature for more consistent judging
        description="GPT-4o-mini configured for robust judging"
    ),
    "gpt4o_judge": ModelConfig(
        name="GPT-4o-Judge",
        model="gpt-4o",
        family="openai",
        temperature=0.1,
        description="GPT-4o configured for robust judging"
    ),
    "claude_3_5_sonnet_judge": ModelConfig(
        name="Claude-3.5-Sonnet-Judge",
        model="anthropic/claude-3-5-sonnet-20241022",
        family="anthropic",
        temperature=0.1,
        description="Claude 3.5 Sonnet configured for robust judging"
    )
}


def create_multimodel_config_from_env() -> MultiModelConfig:
    """Create multi-model configuration from environment variables.

    Environment variables:
    - TEST_MODELS: comma-separated list of model config names
    - JUDGE_MODELS: comma-separated list of judge config names
    - PARALLEL_EXECUTION: true/false
    """
    config = MultiModelConfig()

    # Parse test models from environment
    test_models_env = os.getenv("TEST_MODELS", "")
    if test_models_env:
        model_names = [name.strip() for name in test_models_env.split(",")]
        for model_name in model_names:
            if model_name in COMMON_MODEL_CONFIGS:
                model_config = COMMON_MODEL_CONFIGS[model_name]
                # Override with environment-specific settings
                if model_config.family == "openai":
                    model_config.api_key = os.getenv("OPENAI_API_KEY", "")
                elif model_config.family == "anthropic":
                    model_config.api_key = os.getenv("ANTHROPIC_API_KEY", "")
                config.models.append(model_config)
            else:
                logger.warning(f"Unknown model config: {model_name}")

    # Parse judge models from environment
    judge_models_env = os.getenv("JUDGE_MODELS", "gpt4o_mini_judge")
    if judge_models_env:
        judge_names = [name.strip() for name in judge_models_env.split(",")]
        for judge_name in judge_names:
            if judge_name in ROBUST_JUDGE_CONFIGS:
                judge_config = ROBUST_JUDGE_CONFIGS[judge_name]
                # Override with environment-specific settings
                if judge_config.family == "openai":
                    judge_config.api_key = os.getenv("OPENAI_API_KEY", "")
                elif judge_config.family == "anthropic":
                    judge_config.api_key = os.getenv("ANTHROPIC_API_KEY", "")
                config.judge_models.append(judge_config)
            else:
                logger.warning(f"Unknown judge config: {judge_name}")

    # Parse other settings
    config.parallel_execution = os.getenv("PARALLEL_EXECUTION", "false").lower() == "true"

    return config


def setup_dspy_for_model(model_config: ModelConfig) -> None:
    """Configure DSPy for a specific model configuration."""
    try:
        import dspy
    except ImportError as exc:
        raise RuntimeError("dspy is required to run experiments") from exc

    lm = dspy.LM(
        model_config.model,
        api_base=model_config.api_base,
        api_key=model_config.api_key,
        temperature=model_config.temperature,
        max_tokens=model_config.max_tokens,
        timeout_s=model_config.timeout_s,
    )
    dspy.configure(lm=lm)

    logger.info(
        "DSPy configured for %s (%s): model=%s, family=%s",
        model_config.name,
        model_config.description,
        model_config.model,
        model_config.family
    )
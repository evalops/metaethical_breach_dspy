"""
Configuration management for the Metaethical Breach experiment.

This module encapsulates all tunable parameters in a dataclass and
provides a helper to configure the DSPy runtime accordingly.  It
mirrors the configuration approach of Folie à Deux【327039458444812†L384-L404】
while adapting to the needs of safety guardrail evaluation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
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
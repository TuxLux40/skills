"""Prompt file loading helpers."""

from app.constants import (
    DEFAULT_EXTRACTION_PROMPT,
    DEFAULT_FACT_VERIFICATION_PROMPT,
    DEFAULT_FOLDER_SUMMARY_PROMPT,
    DEFAULT_SYNTHESIS_MATTER_PROMPT,
    DEFAULT_SYNTHESIS_OVERVIEW_PROMPT,
    DEFAULT_VISION_EXTRACTION_PROMPT,
    EXTRACTION_PROMPT_FILE,
    FACT_VERIFICATION_PROMPT_FILE,
    FOLDER_SUMMARY_PROMPT_FILE,
    PROMPTS_DIR,
    SYNTHESIS_MATTER_PROMPT_FILE,
    SYNTHESIS_OVERVIEW_PROMPT_FILE,
    VISION_EXTRACTION_PROMPT_FILE,
)


def load_prompt(filename: str, fallback: str = "") -> str:
    """Load a prompt markdown file from the prompts directory."""
    prompt_path = PROMPTS_DIR / filename
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return fallback


def load_extraction_prompt() -> str:
    """Load the system prompt used for OKF extraction."""
    return load_prompt(EXTRACTION_PROMPT_FILE, fallback=DEFAULT_EXTRACTION_PROMPT)


def load_folder_summary_prompt() -> str:
    """Load the system prompt used to synthesize a folder aggregate's top summary."""
    return load_prompt(FOLDER_SUMMARY_PROMPT_FILE, fallback=DEFAULT_FOLDER_SUMMARY_PROMPT)


def load_vision_extraction_prompt() -> str:
    """Load the system prompt used to transcribe + describe images via a vision-capable model."""
    return load_prompt(VISION_EXTRACTION_PROMPT_FILE, fallback=DEFAULT_VISION_EXTRACTION_PROMPT)


def load_synthesis_overview_prompt() -> str:
    """Load the system prompt used by the synthesis pass to synthesize across folder aggregates."""
    return load_prompt(SYNTHESIS_OVERVIEW_PROMPT_FILE, fallback=DEFAULT_SYNTHESIS_OVERVIEW_PROMPT)


def load_synthesis_matter_prompt() -> str:
    """Load the system prompt used to deep-dive one candidate cross-folder matter."""
    return load_prompt(SYNTHESIS_MATTER_PROMPT_FILE, fallback=DEFAULT_SYNTHESIS_MATTER_PROMPT)


def load_fact_verification_prompt() -> str:
    """Load the system prompt used to verify one extraction against its source text."""
    return load_prompt(FACT_VERIFICATION_PROMPT_FILE, fallback=DEFAULT_FACT_VERIFICATION_PROMPT)

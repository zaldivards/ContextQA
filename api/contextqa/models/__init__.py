from typing import TypedDict, Literal


class SettingsSchema(TypedDict):
    """Dict schema returned from the config manager"""

    platform: Literal["openai", "huggingface"]
    model: str
    temperature: float
    local: bool

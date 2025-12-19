class BaseModelProvider:
    """Minimal interface for model providers used by skills."""

    def chat(self, model: str, messages: list[dict], *, options: dict | None = None) -> dict:
        raise NotImplementedError


class OllamaProvider(BaseModelProvider):
    """Default local provider using Ollama. Safe to import if available."""

    def __init__(self):
        try:
            import ollama  # type: ignore
        except Exception:  # pragma: no cover
            self.ollama = None
        else:
            self.ollama = ollama

    def chat(self, model: str, messages: list[dict], *, options: dict | None = None) -> dict:
        if self.ollama is None:
            raise RuntimeError("Ollama provider is unavailable")
        opts = options or {}
        return self.ollama.chat(model=model, messages=messages, options=opts)

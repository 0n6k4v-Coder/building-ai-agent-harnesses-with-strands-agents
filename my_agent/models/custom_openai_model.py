from strands.models.openai import OpenAIModel
from strands.types.exceptions import ContextWindowOverflowException

_OVERFLOW_KEYWORDS = (
    "16384",
    "context_length",
    "context length",
    "maximum context",
    "too many tokens",
    "context window",
)

class CustomOpenAIModel(OpenAIModel):
    async def stream(self, *args, **kwargs):
        try:
            async for event in super().stream(*args, **kwargs):
                yield event
        except ContextWindowOverflowException:
            raise
        except Exception as e:
            msg = str(e).lower()
            if any(keyword in msg for keyword in _OVERFLOW_KEYWORDS):
                raise ContextWindowOverflowException(str(e)) from e
            raise
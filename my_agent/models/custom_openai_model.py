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
    def _sanitize_messages(self, messages):
        if not isinstance(messages, list):
            return messages

        sanitized = []
        for msg in messages:
            if isinstance(msg, dict):
                clean_msg = {}
                for k, v in msg.items():
                    if k in ["reasoningContent", "reasoning_content"]:
                        continue
                    
                    if k == "content" and isinstance(v, list):
                        new_v = []
                        for item in v:
                            if isinstance(item, dict) and "reasoningContent" not in item and "reasoning_content" not in item:
                                new_v.append(item)
                            elif isinstance(item, str):
                                new_v.append(item)
                        clean_msg[k] = new_v
                    else:
                        clean_msg[k] = v
                sanitized.append(clean_msg)
            else:
                sanitized.append(msg)
        return sanitized

    async def stream(self, *args, **kwargs):
        if args and isinstance(args[0], list):
            args = (self._sanitize_messages(args[0]),) + args[1:]
            
        if "messages" in kwargs:
            kwargs["messages"] = self._sanitize_messages(kwargs["messages"])
            
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
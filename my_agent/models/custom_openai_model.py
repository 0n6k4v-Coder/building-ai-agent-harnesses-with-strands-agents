# my_agent/models/custom_openai_model.py
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
        """
        ลบ reasoningContent ออกจากประวัติการแชทก่อนส่งกลับไปที่ API
        ทั้งในระดับ Key หลัก และในระดับ List ของ Content
        """
        if not isinstance(messages, list):
            return messages

        sanitized = []
        for msg in messages:
            if isinstance(msg, dict):
                clean_msg = {}
                for k, v in msg.items():
                    # 1. ตัด key ที่ API ไม่รองรับทิ้งไปเลย
                    if k in ["reasoningContent", "reasoning_content"]:
                        continue
                    
                    # 2. ตัด reasoningContent ที่ซ่อนอยู่ใน List ของ Content (สำหรับโมเดลบางตัว)
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
        # 🛑 ดักจับและทำความสะอาด messages ทั้งใน args และ kwargs
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
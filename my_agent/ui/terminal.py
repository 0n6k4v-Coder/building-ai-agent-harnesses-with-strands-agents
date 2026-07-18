import io
import sys
import re

def render_terminal_markdown(text: str) -> str:
    """ฟังก์ชันเรนเดอร์ Markdown พื้นฐาน สำหรับใช้คลีนข้อความ"""
    text = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', text)
    text = re.sub(r'\*(.*?)\*', r'\033[4m\1\033[0m', text)
    text = re.sub(r'`(.*?)`', r'\033[36m\1\033[0m', text)
    return text

class RealTimeStateStreamer(io.TextIOBase):
    """Custom Stream Wrapper คอยดักสตรีมจาก stdout ของ Strands แล้วแยกแยะ State สด ๆ"""
    def __init__(self):
        self.buffer = ""
        self.in_think_block = False
        self.think_header_printed = False
        self.ai_header_printed = False
        self.clean_response_accumulated = ""
        self.actual_tool_logs = []

    def write(self, s):
        if not s:
            return len(s)
        
        self.buffer += s

        # 🛠️ ตรวจจับ Log การทำงานของเครื่องมือ (Tool Execution Logs)
        if "Calling tool" in s or "Tool returned" in s or ("[" in s and "Tool" in s):
            if not self.in_think_block and not self.ai_header_printed:
                if not any("🛠️ [Tools Call State]" in line for line in self.actual_tool_logs):
                    sys.__stdout__.write(f"\n\033[1;33m🛠️ [Tools Call State]\033[0m\n")
                sys.__stdout__.write(f"\033[90m{s}\033[0m")
                sys.__stdout__.flush()
                self.actual_tool_logs.append(s)
                return len(s)

        # 🧠 ตรวจจับการเริ่มเปิดแท็ก <think> แบบเรียลไทม์
        if "<think>" in self.buffer and not self.in_think_block:
            self.in_think_block = True
            if not self.think_header_printed:
                sys.__stdout__.write(f"\n\033[1;30m🧠 [Thinking State]\033[0m\n")
                sys.__stdout__.flush()
                self.think_header_printed = True
            self.buffer = self.buffer.replace("<think>", "")

        # 🛑 ตรวจจับการปิดแท็ก </think> แบบเรียลไทม์
        if "</think>" in self.buffer and self.in_think_block:
            parts = self.buffer.split("</think>")
            if parts[0]:
                sys.__stdout__.write(f"\033[90m{parts[0]}\033[0m")
            
            sys.__stdout__.write(f"\033[0m\n\033[90m" + "—" * 50 + "\033[0m\n")
            sys.__stdout__.flush()
            
            self.in_think_block = False
            self.buffer = parts[1] if len(parts) > 1 else ""

        # 📺 พ่นข้อความทีละ Token ตามสถานะจริง
        if self.in_think_block:
            if self.buffer and not any(tag in self.buffer for tag in ["<", "</", "</t", "</th"]):
                sys.__stdout__.write(f"\033[90m{self.buffer}\033[0m")
                sys.__stdout__.flush()
                self.buffer = ""
        else:
            # สตรีมข้อความคำตอบสุดท้ายของ AI
            if self.buffer and not any(tag in self.buffer for tag in ["<", "</", "</t", "</th"]):
                if not self.ai_header_printed:
                    sys.__stdout__.write(f"\n\033[1;95m🤖 AI > \033[0m")
                    sys.__stdout__.flush()
                    self.ai_header_printed = True
                
                self.clean_response_accumulated += self.buffer
                
                chunk = self.buffer
                chunk = re.sub(r'`(.*?)`', r'\033[36m\1\033[0m', chunk)
                
                sys.__stdout__.write(chunk)
                sys.__stdout__.flush()
                self.buffer = ""

        return len(s)

    def flush(self):
        sys.__stdout__.flush()
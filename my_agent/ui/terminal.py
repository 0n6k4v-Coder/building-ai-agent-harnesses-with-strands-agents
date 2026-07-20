import sys
import re
import json

class RealTimeStateStreamer:
    def __init__(self):
        self.buffer = ""
        self.in_think_block = False
        self.think_header_printed = False
        self.ai_header_printed = False
        self.last_tool_name = None

    def __call__(self, **kwargs):
        reasoning_text = kwargs.get("reasoningText")
        data = kwargs.get("data", "")
        complete = kwargs.get("complete", False)
        current_tool_use = kwargs.get("current_tool_use") or {}

        tool_name = current_tool_use.get("name")
        tool_input = current_tool_use.get("input")

        if tool_name and tool_name != self.last_tool_name:
            self.last_tool_name = tool_name
            self._reset_headers()
            sys.stdout.write(f"\n\033[1;33m🛠️ [Tools Call State] {tool_name}\033[0m\n")

            if tool_input is not None:
                try:
                    input_str = json.dumps(tool_input, ensure_ascii=False, indent=2)
                    sys.stdout.write(f"\033[90m{input_str}\033[0m\n")
                except Exception:
                    sys.stdout.write(f"\033[90m{str(tool_input)}\033[0m\n")
            
            sys.stdout.flush()

        if reasoning_text:
            self._emit_think(reasoning_text)

        if data:
            self._process_stream_chunk(data)

        if complete:
            if self.ai_header_printed or self.think_header_printed:
                sys.stdout.write("\n")
            sys.stdout.flush()
            self._reset_headers()
            self.last_tool_name = None

    def _reset_headers(self):
        self.think_header_printed = False
        self.ai_header_printed = False

    def _emit_think(self, text):
        if not text:
            return
        
        if self.ai_header_printed:
            self.ai_header_printed = False
            
        if not self.think_header_printed:
            sys.stdout.write("\n\033[1;30m🧠 [Thinking State]\033[0m\n")
            self.think_header_printed = True
            
        sys.stdout.write(f"\033[90m{text}\033[0m")
        sys.stdout.flush()

    def _emit_answer(self, text):
        if not text or text.isspace():
            return
            
        if not self.ai_header_printed:
            text = text.lstrip()
            if not text:
                return
            
        if self.think_header_printed:
            self.think_header_printed = False
            
        if not self.ai_header_printed:
            sys.stdout.write("\n\033[1;95m🤖 AI > \033[0m")
            self.ai_header_printed = True
            
        chunk = text
        chunk = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', chunk)
        chunk = re.sub(r'`(.*?)`', r'\033[36m\1\033[0m', chunk)
        
        sys.stdout.write(chunk)
        sys.stdout.flush()

    def _process_stream_chunk(self, chunk):
        self.buffer += chunk

        while True:
            if not self.in_think_block:
                start = self.buffer.find("<think>")
                if start == -1:
                    safe_len = self._safe_flush_length(self.buffer, "<think>")
                    if safe_len:
                        self._emit_answer(self.buffer[:safe_len])
                        self.buffer = self.buffer[safe_len:]
                    return
                if start > 0:
                    self._emit_answer(self.buffer[:start])
                self.buffer = self.buffer[start + len("<think>"):]
                self.in_think_block = True
            else:
                end = self.buffer.find("</think>")
                if end == -1:
                    safe_len = self._safe_flush_length(self.buffer, "</think>")
                    if safe_len:
                        self._emit_think(self.buffer[:safe_len])
                        self.buffer = self.buffer[safe_len:]
                    return
                self._emit_think(self.buffer[:end])
                self.buffer = self.buffer[end + len("</think>"):]
                self.in_think_block = False
                self.think_header_printed = False

    @staticmethod
    def _safe_flush_length(buf: str, tag: str) -> int:
        max_keep = len(tag) - 1
        for i in range(min(max_keep, len(buf)), 0, -1):
            if tag.startswith(buf[-i:]):
                return len(buf) - i
        return len(buf)
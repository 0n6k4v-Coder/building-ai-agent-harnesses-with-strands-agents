import re
import shutil
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

COMMANDS = ["/clear", "/exit", "/paste", "/continue", "/model"]

# สร้างฟังก์ชันสำหรับจัดรูปแบบให้เต็มหน้าจอ (เหมือน Slash Command ปกติ)
def _get_full_width_display(text: str) -> str:
    terminal_width = shutil.get_terminal_size().columns
    indent_spaces = 6
    padding_length = max(0, terminal_width - len(text) - indent_spaces - 5)
    return f"{' ' * indent_spaces}{text}{' ' * padding_length}"

class SlashCommandCompleter(Completer):
    def __init__(self, provider_manager=None):
        self.provider_manager = provider_manager

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        if text in COMMANDS:
            return

        if text.startswith("/model") and self.provider_manager:
            yield from self._get_model_completions(document, text)
            return

        if text.startswith("/"):
            for cmd in COMMANDS:
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text), display=_get_full_width_display(cmd))

    def _get_model_completions(self, document, text):
        parts = text.split()
        
        # State 1: พิมพ์ /model ยังไม่มีวรรค
        if len(parts) == 1 and not text.endswith(" "):
            yield Completion("/model ", start_position=-len(text), display=_get_full_width_display("/model "))
            return

        # State 2: พิมพ์ /model แล้วมีวรรค (กำลังเลือก Provider)
        if len(parts) == 1 and text.endswith(" "):
            providers = self.provider_manager.list_all_providers()
            for p in providers:
                yield Completion(f"/{p} ", start_position=0, display=_get_full_width_display(f"/{p}"))
            yield Completion("/cancel ", start_position=0, display=_get_full_width_display("/cancel"))
            return

        # State 3: พิมพ์ /model /provider... (กำลังพิมพ์ชื่อ Provider)
        if len(parts) == 2 and not text.endswith(" "):
            provider_text = parts[1]
            
            if "/cancel".startswith(provider_text):
                yield Completion("/cancel ", start_position=-len(provider_text), display=_get_full_width_display("/cancel"))
                return

            providers = self.provider_manager.list_all_providers()
            matched_providers = [p for p in providers if f"/{p}".startswith(provider_text)]
            
            for p in matched_providers:
                yield Completion(f"/{p} ", start_position=-len(provider_text), display=_get_full_width_display(f"/{p}"))
            return

        # State 4: พิมพ์ /model /provider แล้วมีวรรค (กำลังเลือก Model)
        if len(parts) == 2 and text.endswith(" "):
            provider_name = parts[1].lstrip("/")
            
            if provider_name == "cancel":
                return

            models = self.provider_manager.fetch_available_models(provider_name)
            replace_len = len(parts[1]) + 1
            for m in models:
                yield Completion(f"/{provider_name}/{m}", start_position=-replace_len, display=_get_full_width_display(f"/{provider_name}/{m}"))
            yield Completion("/back", start_position=-replace_len, display=_get_full_width_display("/back"))
            return

        # State 5: พิมพ์ /model /provider /model... (กำลังพิมพ์ชื่อ Model)
        if len(parts) >= 3:
            provider_name = parts[1].lstrip("/")
            models = self.provider_manager.fetch_available_models(provider_name)
            
            model_text = parts[2]
            replace_len = len(model_text) + 1
            matched_models = [m for m in models if m.startswith(model_text.lstrip("/"))]
            
            for m in matched_models:
                yield Completion(f"/{m}", start_position=-replace_len, display=_get_full_width_display(f"/{provider_name}/{m}"))
            return

def create_cli_session(provider_manager=None) -> PromptSession:
    command_completer = SlashCommandCompleter(provider_manager)
    kb = KeyBindings()

    @kb.add("enter", eager=True)
    def _(event):
        buffer = event.app.current_buffer
        text = buffer.text
        
        # 1. ถ้ากำลังเปิดเมนูอยู่ ให้เลือกของที่ไฮไลต์
        if buffer.complete_state:
            buffer.apply_completion(buffer.complete_state.current_completion)
            event.app.invalidate()
            
            new_text = buffer.text
            if new_text.startswith("/model /") and new_text.endswith(" "):
                buffer.start_completion(select_first=True)
            return
            
        # 2. ถ้าพิมพ์ /model (ยังไม่มีวรรค) แล้วกด Enter ให้แทรกวรรคและเปิดเมนู Provider
        if text.strip() == "/model":
            buffer.insert_text(" ")
            buffer.start_completion(select_first=True)
            event.app.invalidate()
            return
            
        # 3. ถ้าพิมพ์ /model /provider (ยังไม่มีวรรคด้านหลัง) แล้วกด Enter ให้แทรกวรรคและเปิดเมนู Model
        if text.strip().startswith("/model /") and not text.endswith(" "):
            parts = text.strip().split()
            if len(parts) == 2 and parts[1].count("/") == 1 and parts[1] not in ["/back", "/cancel"]:
                buffer.insert_text(" ")
                buffer.start_completion(select_first=True)
                event.app.invalidate()
                return

        # 4. ปกติ: ส่งข้อความเข้าระบบ
        buffer.validate_and_handle()

    @kb.add("tab")
    def _(event):
        buffer = event.app.current_buffer
        if buffer.complete_state:
            buffer.apply_completion(buffer.complete_state.completions[0])
            buffer.cancel_completion()
        else:
            buffer.start_completion(select_first=False)

    @kb.add("up")
    def _(event):
        buffer = event.app.current_buffer
        if buffer.complete_state:
            buffer.complete_previous()
        else:
            buffer.auto_up()

    @kb.add("down")
    def _(event):
        buffer = event.app.current_buffer
        if buffer.complete_state:
            buffer.complete_next()
        else:
            buffer.auto_down()

    @kb.add("backspace")
    def _(event):
        buffer = event.app.current_buffer
        buffer.delete_before_cursor(1)
        text = buffer.text
        if text.startswith("/") and text not in COMMANDS:
            buffer.start_completion(select_first=False)
        else:
            buffer.cancel_completion()

    style = Style.from_dict({
        'completion-menu': 'bg:default',
        'completion-menu.completion': 'bg:default fg:#888888',
        'completion-menu.completion.current': 'bg:ansigray fg:ansiwhite',
    })

    return PromptSession(
        completer=command_completer, 
        complete_while_typing=True,
        key_bindings=kb,
        style=style
    )

def get_user_input(session: PromptSession) -> str:
    first_line = session.prompt(HTML('<ansicyan>👤 You > </ansicyan>')).strip()

    if first_line.lower() == "/paste":
        print("\033[90m(โหมด paste: พิมพ์/วางข้อความหลายบรรทัด แล้วปิดท้ายด้วยบรรทัดที่มีแค่ /end)\033[0m")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip().lower() == "/end":
                break
            lines.append(line)
        return "\n".join(lines).strip()

    return first_line
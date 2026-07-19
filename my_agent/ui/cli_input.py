# my_agent/ui/cli_input.py
import shutil
from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

COMMANDS = ["/clear", "/exit", "/paste", "/continue"]

PROMPT_WIDTH = 9 

class SlashCommandCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        if text in COMMANDS:
            return
            
        if text.startswith("/"):
            terminal_width = shutil.get_terminal_size().columns
            
            for cmd in COMMANDS:
                if cmd.startswith(text):
                    padding_length = max(0, terminal_width - PROMPT_WIDTH - len(cmd) - 2)
                    padded_cmd = f"{cmd}{' ' * padding_length}"
                    
                    yield Completion(cmd, start_position=-len(text), display=padded_cmd)

def create_cli_session() -> PromptSession:
    command_completer = SlashCommandCompleter()
    kb = KeyBindings()

    @kb.add("tab")
    def _(event):
        buffer = event.app.current_buffer
        if buffer.complete_state:
            buffer.apply_completion(buffer.complete_state.completions[0])
            buffer.cancel_completion()
        else:
            buffer.start_completion(select_first=False)

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
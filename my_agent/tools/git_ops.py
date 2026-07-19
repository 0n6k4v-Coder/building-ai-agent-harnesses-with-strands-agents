import os
import shlex
import subprocess
from strands import tool

WORKSPACE_ROOT = os.path.abspath(os.getcwd())

_ALLOWED_SUBCOMMANDS = {
    "status", "diff", "log", "add", "commit", "show",
    "branch", "stash", "restore", "reset --soft", "reset --mixed",
    "rev-parse", "ls-files", "config --get",
}

@tool
def git(command: str) -> str:
    try:
        args = shlex.split(command)
        
        if not args or args[0] != "git":
            return "Error: command must start with 'git'"

        sub_args = args[1:]
        sub = " ".join(sub_args[:2]) if len(sub_args) >= 2 else " ".join(sub_args)

        is_allowed = False
        for allowed in _ALLOWED_SUBCOMMANDS:
            if sub == allowed or sub.startswith(allowed + " ") or sub.startswith(allowed):
                is_allowed = True
                break
        
        if not is_allowed:
            return (
                f"Error: git subcommand '{sub}' is not allowed. "
                f"Allowed: {sorted(_ALLOWED_SUBCOMMANDS)}"
            )

        result = subprocess.run(
            args,
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        out = result.stdout.strip()
        err = result.stderr.strip()
        
        if result.returncode != 0:
            return (
                f"git exited with code {result.returncode}\n"
                f"STDERR:\n{err}\n"
                f"STDOUT:\n{out}"
            )
        return out or err or "(no output)"

    except subprocess.TimeoutExpired:
        return "Error: git command timed out after 30s"
    except Exception as e:
        return f"Error running git: {e}"
import os
from strands import tool

WORKSPACE_ROOT = os.path.abspath(os.getcwd())

def _safe_path(relative_path: str) -> str:
    safe_path = os.path.abspath(os.path.join(WORKSPACE_ROOT, relative_path))
    if not safe_path.startswith(WORKSPACE_ROOT):
        raise PermissionError("Access denied: Operation not allowed outside the workspace directory.")
    return safe_path

@tool
def list_dir(path: str = ".") -> str:
    try:
        target = _safe_path(path)
        if not os.path.exists(target):
            return f"Error: The path '{path}' does not exist."

        items = os.listdir(target)
        if not items:
            return f"The directory '{path}' is currently empty."

        result = []
        for item in items:
            item_path = os.path.join(target, item)
            prefix = "📁 " if os.path.isdir(item_path) else "📄 "
            result.append(f"{prefix}{item}")

        return "\n".join(result)
    except Exception as e:
        return f"Error listing directory content: {str(e)}"

@tool
def read_file(path: str) -> str:
    try:
        target = _safe_path(path)
        if not os.path.isfile(target):
            return f"Error: '{path}' is not a valid file or does not exist."

        with open(target, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file content: {str(e)}"

@tool
def write_file(path: str, content: str) -> str:
    try:
        target = _safe_path(path)

        dir_name = os.path.dirname(target)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)

        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Success: Content written to file '{path}' successfully."
    except Exception as e:
        return f"Error writing content to file: {str(e)}"

@tool
def edit_file_patch(path: str, search_text: str, replace_text: str) -> str:
    try:
        target = _safe_path(path)
        if not os.path.isfile(target):
            return f"Error: Target file '{path}' does not exist."

        with open(target, 'r', encoding='utf-8') as f:
            file_content = f.read()

        if search_text not in file_content:
            return (
                f"Error: Could not find the exact text block to replace in '{path}'. "
                f"Please ensure your 'search_text' matches the target block exactly "
                f"(including tabs, spaces, and newlines)."
            )

        updated_content = file_content.replace(search_text, replace_text, 1)

        with open(target, 'w', encoding='utf-8') as f:
            f.write(updated_content)

        return f"Success: File '{path}' modified successfully via search-and-replace patch."
    except Exception as e:
        return f"Error patching file: {str(e)}"
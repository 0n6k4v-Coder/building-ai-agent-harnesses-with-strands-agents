import os
from strands import tool

class FileTools:
    def __init__(self, workspace_root: str):
        self.workspace_root = os.path.abspath(workspace_root)

    def _safe_path(self, relative_path: str) -> str:
        if os.path.isabs(relative_path):
            pass 
            
        safe_path = os.path.abspath(os.path.join(self.workspace_root, relative_path))

        if os.path.commonpath([safe_path, self.workspace_root]) != self.workspace_root:
            raise PermissionError("Access denied: Operation not allowed outside the workspace directory.")
            
        return safe_path

    @tool(
        name="list_dir",
        description="Lists the contents of a specified directory in the workspace. Use this to inspect files and folders before assuming code layout."
    )
    def list_dir(self, path: str = ".") -> str:
        try:
            target = self._safe_path(path)
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
        except PermissionError as pe:
            return f"Security Error: {str(pe)}"
        except Exception as e:
            return f"Error listing directory content: {str(e)}"

    @tool(
        name="read_file",
        description="Reads the complete content of a specified file in the workspace. Use this to inspect source code or text files."
    )
    def read_file(self, path: str) -> str:
        try:
            target = self._safe_path(path)
            if not os.path.isfile(target):
                return f"Error: '{path}' is not a valid file or does not exist."

            with open(target, 'r', encoding='utf-8') as f:
                return f.read()
        except PermissionError as pe:
            return f"Security Error: {str(pe)}"
        except Exception as e:
            return f"Error reading file content: {str(e)}"

    @tool(
        name="write_file",
        description="Creates a new file or completely overwrites an existing file with the provided content. Use this for creating new files. For modifying existing code, prefer 'edit_file_patch'."
    )
    def write_file(self, path: str, content: str) -> str:
        try:
            target = self._safe_path(path)

            dir_name = os.path.dirname(target)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            with open(target, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Success: Content written to file '{path}' successfully."
        except PermissionError as pe:
            return f"Security Error: {str(pe)}"
        except Exception as e:
            return f"Error writing content to file: {str(e)}"

    @tool(
        name="edit_file_patch",
        description="Modifies an existing file by replacing a specific exact text block with new text. Always prefer this over 'write_file' for targeted updates. Ensure 'search_text' matches exactly (including tabs and spaces)."
    )
    def edit_file_patch(self, path: str, search_text: str, replace_text: str) -> str:
        try:
            target = self._safe_path(path)
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
        except PermissionError as pe:
            return f"Security Error: {str(pe)}"
        except Exception as e:
            return f"Error patching file: {str(e)}"

WORKSPACE_ROOT = os.path.abspath(os.getcwd())

file_tools_instance = FileTools(WORKSPACE_ROOT)

list_dir = file_tools_instance.list_dir
read_file = file_tools_instance.read_file
write_file = file_tools_instance.write_file
edit_file_patch = file_tools_instance.edit_file_patch
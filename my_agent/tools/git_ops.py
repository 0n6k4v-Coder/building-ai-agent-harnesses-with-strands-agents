import os
import subprocess
from typing import List, Literal
from strands import tool

class GitTools:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root

    @tool(
        name="git_inspector",
        description="Inspects the current state of the local git repository. Use this to check what files have changed or view recent history. This tool is strictly READ-ONLY and cannot modify the repository."
    )
    def inspect_git(
        self,
        command: Literal["status", "diff", "diff --stat", "log", "log --oneline"]
    ) -> str:
        try:
            args = ["git"] + command.split()
            result = subprocess.run(
                args, cwd=self.workspace_root, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                return f"Error: {result.stderr.strip() or result.stdout.strip()}"
            return result.stdout.strip() or "(no output)"
        except Exception as e:
            return f"Error running git: {e}"

    @tool(
        name="git_committer",
        description="Stages specified files and creates a git commit in the repository. Use this tool ONLY when the user explicitly asks you to 'execute', 'run', 'commit it for me', or 'do it'. If the user only asks to 'generate', 'prepare', or 'draft' a commit, DO NOT use this tool. Instead, output the `git add` and `git commit` commands as text blocks for the user to review."
    )
    def commit_git(
        self,
        files: List[str],
        commit_message: str
    ) -> str:
        try:
            add_args = ["git", "add"] + files
            add_result = subprocess.run(
                add_args, cwd=self.workspace_root, capture_output=True, text=True, timeout=30
            )
            if add_result.returncode != 0:
                return f"Failed to stage files: {add_result.stderr.strip()}"

            commit_args = ["git", "commit", "-m", commit_message]
            commit_result = subprocess.run(
                commit_args, cwd=self.workspace_root, capture_output=True, text=True, timeout=30
            )
            
            if commit_result.returncode != 0:
                return f"Failed to commit: {commit_result.stderr.strip()}"
            
            return f"Success!\nSTDOUT:\n{commit_result.stdout.strip()}"
        except Exception as e:
            return f"Error executing git commit: {e}"

WORKSPACE_ROOT = os.path.abspath(os.getcwd())

git_tools_instance = GitTools(WORKSPACE_ROOT)

git_inspector = git_tools_instance.inspect_git
git_committer = git_tools_instance.commit_git
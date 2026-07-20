import os
import subprocess
from typing import List, Literal
from strands import tool

class GitTools:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root

    @tool(
        name="git_status",
        description=(
            "Shows the current state of the git repository (changed files). READ-ONLY.\n"
            "Use this tool when the user wants to: check status, see what files changed.\n"
            "DO NOT use this tool for: staging files, committing, or pushing. "
            "If the user says 'commit' or 'push', this tool CANNOT do that."
        )
    )
    def status(self) -> str:
        try:
            result = subprocess.run(["git", "status"], cwd=self.workspace_root, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
        except Exception as e:
            return f"Error: {e}"

    @tool(
        name="git_diff",
        description=(
            "Shows the changes in files that are not yet committed. READ-ONLY.\n"
            "Use this tool when the user wants to: view code changes, see diffs.\n"
            "DO NOT use this tool for: committing or pushing."
        )
    )
    def diff(self) -> str:
        try:
            result = subprocess.run(["git", "diff"], cwd=self.workspace_root, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
        except Exception as e:
            return f"Error: {e}"

    @tool(
        name="git_log",
        description=(
            "Shows recent commit history. READ-ONLY.\n"
            "Use this tool when the user wants to: view commit log, see history.\n"
            "DO NOT use this tool for: creating new commits or pushing."
        )
    )
    def log(self) -> str:
        try:
            result = subprocess.run(["git", "log", "--oneline", "-5"], cwd=self.workspace_root, capture_output=True, text=True, timeout=30)
            return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr.strip()}"
        except Exception as e:
            return f"Error: {e}"

    @tool(
        name="git_commit",
        description=(
            "Stages specified files and creates a git commit in the repository.\n"
            "Use this tool when the user says 'approve', 'execute', 'run', or 'commit'.\n"
            "The commit_message MUST be a human-readable description of the change. "
            "NEVER pass the user's raw command word (e.g. 'push', 'commit', 'approve') as the commit_message.\n"
            "DO NOT use this tool for pushing to remote — use git_push instead."
        )
    )
    def commit(self, files: List[str], commit_message: str) -> str:
        try:
            add_args = ["git", "add"] + files
            add_result = subprocess.run(add_args, cwd=self.workspace_root, capture_output=True, text=True, timeout=30)
            if add_result.returncode != 0:
                return f"Failed to stage files: {add_result.stderr.strip()}"

            commit_args = ["git", "commit", "-m", commit_message]
            commit_result = subprocess.run(commit_args, cwd=self.workspace_root, capture_output=True, text=True, timeout=30)
            
            if commit_result.returncode != 0:
                return f"Failed to commit: {commit_result.stderr.strip()}"
            
            return f"Success!\nSTDOUT:\n{commit_result.stdout.strip()}"
        except Exception as e:
            return f"Error executing git commit: {e}"

    @tool(
        name="git_push",
        description=(
            "Pushes local commits to a remote repository (e.g., GitHub, GitLab).\n"
            "Use this tool ONLY when the user explicitly asks to 'push' or 'push to remote'.\n"
            "DO NOT use this tool to create commits — use git_commit instead.\n"
            "NEVER tell the user to run git push manually if you have this tool available."
        )
    )
    def push(self, remote: str = "origin", branch: str = "") -> str:
        try:
            args = ["git", "push", remote]
            if branch:
                args.append(branch)
                
            result = subprocess.run(args, cwd=self.workspace_root, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                return f"Failed to push: {result.stderr.strip() or result.stdout.strip()}"
            return f"Success!\nSTDOUT:\n{result.stdout.strip()}" or "Pushed successfully (no output)"
        except subprocess.TimeoutExpired:
            return "Error: git push timed out after 60s. (Might be waiting for credentials)"
        except Exception as e:
            return f"Error executing git push: {e}"

WORKSPACE_ROOT = os.path.abspath(os.getcwd())
git_tools_instance = GitTools(WORKSPACE_ROOT)

git_status = git_tools_instance.status
git_diff = git_tools_instance.diff
git_log = git_tools_instance.log
git_commit = git_tools_instance.commit
git_push = git_tools_instance.push
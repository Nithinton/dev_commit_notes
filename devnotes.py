import os
import re
import subprocess
import pyperclip

# ----------------------------
# HELPERS
# ----------------------------
def run(cmd):
    return subprocess.check_output(
        cmd,
        shell=True,
        stderr=subprocess.DEVNULL
    ).decode().strip()


def find_git_root(path):
    current = path
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current

        parent = os.path.dirname(current)

        if parent == current:
            return None

        current = parent


def is_valid_git_hash(value):
    """
    Valid Git SHA:
      - 7 to 40 hex characters
    """
    if not value:
        return False

    value = value.strip()

    return re.fullmatch(r"[0-9a-fA-F]{7,40}", value) is not None


def commit_exists(commit_hash):
    """
    Check whether the SHA exists in the current repository.
    """
    try:
        subprocess.check_output(
            f"git cat-file -e {commit_hash}^{{commit}}",
            shell=True,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


# ----------------------------
# MAIN
# ----------------------------

try:

    repo_root = find_git_root(os.getcwd())

    if not repo_root:
        raise Exception("Not inside a Git repository")

    os.chdir(repo_root)

    repo = os.path.basename(repo_root)
    branch = run("git branch --show-current")

    # ----------------------------
    # Decide which commit to use
    # ----------------------------

    clipboard = pyperclip.paste().strip()

    if is_valid_git_hash(clipboard) and commit_exists(clipboard):
        target_commit = clipboard
    else:
        target_commit = "HEAD"

    # ----------------------------
    # Read commit details
    # ----------------------------

    commit_hash = run(f"git rev-parse {target_commit}")
    commit_msg = run(f"git show -s --format=%s {target_commit}")

    output = f"""
Dev Notes:
- Summary: {commit_msg}
- Repo: {repo}
- Branch: {branch}
- Commit: {commit_hash}
""".strip()

    pyperclip.copy(output)

    print("✅ Dev Notes copied to clipboard!")

except Exception as e:
    print(f"❌ Error: {e}")
import subprocess


def commit_data_changes() -> None:
    subprocess.run(["git", "add", "data/"], check=False)
    subprocess.run(["git", "diff", "--cached", "--quiet"], check=False)

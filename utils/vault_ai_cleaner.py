import subprocess

def run_cleanup():
    subprocess.run(
        ["python", "vault/run_vault_cleanup.py"],
        check=False
    )

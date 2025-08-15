import subprocess

def adb_kill_server():
    """Kills the adb server."""
    try:
        subprocess.run(['adb', 'kill-server'], check=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        print("ADB server killed.")
    except Exception as e:
        print(f"無法終止 ADB 服務: {e}")
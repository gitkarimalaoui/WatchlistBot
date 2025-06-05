
import subprocess
import os

def start_tick_collector_background():
    script_path = os.path.join("realtime", "real_time_tick_collector.py")
    try:
        subprocess.Popen(["python", script_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Tick collector started in background.")
    except Exception as e:
        print(f"❌ Error launching tick collector: {e}")

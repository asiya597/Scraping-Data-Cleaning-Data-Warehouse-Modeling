import subprocess
import time
import sys
from datetime import datetime


LOG_FILE = "pipeline.log"


def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"
    print(full_message)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_message + "\n")


def run_step(step_name, command, retries=2, wait_seconds=3):
    for attempt in range(1, retries + 2):
        try:
            write_log(f"START {step_name} - attempt {attempt}")
            subprocess.run(command, check=True)
            write_log(f"SUCCESS {step_name}")
            return
        except subprocess.CalledProcessError:
            write_log(f"ERROR in {step_name}")

            if attempt <= retries:
                write_log(f"Retrying {step_name} after {wait_seconds} seconds")
                time.sleep(wait_seconds)
            else:
                write_log(f"FAILED {step_name} after all retries")
                raise


def main():
    python_exe = sys.executable

    write_log("PIPELINE STARTED")

    run_step("clean", [python_exe, "clean/clean_data.py"])
    run_step("warehouse", [python_exe, "warehouse/load_warhouse.py"])

    write_log("PIPELINE FINISHED SUCCESSFULLY")


if __name__ == "__main__":
    main()

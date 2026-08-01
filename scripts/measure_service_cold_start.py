from __future__ import annotations

import json
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


def main() -> None:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--app-dir",
        "backend",
        "--host",
        "127.0.0.1",
        "--port",
        "8765",
    ]
    started = time.perf_counter()
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    health = None
    try:
        for _ in range(240):
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=5)
                raise RuntimeError(
                    f"service exited early with {process.returncode}\nstdout={stdout}\nstderr={stderr}"
                )
            try:
                with urlopen("http://127.0.0.1:8765/api/health", timeout=1) as response:
                    health = json.loads(response.read().decode("utf-8"))
                break
            except (URLError, TimeoutError):
                time.sleep(0.1)
        if health is None:
            raise RuntimeError("service did not become healthy within 24 seconds")
        print(
            json.dumps(
                {
                    "service_cold_start_ms": round((time.perf_counter() - started) * 1000, 4),
                    "health": health,
                    "python_executable": sys.executable,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    main()

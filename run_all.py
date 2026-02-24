"""
Convenience entry point that exercises the full application pipeline and
its accompanying tests in a single run.  Useful for local deployments or CI
checks where you want to ensure every component works end-to-end.

Usage:
    python run_all.py

The following steps are executed sequentially:

  1. Scraper sanity tests (`test_scrapers.py`)
  2. NLP enhancement tests (`test_nlp_enhancements.py`)
  3. Insight analyzer grading tests (`test_insight_analyzer.py`)
  4. NLP validation (`validate_nlp.py`)
  5. Full data pipeline run (`main.py`)
  6. Streamlit dashboard launch (runs in background)

If any step fails, the script will abort and report the failure.  Once all
steps complete successfully, the Streamlit dashboard is automatically launched
at http://localhost:8501.
"""

import subprocess
import sys
import os

SCRIPTS = [
    ("test_scrapers.py", "Scraper tests"),
    ("test_nlp_enhancements.py", "NLP enhancement tests"),
    ("test_insight_analyzer.py", "Insight analyzer tests"),
    ("validate_nlp.py", "NLP validation"),
    ("main.py", "Pipeline run"),
]


def run_script(relpath: str, description: str) -> bool:
    """Execute a helper script and return True if it succeeded.

    The script is invoked using the same Python interpreter that is running
    this module.  Output from the child process is streamed directly to the
    console.
    """
    print("\n" + "=" * 70)
    print(f"STEP: {description}")
    print("=" * 70)

    path = os.path.abspath(relpath)
    if not os.path.exists(path):
        print(f"  script not found: {path}")
        return False

    rc = subprocess.call([sys.executable, path])
    if rc != 0:
        print(f"  {description} exited with code {rc}")
        return False
    return True


def main() -> None:
    for script, desc in SCRIPTS:
        if not run_script(script, desc):
            print("\nAborting remaining steps due to error.")
            sys.exit(1)

    print("\nAll steps completed successfully.")
    print("Launching Streamlit dashboard...")
    # spawn streamlit in new process; do not wait for it.  forward any extra
    # command-line arguments so callers can specify port/address etc.
    cmd = [sys.executable, "-m", "streamlit", "run", "dashboard.py"]
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    subprocess.Popen(cmd)
    print("Dashboard should be reachable at http://localhost:8501")


if __name__ == "__main__":
    main()

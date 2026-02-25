import sys
from main import main as run_pipeline  # assuming main.py runs scraping + DB insert

if __name__ == "__main__":
    try:
        print("Running production pipeline...")
        run_pipeline()
        print("Pipeline completed successfully.")
    except Exception as e:
        print(f"Pipeline failed: {e}")
        sys.exit(1)

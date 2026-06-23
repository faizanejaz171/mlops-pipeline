"""
Entry point for the CV Data Pipeline.
Place test.py logic here (or import from it) as we modularize.
"""
import sys
import os

# Allow running as: python src/pipeline/main.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# TODO: as we refactor test.py, import sections here
# from pipeline.ingestion import run_gcp_ingestion
# from pipeline.curation import run_smart_curator
# from pipeline.annotation import run_sam3_pipeline

if __name__ == "__main__":
    # Temporary: run original script until modularized
    script_path = os.path.join(os.path.dirname(__file__), "../../test.py")
    if os.path.exists(script_path):
        exec(open(script_path).read())
    else:
        print("Place test.py in project root, or run modularized pipeline.")

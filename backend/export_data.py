"""Run the ecommerce data export pipeline."""

from app.export.export_pipeline import run_export_pipeline


if __name__ == "__main__":
    uploaded_keys = run_export_pipeline()
    print("Export completed successfully")
    for key in uploaded_keys:
        print(f"Uploaded: {key}")

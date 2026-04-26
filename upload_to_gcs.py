import os
from google.cloud import storage

# --- CONFIGURATION ---
KEY_FILE = "secrets/gcs-key.json"  # Place your JSON key file here
BUCKET_NAME = "innsight-data-storage"
LOCAL_DIRECTORY = "local_storage"
GCS_PREFIX = "taba_docs"
# ---------------------


def upload_files():
    if not os.path.exists(KEY_FILE):
        print(
            f"Error: {KEY_FILE} not found. Please place your service account JSON key in the root directory."
        )
        return

    try:
        # Initialize client with the specific service account key
        client = storage.Client.from_service_account_json(KEY_FILE)
        bucket = client.bucket(BUCKET_NAME)

        print(f"Starting upload to bucket: {BUCKET_NAME}...")

        for root, dirs, files in os.walk(LOCAL_DIRECTORY):
            for file in files:
                local_path = os.path.join(root, file)

                # Create GCS path: prefix / relative_path_from_local_dir
                relative_path = os.path.relpath(local_path, LOCAL_DIRECTORY)
                gcs_path = os.path.join(GCS_PREFIX, relative_path).replace("\\", "/")

                blob = bucket.blob(gcs_path)

                print(f"Uploading: {relative_path} -> {gcs_path}")
                blob.upload_from_filename(local_path)

        print("\nSuccess! All files uploaded.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")


if __name__ == "__main__":
    upload_files()

import os
import json
import hashlib

# --- CONFIGURATION ---
LOCAL_DIRECTORY = "local_storage"
BUCKET_NAME = "innsight-data-storage"  # Replace with your bucket
GCS_PREFIX = "taba_docs"
OUTPUT_FILE = "metadata.jsonl"
# ---------------------


def generate_metadata():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for plan_id in os.listdir(LOCAL_DIRECTORY):
            plan_path = os.path.join(LOCAL_DIRECTORY, plan_id)
            if not os.path.isdir(plan_path):
                continue

            # Walk through all files in this plan's folder
            for root, dirs, files in os.walk(plan_path):
                for file in files:
                    local_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_path, LOCAL_DIRECTORY)
                    gcs_path = os.path.join(GCS_PREFIX, relative_path).replace(
                        "\\", "/"
                    )
                    
                    # Create a safe ID using a hash of the GCS path
                    safe_id = hashlib.md5(gcs_path.encode()).hexdigest()

                    # Create the metadata entry
                    entry = {
                        "id": safe_id,
                        "structData": {"plan_id": plan_id, "file_name": file},
                        "content": {
                            "uri": f"gs://{BUCKET_NAME}/{gcs_path}",
                            "mimeType": "application/pdf"
                        },
                    }
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    print(f"Success! {OUTPUT_FILE} created. Upload this to the ROOT of your bucket.")


if __name__ == "__main__":
    generate_metadata()

from google.cloud import discoveryengine_v1beta as discoveryengine
import os

# --- CONFIGURATION ---
KEY_FILE = "secrets/gcs-key.json"  # Use the same key from the upload
PROJECT_ID = "bgu-2026-10"  # Your GCP Project ID
LOCATION = "global"  # Usually 'global'
DATA_STORE_ID = "taba-plans-datastore_1777189395688"  # Get this from Vertex AI Console
# ---------------------

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = KEY_FILE


def search_plans(query):
    client = discoveryengine.SearchServiceClient()

    serving_config = client.serving_config_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        serving_config="default_config",
    )

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=5,
        # This enables the "summary" which is essentially the RAG part
        content_search_spec={
            "summary_spec": {
                "summary_definition_version": "v2",
                "ignore_adversarial_query": True,
                "include_citations": True,
            }
        },
    )

    response = client.search(request)

    print(f"\n--- Results for: {query} ---\n")

    # Print the AI-generated summary (The RAG answer)
    if response.summary:
        print(f"AI SUMMARY:\n{response.summary.summary_text}\n")

    # Print individual document results
    for result in response.results:
        data = result.document.derived_struct_data
        title = data.get("title", "Unknown Title")
        link = data.get("link", "No Link")
        print(f"Document: {title}")
        print(f"Link: {link}\n")


if __name__ == "__main__":
    search_query = input("Enter your search query (Hebrew supported): ")
    search_plans(search_query)

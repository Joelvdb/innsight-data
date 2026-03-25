import json
import requests
import io
from PyPDF2 import PdfReader
import time

def search_keywords_in_pdf(url, keywords):
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with io.BytesIO(response.content) as f:
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                
                for kw in keywords:
                    if kw in text:
                        return kw # Return the keyword found
        else:
            print(f"  -> Failed to download PDF: {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"  -> Error processing PDF {url}: {e}")
    return None

def main():
    input_filename = "plans_data.json"
    output_filename = "hotel_plans.json"
    keywords = ["מלון", "מלונ"]
    base_url = "https://apps.land.gov.il"
    
    try:
        with open(input_filename, "r", encoding="utf-8") as f:
            plans = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_filename} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode {input_filename}.")
        return

    hotel_plans = []
    total_plans = len(plans)
    
    print(f"Starting search for {keywords} in {total_plans} plans...")

    for i, plan in enumerate(plans):
        plan_number = plan.get("planNumber", "Unknown")
        takanon = plan.get("documentsSet", {}).get("takanon")
        
        if takanon and takanon.get("path"):
            path = takanon["path"]
            # Ensure path starts with /
            if not path.startswith("/"):
                path = "/" + path
            
            # Replace backslashes if any
            path = path.replace("\\", "/")
            
            full_url = base_url + path
            print(f"[{i+1}/{total_plans}] Checking plan {plan_number}...")
            
            found_keyword = search_keywords_in_pdf(full_url, keywords)
            if found_keyword:
                print(f"  -> FOUND keyword '{found_keyword}' in plan {plan_number}!")
                plan["found_keyword"] = found_keyword
                hotel_plans.append(plan)
                # Save progress
                with open(output_filename, "w", encoding="utf-8") as out_f:
                    json.dump(hotel_plans, out_f, ensure_ascii=False, indent=4)
            
            time.sleep(1) # Be gentle to the server
        else:
            print(f"[{i+1}/{total_plans}] Plan {plan_number} has no takanon path. Skipping.")

    print(f"\nDone! Found {len(hotel_plans)} plans with keywords {keywords}.")
    print(f"Results saved to {output_filename}")

if __name__ == "__main__":
    main()

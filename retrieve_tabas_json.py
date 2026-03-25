import requests
import json
import time
from datetime import datetime, timedelta


def scrape_to_json(start_date_str, end_date_str, filename="plans_data.json"):
    url = "https://apps.land.gov.il/TabaSearch/api/SerachPlans/GetPlans"
    headers = {"Content-Type": "application/json"}

    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")

    all_plans = []
    current_day = start

    while current_day <= end:
        # Format the date for the API payload
        from_date = current_day.strftime("%Y-%m-%dT22:00:00.000Z")
        to_date = (current_day + timedelta(days=1)).strftime("%Y-%m-%dT22:00:00.000Z")
        print(
            f"Scraping range: {current_day.date()} to {(current_day + timedelta(days=1)).date()}..."
        )

        payload = {
            "planNumber": "",
            "gush": "",
            "chelka": "",
            "statuses": None,
            "planTypes": [
                72,
                21,
                1,
                8,
                9,
                10,
                12,
                20,
                62,
                31,
                41,
                25,
                22,
                2,
                11,
                13,
                61,
                32,
                74,
                78,
                77,
                73,
                76,
                75,
                80,
                79,
                40,
                60,
                71,
                70,
                67,
                68,
                69,
                30,
                50,
                3,
            ],
            "fromStatusDate": from_date,
            "toStatusDate": to_date,
            "planTypesUsed": False,
        }

        try:
            retries = 3
            for attempt in range(retries):
                try:
                    # Added a longer timeout for the large API response
                    response = requests.post(
                        url, json=payload, headers=headers, timeout=60
                    )
                    if response.status_code == 200:
                        response_data = response.json()
                        day_plans = response_data.get("plansSmall", [])
                        if day_plans:
                            all_plans.extend(day_plans)
                            print(f"  -> Found {len(day_plans)} plans.")
                        else:
                            print("  -> No plans found.")
                        break  # Success
                    else:
                        print(f"  -> Error {response.status_code}")
                        break
                except requests.exceptions.RequestException as e:
                    if attempt < retries - 1:
                        print(
                            f"  -> Timeout/Error, retrying ({attempt + 1}/{retries})..."
                        )
                        time.sleep(5)
                    else:
                        print(f"  -> Request failed after {retries} attempts: {e}")
        except Exception as e:
            print(f"  -> Unexpected error: {e}")

        # Save progress immediately
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(all_plans, f, ensure_ascii=False, indent=4)

        current_day += timedelta(days=1)
        time.sleep(2)

    print(f"\nDone! Saved {len(all_plans)} plans to {filename}")


# Example usage:
if __name__ == "__main__":
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10) 
    scrape_to_json(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

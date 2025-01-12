import os
import requests
from datetime import datetime
import dotenv

from dotenv import load_dotenv
load_dotenv()

def search(question, num_results=10, days=5, start=0):
    # Read API key and cx from environment variables
    google_search_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    google_cse_id = os.getenv("GOOGLE_CSE_ID")

    # API endpoint and parameters
    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {
        "q": question,
        "key": google_search_api_key,
        "cx": google_cse_id,
        "lr": "lang_de",
        "gl": "de",
        "dateRestrict" : "d" + str(days),
        "num": num_results,  # Get the specified number of search results
        "googlehost": "google.de",  # Search on google.de domain
        "cr": "countryDE",  # Restrict search to Germany
        "start": start  # The index to start the search results from
    }

    # Make request to API and extract news results
    response = requests.get(url, params=params).json()

    # Check if the "items" key exists in the response
    if "items" in response:
        results = response["items"]
    else:
        results = []

    # Extract article URL, title, snippet, source, and image URL for each search result and store in list
    news_results = []
    for result in results:
        news_result = {
            "url": result["link"],
            "title": result["title"],
            "snippet": result["snippet"],
            "source": result["displayLink"]
        }

        print (news_result['title'])

        # Extract image URL if available
        if "pagemap" in result and "cse_image" in result["pagemap"]:
            news_result["image_url"] = result["pagemap"]["cse_image"][0]["src"]

        news_results.append(news_result)

    return news_results

search("Wann spielt der FCBayern?")
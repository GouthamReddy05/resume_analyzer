
import os
# import json
import requests
from dotenv import load_dotenv
# from langchain.agents import initialize_agent, load_tools
from langchain.agents.agent_types import AgentType
from langchain_community.llms import Ollama
from langchain.tools import tool

load_dotenv()

SERPAPI_API_KEY = os.getenv("serpapi_api_key")
if not SERPAPI_API_KEY:
    raise ValueError("Missing 'serpapi_api_key' in environment variables. Please check your .env file.")

@tool
def fetch_jobs_from_google(role_location: str) -> list:
    """
    Fetch job listings from Google Jobs via SerpAPI based on role and location.
    Returns a list of dicts with job titles, companies, locations, and links.
    """
    if "," in role_location:
        role, location = [x.strip() for x in role_location.split(",", 1)]
    else:
        role = role_location.strip()
        location = ""
    query = f"{role} jobs {location}" if location else f"{role} jobs"

    params = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }

    response = requests.get("https://serpapi.com/search?engine=google_jobs", params=params)

    if response.status_code != 200:
        return [{"error": f"{response.status_code} {response.reason}"}]
    
    data = response.json()
    jobs = data.get("jobs_results", [])
    if not jobs:
        return []
    jobs_list = []
    for job in jobs:
        jobs_list.append({
            "title": job.get("title", "N/A"),
            "company": job.get("company_name", "N/A"),
            "location": job.get("location", "N/A"),
            "link": job.get("apply_options", [{}])[0].get("link", "#")
        })
    return jobs_list


# llm = Ollama(model="llama3")

# tools = [fetch_jobs_from_google]

# agent = initialize_agent(
#     tools,
#     llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     max_iterations=10,
#     handle_parsing_errors=True
# )

# # Run agent
# role_location = "Data Scientist, India"
# response = agent.invoke(role_location)
# print(response)

# Directly call the tool and print job listings in a readable format
jobs = fetch_jobs_from_google("Data Scientist, India")
if jobs:
    print("\nJob Listings:")
    for job in jobs:
        print(f"🔹 {job['title']} – {job['company']}\n📍 {job['location']}\n🔗 {job['link']}\n")
else:
    print("No jobs found.")
        # return result_text.strip()

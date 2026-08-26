from dotenv import load_dotenv
from browser_use_sdk.v4 import BrowserUse

load_dotenv()

with BrowserUse() as client:
    run = client.runs.create(
        "Search for the top 10 Hacker News posts and return the title and URL."
    )
    result = client.runs.wait_for_completion(run.id)
    print(result.result)

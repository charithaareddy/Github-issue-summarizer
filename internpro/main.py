from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from frontend import fetch_github_issue  # Custom function to fetch issue details
import os
import requests

# Create FastAPI instance
app = FastAPI()

# Define request schema using Pydantic
class IssueRequest(BaseModel):
    repo_url: str
    issue_number: int

# Define the POST endpoint for analyzing a GitHub issue
@app.post("/analyze_issue")
async def analyze_issue(request: IssueRequest):
    # Fetch issue data from GitHub
    issue_data = fetch_github_issue(request.repo_url, request.issue_number)

    # Raise error if issue couldn't be fetched
    if 'error' in issue_data:
        raise HTTPException(status_code=400, detail=issue_data['error'])

    # Extract relevant fields
    title = issue_data.get('title', "")
    body = issue_data.get('body', "")
    comments = issue_data.get('comments', [])

    # Combine title, body, and all comments into a single text string
    combined_comments = ' '.join(c for c in comments if c)
    combined_text = f"{title}\n\n{body}\n\n{combined_comments}".strip()

    # Helper function to truncate text for summarization
    def truncate_text(text, max_words=750):
        words = text.split()
        return ' '.join(words[:max_words]) + ("..." if len(words) > max_words else "")

    # Prepare input for summarization model
    truncated_text = truncate_text(combined_text)

    # Hugging Face model URL and token
    HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    huggingface_token = os.getenv("HF_TOKEN")  # Load token from environment variable

    # If no token found, return server error
    if not huggingface_token:
        raise HTTPException(status_code=500, detail="Missing Hugging Face token (HF_TOKEN).")

    headers = {
        "Authorization": f"Bearer {huggingface_token}"
    }

    summary_text = "No content available for summarization."

    # Perform summarization using Hugging Face model
    if truncated_text:
        try:
            response = requests.post(
                HF_API_URL,
                headers=headers,
                json={
                    "inputs": truncated_text,
                    "parameters": {"max_length": 150, "min_length": 30}
                }
            )
            response.raise_for_status()
            response_json = response.json()

            # Handle various response formats
            if isinstance(response_json, list) and len(response_json) > 0:
                summary_text = response_json[0].get("summary_text", "Summary not found.")
            elif isinstance(response_json, dict) and response_json.get("error"):
                raise HTTPException(status_code=500, detail=f"Hugging Face error: {response_json['error']}")
            else:
                summary_text = "Unexpected Hugging Face response format."

        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Request to Hugging Face failed: {str(e)}")

    # Classify issue type based on keywords
    text_lower = f"{title} {body}".lower()

    issue_type = "other"
    if any(w in text_lower for w in ["error", "fail", "crash", "bug"]):
        issue_type = "bug"
    elif any(w in text_lower for w in ["feature", "support", "add", "implement"]):
        issue_type = "feature_request"
    elif any(w in text_lower for w in ["doc", "readme", "guide", "documentation"]):
        issue_type = "documentation"
    elif any(w in text_lower for w in ["help", "can i", "what", "question"]):
        issue_type = "question"

    # Score the issue's priority based on severity keywords
    priority_score_value = 1
    priority_justification = "Lowest priority, general discussion."

    if issue_type == "bug":
        if any(w in text_lower for w in ["critical", "crash", "blocking", "data loss"]):
            priority_score_value = 5
            priority_justification = "Critical: blocks functionality or causes data loss."
        elif any(w in text_lower for w in ["major", "frequent"]):
            priority_score_value = 4
            priority_justification = "High: affects many users or core features."
        else:
            priority_score_value = 3
            priority_justification = "Medium severity bug."
    elif issue_type == "feature_request":
        if any(w in text_lower for w in ["must-have", "key", "essential"]):
            priority_score_value = 4
            priority_justification = "Important new functionality."
        else:
            priority_score_value = 3
            priority_justification = "Useful improvement."
    elif issue_type == "documentation":
        priority_score_value = 2
        priority_justification = "Improves documentation."
    elif issue_type == "question":
        priority_score_value = 2
        priority_justification = "User inquiry."

    # Combine score and reason into one string
    priority_score = f"{priority_score_value} - {priority_justification}"

    # Map issue type to suggested GitHub labels
    label_map = {
        "bug": ["bug", "priority-high", "needs-triage"],
        "feature_request": ["enhancement", "feature", "future-consideration"],
        "documentation": ["docs", "help-wanted", "documentation"],
        "question": ["question", "discussion", "clarification-needed"],
        "other": ["discussion", "misc"]
    }
    labels = label_map.get(issue_type, ["uncategorized"])[:3]

    # Potential impact description based on type
    potential_impact = {
        "bug": "May cause failure or block critical features.",
        "feature_request": "Can improve user experience or core capability.",
        "documentation": "Helps onboarding and reduces confusion.",
        "question": "Can inform future improvements.",
        "other": "General impact unclear."
    }.get(issue_type, "Limited direct user impact.")

    # Return final structured response
    return {
        "summary": summary_text,
        "type": issue_type,
        "priority_score": priority_score,
        "suggested_labels": labels,
        "potential_impact": potential_impact
    }

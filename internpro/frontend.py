import requests
"""
    Fetches a GitHub issue's title, body, and comments using the GitHub API.

    Parameters:
        repo_url (str): GitHub repository URL (e.g., "https://github.com/owner/repo" or "owner/repo")
        issue_number (int or str): The number of the issue to fetch

    Returns:
        dict: A dictionary with 'title', 'body', and 'comments' of the issue,
              or an error message if the fetch fails.
    """
# Extract the owner and repository name from the URL
def fetch_github_issue(repo_url, issue_number):
    if repo_url.startswith("https://github.com/"):
        parts = repo_url.rstrip("/").split("/")
        owner = parts[-2]
        repo = parts[-1]
    else:
        owner, repo = repo_url.split("/")
# Construct the API URL for the specific issue
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
     # Send GET request to GitHub API to fetch issue details
    response = requests.get(api_url)
 # If successful response received
    if response.status_code == 200:
        issue_data = response.json()
        # Extract the issue title and body
        title = issue_data.get('title', 'No title')
        body = issue_data.get('body', 'No body')
        # Get the URL to fetch comments (if available)
        comments_url = issue_data.get('comments_url', '')

        comments = []
        if comments_url:
            # Send another GET request to fetch comments
            comments_response = requests.get(comments_url)
            if comments_response.status_code == 200:
                comments_data = comments_response.json()
                # Extract comment bodies into a list
                comments = [c['body'] for c in comments_data]
  # Return the collected issue data
        return {
            "title": title,
            "body": body,
            "comments": comments
        }
    else:
         # If the API request failed, return an error with the status code
        return {"error": f"GitHub issue fetch failed: {response.status_code}"}

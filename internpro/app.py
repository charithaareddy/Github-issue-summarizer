import streamlit as st
import requests
import json
#setup streamlit page
st.set_page_config(page_title="GitHub Issue Summarizer", page_icon="🐙")
st.title("🧠 GitHub Issue Summarizer")
# Input fields for repo URL and issue number
repo_url = st.text_input("GitHub Repository URL", "https://github.com/facebook/react")
issue_number = st.number_input("Issue Number", min_value=1, step=1, value=123) # Added default value for easier testing
# When the "Analyze Issue" button is clicked
if st.button("Analyze Issue"):
    if not repo_url or not issue_number:
        st.warning("Please provide both repository URL and issue number.")
    else:
        # Prepare request payload
        payload = {
            "repo_url": repo_url,
            "issue_number": int(issue_number)
        }

        with st.spinner("Analyzing issue..."): # Added a spinner for better UX
            try:
                # Call your FastAPI backend
                response = requests.post("http://127.0.0.1:8000/analyze_issue", json=payload)
                # Check if the response is successful and display the result
                if response.status_code == 200:
                    try:
                        result = response.json()

                        # This specific fix is likely not needed anymore if main.py always returns a list
                        # if isinstance(result.get("suggested_labels"), dict):
                        #     result["suggested_labels"] = list(result["suggested_labels"].values())

                        st.json(result)  # displays raw JSON

 # This will display the JSON as requested

                    except json.JSONDecodeError:
                        st.warning("⚠️ Could not parse response as JSON from backend.")
                        st.text(response.text)
                else:
                    st.error(f"❌ Error from backend: {response.status_code}")
                    st.text(response.text)
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the FastAPI backend. Make sure it's running at http://127.0.0.1:8000.")
            except Exception as e:
                st.error("Something went wrong while calling the backend.")
                st.text(str(e))
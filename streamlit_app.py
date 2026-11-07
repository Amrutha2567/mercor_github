import os
import requests
import streamlit as st

st.set_page_config(page_title="GitHub Complexity Analyzer", page_icon="🧠")
st.title("🧠 GitHub Repository Complexity Analyzer")
st.write("Compare a user's public repositories using evidence-based GPT analysis.")
api_url = st.text_input("Backend URL", value=os.getenv("API_URL", "http://localhost:8000")).rstrip("/")
github_url = st.text_input("GitHub profile URL", placeholder="https://github.com/octocat")
if st.button("Analyze repositories", type="primary"):
    if not github_url.strip():
        st.error("Enter a GitHub profile URL.")
    else:
        with st.spinner("Fetching repositories and evaluating code. This may take several minutes..."):
            try:
                response = requests.post(f"{api_url}/analyze",
                                         json={"github_url": github_url}, timeout=1800)
                response.raise_for_status()
                result = response.json()
                winner = result["winner"]
                repo = winner["repository"]
                analysis = winner["analysis"]
                st.success(f"Most technically complex: {repo['full_name']}")
                st.markdown(f"[Open repository]({repo['html_url']})")
                st.metric("Weighted complexity score", f"{analysis['weighted_score']}/10")
                st.subheader("GPT justification")
                st.write(analysis.get("technical_summary", "No summary returned."))
                st.subheader("Evidence")
                for item in analysis.get("evidence", []):
                    st.markdown(f"- **{item.get('file', 'File')}** — {item.get('observation', '')}")
                st.subheader("Repository comparison")
                st.json(result["comparison"])
                with st.expander("Full repository assessments"):
                    st.json(result["assessments"])
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

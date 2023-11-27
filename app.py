import streamlit as st
import os
from construct_index import construct_index


def main():
    port = int(os.environ.get("PORT", 8501))

    st.title("Your Chatbot")
    st.write('''This app will ingest all of your content that you upload to a github repo.
             You'll need to provide a repo of your content (check mine https://github.com/MasonYuDev/Mason-Writing-Corpus)
             and your OpenAI API key. After that, you can ask it to write application questions for you as long as the content
             you uploaded is relevant to your query.''')
    
    with st.form(key='user_input_form'):
        st.session_state.repo_url = st.text_input("Enter GitHub Repository URL:")
        st.session_state.api_key = st.text_input("Enter OpenAI API Key:", type='password')
        st.session_state.submitted = st.form_submit_button('Submit')

    if st.session_state.submitted:
        if not st.session_state.repo_url or not st.session_state.api_key:
            st.error("Please enter a valid GitHub Repository URL and OpenAI API Key.")
        else:
            st.success("Submission successful. Repository cloning and indexing will begin.")
            repo_name = os.path.basename(st.session_state.repo_url.rstrip('/'))
            repo_folder = os.path.join('/tmp/content', repo_name)
            os.makedirs(repo_folder, exist_ok=True)
 
            clone_cmd = f"git clone {st.session_state.repo_url} {repo_folder}"
            os.system(clone_cmd)

            directory_path = repo_folder
            st.session_state["query_engine"] = construct_index(directory_path, st.session_state.api_key)
            st.success("Repository cloned and indexed successfully!")

    query = st.chat_input("What do you want to know?")
    if query and st.session_state.query_engine:
        st.write(query)
        if query.lower() == "quit":
            st.stop()
        else:
            response = st.session_state.query_engine.query(query)
            st.write(f"Mason says: {response.response}")
            
    
if __name__ == "__main__":
    main()

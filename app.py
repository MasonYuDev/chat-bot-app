import streamlit as st
import os
from construct_index import construct_index
import json
import tempfile


def main():
    port = int(os.environ.get("PORT", 8501))

    st.title("Chatbot from Indexed Documents")
    st.write('''This app will ingest all of your content that you upload to a github repo or in a JSON file.
             You'll need to provide a repo of your content (check mine https://github.com/MasonYuDev/Mason-Writing-Corpus) or a JSON file
             and your OpenAI API key. After that, you can ask it creative questions for you as long as the content
             you uploaded is relevant to your query.''')
    
    content_source = st.radio("Choose content source:", ["GitHub Repo", "JSON File"])

    with st.form(key='user_input_form'):
        if content_source == "GitHub Repo":
            st.session_state.repo_url = st.text_input("Enter GitHub Repository URL:")
        elif content_source == "JSON File":
            uploaded_file = st.file_uploader("Upload JSON File", type=["json"])
        st.session_state.api_key = st.text_input("Enter OpenAI API Key:", type='password')
        st.session_state.submitted = st.form_submit_button('Submit')

    if st.session_state.submitted:
        if content_source == "GitHub Repo":
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

        elif content_source == "JSON File":
            if uploaded_file is not None:
                # Read the file content
                temp_dir = tempfile.mkdtemp()

            # Read the file content
                json_data = uploaded_file.read().decode('utf-8')
                data = json.loads(json_data)

            # Save each JSON entry as a separate file in the temporary directory
                for idx, entry in enumerate(data):
                    entry_filename = f"json_entry_{idx}.json"
                    entry_filepath = os.path.join(temp_dir, entry_filename)
                    with open(entry_filepath, 'w') as entry_file:
                        json.dump(entry, entry_file)
                print(temp_dir)
                st.session_state["query_engine"] = construct_index(temp_dir, st.session_state.api_key)
                st.success("JSON File uploaded and indexed successfully!")

            else:
                st.warning("Please upload a valid JSON file.")
            
    
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

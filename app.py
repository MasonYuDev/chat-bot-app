import streamlit as st
import os
from construct_index import construct_index


def main():
    port = int(os.environ.get("PORT", 8501))


    st.title("Your Chatbot")
    st.header("Use Your Chatbot")
    
    st.text_input("Enter GitHub Repository URL:", key = "repo_url")
    st.text_input("Enter OpenAI API Key:", key = "api_key")
    
    if not st.session_state.repo_url or not st.session_state.api_key:
        st.error("Please enter a valid GitHub Repository URL and OpenAI API Key.")
        return

    # Create a folder with the repository name
    repo_name = os.path.basename(st.session_state.repo_url.rstrip('/'))
    repo_folder = os.path.join('/tmp/content', repo_name)
    os.makedirs(repo_folder, exist_ok=True)

    # Clone the repository
    clone_cmd = f"git clone {st.session_state.repo_url} {repo_folder}"
    os.system(clone_cmd)

    # Use the correct path to the cloned repository
    directory_path = repo_folder
    st.session_state["query_engine"] = construct_index(directory_path, st.session_state.api_key)

    st.success("Repository cloned and indexed successfully!")

    query = st.chat_input("What do you want to know?")
    if query and st.session_state.query_engine:
        st.write(query)
        if query.lower() == "quit":
            st.stop()
        else:
            # Query the engine and display the result
            response = st.session_state.query_engine.query(query)
            st.write(f"Mason says: {response.response}")
            
    st.run_app(port=port)
    
if __name__ == "__main__":
    main()

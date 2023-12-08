import streamlit as st
import os
from construct_index import construct_index
from resume import scrape_dynamic_page, process_web_content, extract_job_requirements, generate_cover_letter
import json
import tempfile


def main():
    port = int(os.environ.get("PORT", 8501))

    st.title("Cover Letter from Indexed Documents & Job Description")
    st.write('''Upload your resume in Docx or PDF format. Alternatively, upload all your content through a github repo or in a JSON file.
             \nThen add your API key.
             \nAfter your content has been indexed into the database, submit the URL of the job description.
             \nWatch as the bot completes each step.
             \nIt can take 2 minutes to generate your cover letter.''')
    
    content_source = st.radio("Choose content source:", ["File Upload", "GitHub Repo", "JSON File"])

    with st.form(key='user_input_form'):
        if content_source == "GitHub Repo":
            st.session_state.repo_url = st.text_input("Enter GitHub Repository URL:")
        elif content_source == "JSON File":
            uploaded_file = st.file_uploader("Upload JSON File", type=["json"])
        else:
            uploaded_file = st.file_uploader("Upload Your File")
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
        else:
            if uploaded_file is not None:
                temp_dir = tempfile.mkdtemp()
                file_name = uploaded_file.name
                file_filepath = os.path.join(temp_dir, file_name)

        # Save the file content to the temporary file
                with open(file_filepath, 'wb') as file:
                    print(uploaded_file.read)
                    file.write(uploaded_file.read())

                st.session_state["query_engine"] = construct_index(temp_dir, st.session_state.api_key)
                st.success("Index Constructed Successfully!")

            
    query = st.chat_input("Enter URL")
    
    if query and st.session_state.query_engine:
        st.write(query)
        if query.lower() == "quit":
            st.stop()
        else:
            st.write("extracting page contents...")
            page_content = scrape_dynamic_page(query)
            st.write("processing and cleaning the content. This can take a while...")
            cleaned_content = process_web_content(page_content)
            st.write(f"This is the cleaned job description: {cleaned_content}")
            st.write("Now, parsing job requirements...")
            job_reqs = extract_job_requirements(cleaned_content)
            st.write(f"This is the job reqs: {job_reqs}")
            prompt = "From the top 10 most relevant matches for this list of job requirements, please fill in your top professional experiences. Please output in JSON format with the following keys: Requirement, Matching Experience, Supporting Bullet Point(s), Place/Company of Experience, Reasoning."
            st.write("Finding your job skill matches...")
            matching_skills = st.session_state.query_engine.query(prompt + job_reqs).response
            st.write(f"These are your skill matches: {matching_skills}")
            st.write("Generating cover letter...")
            cover_letter = generate_cover_letter(cleaned_content, matching_skills)
            st.write(cover_letter)
            
    
if __name__ == "__main__":
    main()

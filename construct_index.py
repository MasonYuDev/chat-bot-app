from llama_index import SimpleDirectoryReader, ServiceContext, VectorStoreIndex, LLMPredictor, PromptHelper
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from langchain.chat_models import ChatOpenAI
from llama_index.node_parser.interface import MetadataMode

import os
import uuid
import json

def construct_index(content_source, content_data, openai_key):
    # set maximum input size
    max_input_size = 4096
    # set number of output tokens
    num_outputs = 1024
    # set maximum chunk overlap
    max_chunk_overlap = 20
    # set chunk size limit
    chunk_size_limit = 600
    chunk_overlap_ratio = 0.5
    
    os.environ["OPENAI_API_KEY"] = openai_key

    # define LLM or Language Model Wrapper
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo", max_tokens=num_outputs))
    prompt_helper = PromptHelper(max_input_size, num_outputs, chunk_overlap_ratio, chunk_size_limit=chunk_size_limit)

    llama_debug = LlamaDebugHandler(print_trace_on_end=True)
    callback_manager = CallbackManager([llama_debug])

    service_context = ServiceContext.from_defaults(callback_manager=callback_manager, llm_predictor=llm_predictor)

    if content_source == "GitHub Repo":
        # Load content from GitHub
        documents = SimpleDirectoryReader(content_data).load_data()
        print(documents)
    elif content_source == "JSON File":
        documents = SimpleDirectoryReader(content_data).load_data()

        # Extract relevant information, modify as needed based on your JSON structure
        
    else:
        raise ValueError("Invalid content source. Supported sources: 'GitHub', 'JSON'")
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    print(index)
    query_engine = index.as_query_engine()

    return query_engine



class JSONDocument:
    def __init__(self, title, url, html):
        self.id_ = str(uuid.uuid4())  # Generate a unique ID
        self.embedding = None
        self.metadata = {
            'file_path': None,
            'file_name': None,
            'file_type': None,
            'file_size': None,
            'creation_date': None,
            'last_modified_date': None,
            'last_accessed_date': None
        }
        self.excluded_embed_metadata_keys = [
            'file_name', 'file_type', 'file_size', 'creation_date',
            'last_modified_date', 'last_accessed_date'
        ]
        self.excluded_llm_metadata_keys = self.excluded_embed_metadata_keys
        self.relationships = {}
        self.hash = None
        self.text = f"{title}\n{url}\n{html}"

    def get_doc_id(self):
        return self.id_

    def get_metadata_str(self, mode):
        # Convert metadata dictionary to a JSON-formatted string
        metadata_to_str = {
            '2': lambda: json.dumps(self.metadata, default=str),
            '3': lambda: json.dumps(self.metadata, default=str)
        }
        return metadata_to_str[mode]()
    
    def get_content(self, metadata_mode):
        # Return text content
        return self.text
    
def transform_json_to_documents(json_data):
    return [
        JSONDocument(
            title=entry["title"],
            url=entry["url"],
            html=entry["html"]
        )
        for entry in json_data
        ]
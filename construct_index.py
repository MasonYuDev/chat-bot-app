from llama_index import SimpleDirectoryReader, ServiceContext, GPTListIndex, readers, VectorStoreIndex, LLMPredictor, PromptHelper, StorageContext, load_index_from_storage
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from langchain.chat_models import ChatOpenAI
import streamlit as st
import sys
import os


def construct_index(directory_path, openai_key):
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

    documents = SimpleDirectoryReader(directory_path).load_data()
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    query_engine = index.as_query_engine()

    return query_engine


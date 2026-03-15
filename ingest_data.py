#importing packages to detect format and handle temp files.
import os
import tempfile
from pathlib import Path
from typing import List
#importing loaders
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_community.document_loaders import Docx2txtLoader
#importing function for imbeddings and storing
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

#defining path of chroma db and collection name
db_path = "easydocs_db"
collection = "docs"
#splitter object:
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

#imbedding the document
embeddings = OpenAIEmbeddings()
#storing vector
vectordb = Chroma(
    collection_name=collection,
    persist_directory= db_path,
    embedding_function=embeddings
)



#function to convert files to text, imbed and store in vector db
def process_docs(file_name, file_content):
    LOADER_MAP = {
        ".pdf": PyPDFLoader,
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
        ".html": UnstructuredHTMLLoader,
        ".docx": Docx2txtLoader
    }
    ext = Path(file_name).suffix.lower() #extracting format of the file
    if ext not in LOADER_MAP: #checking if the file format is supported by easy docs
        raise ValueError(f"Unsupported file type: {ext}")
    #writing the supported format's file to temperary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
        temp.write(file_content)
        temp_path = temp.name
    loader_class = LOADER_MAP[ext] #loading the correct loader acording to the format of the file
    loader = loader_class(temp_path)
    docs = loader.load()
    for doc in docs: #adding the original file's name refference
        doc.metadata["source"] = file_name
    #splitting the document in chunks
    chunks = splitter.split_documents(docs)
    vectordb.add_documents(chunks)
    #clearing the temp file
    os.remove(temp_path)
    return len(chunks)






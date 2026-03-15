from langchain_community.document_loaders import RecursiveUrlLoader
from bs4 import BeautifulSoup

from ingest_data import vectordb, splitter


def ingest_url(url: str):

    loader = RecursiveUrlLoader(
        url=url,
        max_depth=2,
        prevent_outside=True
    )

    docs = loader.load()

    cleaned_docs = []

    for doc in docs:

        soup = BeautifulSoup(doc.page_content, "lxml")

        text = soup.get_text()

        doc.page_content = text
        doc.metadata["source"] = url

        cleaned_docs.append(doc)

    chunks = splitter.split_documents(cleaned_docs)

    vectordb.add_documents(chunks)

    return len(chunks)
from langchain_community.document_loaders import RecursiveUrlLoader, PlaywrightURLLoader
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from ingest_data import vectordb, splitter


# 🔁 SMART LOADER (auto handles static + JS sites)
def load_url_smart(url: str):

    print("\nTrying normal loader...")

    loader = RecursiveUrlLoader(
        url=url,
        max_depth=1,
        prevent_outside=True
    )

    docs = loader.load()

    # if content looks valid → use it
    if docs and len(docs[0].page_content.strip()) > 500:
        print("✅ Using normal loader")
        return docs

    print("⚠️ Falling back to Playwright...")

    loader = PlaywrightURLLoader(urls=[url])
    return loader.load()


# 🔗 SAFE LINK FILTER
def is_valid_link(base_url, link):

    if not link:
        return False

    link = link.strip()

    # ❌ skip useless links
    if link.startswith("#") or \
       link.startswith("javascript:") or \
       link.startswith("mailto:"):
        return False

    full_url = urljoin(base_url, link)

    parsed_base = urlparse(base_url)
    parsed_url = urlparse(full_url)

    # ❌ skip different domain
    if parsed_base.netloc != parsed_url.netloc:
        return False

    path = parsed_url.path.lower()

    # ❌ block obvious junk only (keep light)
    blocked_keywords = [
        "login", "signup", "auth",
        "privacy", "terms", "contact",
        "cookie", "legal"
    ]

    if any(f"/{word}" in path for word in blocked_keywords):
        return False

    return True


# 🌐 FINAL INGEST FUNCTION
def ingest_url(url: str, visited=None, max_links=5, depth=0, max_depth=2):

    if visited is None:
        visited = set()

    # 🧹 normalize URL (remove fragments, trailing slash)
    url = url.split("#")[0].rstrip("/")

    print("\n==============================")
    print("Processing URL:", url, "| Depth:", depth)

    # 🔒 STOP recursion
    if depth > max_depth:
        print("Max depth reached:", url)
        return 0

    if url in visited:
        print("Already visited:", url)
        return 0

    visited.add(url)

    # 🔁 load page (smart)
    docs = load_url_smart(url)

    print("Docs loaded:", len(docs))

    total_chunks = 0
    new_links = set()

    for doc in docs:

        print("\n--- DOCUMENT ---")
        print("Raw length:", len(doc.page_content))

        soup = BeautifulSoup(doc.page_content, "lxml")

        # 🔗 extract links safely
        for link in soup.find_all("a", href=True):
            href = link["href"]

            if is_valid_link(url, href):
                full_url = urljoin(url, href)
                full_url = full_url.split("#")[0].rstrip("/")
                new_links.add(full_url)

        print("Valid links found:", len(new_links))

        # 🧹 clean text
        text = " ".join(soup.get_text().split())

        print("Cleaned length:", len(text))

        if not text.strip():
            print("Skipped: Empty content")
            continue

        doc.page_content = text
        doc.metadata["source"] = url

        # ✂️ split into chunks
        chunks = splitter.split_documents([doc])

        print("Chunks created:", len(chunks))

        if not chunks:
            print("Skipped: No chunks")
            continue

        # 💾 store in DB
        vectordb.add_documents(chunks)

        total_chunks += len(chunks)

        print("Chunks added:", len(chunks), "| Total:", total_chunks)

    print("\nLinks to visit next:", len(new_links))

    # 🔁 controlled recursion
    for link in list(new_links)[:max_links]:
        total_chunks += ingest_url(
            link,
            visited,
            max_links,
            depth + 1,
            max_depth
        )

    print("Returning total for", url, ":", total_chunks)

    return total_chunks
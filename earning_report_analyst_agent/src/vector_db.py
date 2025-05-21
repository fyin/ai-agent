import logging
import re
from typing import Optional, List

from bs4 import BeautifulSoup
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from earning_report_analyst_agent.src.logger import configure_logging

logger = configure_logging(log_file = "log/er_analyst.log", module_name="vector_db", log_level=logging.INFO)

class ChromaDB:
    def __init__(self):
        pass

    def extract_text_from_html(self, file_path: str) -> str:
        """
        Extract clean text from an SEC filing HTML document.

        Args:
            file_path (str): Path to the HTML file.

        Returns:
            str: Extracted text or empty string if failed.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            # Remove scripts, styles, and other non-content tags
            for tag in soup(["script", "style", "header", "footer", "nav"]):
                tag.decompose()

            # Get text and clean it
            text = soup.get_text(separator=" ", strip=True)
            # Remove excessive whitespace and special characters
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        except Exception:
            logger.exception(f"Error extracting text from {file_path}")
            return ""

    def create_chroma_vectorstore(self, text: str, collection_name: str, persist_dir: str,
                                  chunk_size: Optional[int] = 5000, chunk_overlap: Optional[int]=200) -> Optional[Chroma]:
        """
        Create a Chroma vector store from text for RAG.

        Args:
            text (str): Text to process (e.g., earnings report).
            collection_name (str): Name of the Chroma collection.
            persist_dir (str): Directory for persistent storage.

        Returns:
            Chroma: Chroma vector store object or None if failed.
        """
        try:
            # Split text into chunks
            splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            doc_splits = splitter.split_text(text)
            if not doc_splits:
                logger.warning("No document chunks created.")
                return None
            unique_splits = []
            seen = set()
            for split in doc_splits:
                if split not in seen:
                    unique_splits.append(split)
                    seen.add(split)

            embedding_model = HuggingFaceEmbeddings()
            # Create Chroma vector store with persistence
            vectorstore = Chroma.from_texts(
                texts=unique_splits,
                collection_name=collection_name,
                embedding=embedding_model,
                persist_directory=persist_dir
            )
            logger.info(f"Created Chroma vector store with {len(doc_splits)} chunks at {persist_dir}/{collection_name}")
            return vectorstore

        except Exception as e:
            logger.exception(f"Error creating Chroma vector store")
            return None

    def query_earnings(self, vectorstore: Chroma, query: str, k: int = 3) -> List[Document]:
        """
        Perform semantic search on the Chroma vector store for a query.

        Args:
            vectorstore (Chroma): Chroma vector store object.
            query (str): Query string (e.g., "What was Apple's Q1 2025 revenue?").
            k (int): Number of results to return.

        Returns:
            list: List of relevant document chunks.
        """
        try:
            results = vectorstore.similarity_search(query, k=k)
            for i, doc in enumerate(results, 1):
                logger.info(f"Result {i}: {doc.page_content[:2000]}...")
            return results

        except Exception as e:
            logger.exception(f"Error querying vector store")
            return []

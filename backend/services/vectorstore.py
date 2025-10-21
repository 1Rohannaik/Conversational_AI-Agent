import os
import re
from typing import Optional

from chromadb import PersistentClient
from chromadb.config import Settings as ChromaSettings
from langchain_community.vectorstores import Chroma

from .embeddings import STEmbeddings


CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")


def collection_name(file_id: str) -> str:
    base = f"file_{file_id}"
    name = re.sub(r"[^a-zA-Z0-9._-]", "-", base)
    if not re.match(r"^[a-zA-Z0-9]", name):
        name = f"f{name}"
    if not re.search(r"[a-zA-Z0-9]$", name):
        name = f"{name}0"
    if len(name) < 3:
        name = (name + "000")[:3]
    if len(name) > 512:
        name = name[:512]
    return name


def get_client() -> PersistentClient:
    return PersistentClient(path=CHROMA_DIR, settings=ChromaSettings(anonymized_telemetry=False))


def get_vectorstore(file_id: str, embedding: Optional[STEmbeddings] = None) -> Chroma:
    emb = embedding or STEmbeddings()
    client = get_client()
    return Chroma(collection_name=collection_name(str(file_id)), embedding_function=emb, client=client)


def create_from_texts(texts, file_id: str, embedding: Optional[STEmbeddings] = None) -> Chroma:
    emb = embedding or STEmbeddings()
    client = get_client()
    return Chroma.from_texts(texts, emb, collection_name=collection_name(str(file_id)), client=client)


def collection_count(file_id: str) -> int:
    client = get_client()
    col = client.get_or_create_collection(name=collection_name(str(file_id)))
    return col.count() if hasattr(col, "count") else 0

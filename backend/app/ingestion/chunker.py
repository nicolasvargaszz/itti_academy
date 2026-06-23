"""
chunker.py — Divide artículos en fragmentos aptos para embeddings.

Tamaño: 1500 chars (~375 tokens). Overlap: 200 chars (~50 tokens).
El overlap preserva contexto entre fragmentos contiguos.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_articles(articles: list[dict]) -> list[dict]:
    """
    Divide cada artículo en chunks con metadata completa.
    Retorna lista de chunks listos para embed_and_store().
    """
    chunks = []
    for art in articles:
        texts = _SPLITTER.split_text(art["content"])
        for i, text in enumerate(texts):
            chunks.append({
                "id": f"{art['id']}_chunk_{i}",
                "text": text,
                "metadata": {
                    "source_url": art["url"],
                    "title": art["title"],
                    "category": art["category"],
                    "chunk_index": i,
                    "total_chunks": len(texts),
                    "scraped_at": art["scraped_at"],
                },
            })
    print(f"✂️  {len(chunks)} chunks desde {len(articles)} artículos")
    return chunks

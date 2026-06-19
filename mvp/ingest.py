"""
ingest.py — Pipeline completo: scraping → chunks → embeddings → ChromaDB
Ejecutar UNA SOLA VEZ (o cuando haya contenido nuevo)
"""
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://ayuda.ueno.com.py"
DATA_DIR = Path("data/scraped")
CHROMA_PATH = "./data/chroma_db"
COLLECTION_NAME = "uendi_knowledge"
DELAY = 1.5  # segundos entre requests

EMBED_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"  # 118MB, descarga automática

HEADERS = {"User-Agent": "UendiRAGBot/1.0 (academico)"}


# ─── HELPERS ────────────────────────────────────────────────────────────────

def fetch(url: str, session: requests.Session) -> BeautifulSoup | None:
    """Descarga una URL y retorna BeautifulSoup, o None si falla."""
    try:
        r = session.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ⚠ {url}: {e}")
        return None


def strip_query(url: str) -> str:
    """Elimina query params de una URL para deduplicar."""
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path, "", "", ""))


# ─── 1. DISCOVERY (3 niveles: section → sub-section → article) ───────────────

def discover_sections(session: requests.Session) -> list[str]:
    """Extrae las URLs de secciones desde la home."""
    soup = fetch(BASE_URL, session)
    if not soup:
        return []
    sections = []
    for a in soup.find_all("a", href=True):
        full = urljoin(BASE_URL, a["href"])
        if "/section/" in full and BASE_URL in full:
            sections.append(full)
    return list(dict.fromkeys(sections))  # preserva orden, sin duplicados


def discover_subsections(section_url: str, session: requests.Session) -> list[str]:
    """Extrae las URLs de sub-secciones desde una sección."""
    soup = fetch(section_url, session)
    if not soup:
        return []
    subsections = []
    for a in soup.find_all("a", href=True):
        full = urljoin(BASE_URL, a["href"])
        if "/sub-section/" in full and BASE_URL in full:
            subsections.append(full)
    return list(dict.fromkeys(subsections))


def discover_articles(subsection_url: str, session: requests.Session) -> list[tuple[str, str]]:
    """
    Extrae las URLs de artículos y su categoría desde una sub-sección.
    Retorna lista de (url_limpia, nombre_categoria).
    """
    soup = fetch(subsection_url, session)
    if not soup:
        return []
    # Nombre de la sub-sección como categoría
    path = urlparse(subsection_url).path  # /sub-section/Tarjeta de débito virtual
    category = path.split("/sub-section/")[-1].replace("%20", " ") if "/sub-section/" in path else "General"

    articles = []
    for a in soup.find_all("a", href=True):
        full = urljoin(BASE_URL, a["href"])
        if "/article/" in full and BASE_URL in full:
            clean = strip_query(full)
            articles.append((clean, category))
    return list(dict.fromkeys(articles))


# ─── 2. EXTRACCIÓN DE CONTENIDO ──────────────────────────────────────────────

# Textos del footer/nav que aparecen en todas las páginas — los excluimos
_BOILERPLATE = {
    "Inicio", "Chateá con uendi", "Centro de ayuda", "Contactanos",
    "Los 7 días, las 24 horas.", "Llamanos al", "+595 21 618 8000",
    "© 2025 ueno bank S.A.", "Todos los derechos reservados.",
}


def extract_article(soup: BeautifulSoup, url: str, category: str) -> dict | None:
    """Extrae título y contenido limpio de una página de artículo."""
    title_el = soup.select_one("h1")
    if not title_el:
        return None
    title = title_el.get_text(strip=True)

    main = soup.select_one("main")
    if not main:
        return None

    for tag in main.find_all(["script", "style", "nav", "button", "footer"]):
        tag.decompose()

    # Tomar párrafos y encabezados con contenido real
    lines = []
    for el in main.find_all(["p", "li", "h1", "h2", "h3"]):
        text = el.get_text(strip=True)
        if text and text not in _BOILERPLATE and len(text) > 5:
            lines.append(text)

    content = "\n".join(lines)
    if len(content) < 50:
        return None

    return {
        "id": hashlib.md5(url.encode()).hexdigest(),
        "url": url,
        "title": title,
        "content": content,
        "category": category,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


# ─── 3. SCRAPING COMPLETO ────────────────────────────────────────────────────

def scrape() -> list[dict]:
    """Scrapea todo ayuda.ueno.com.py y guarda en JSON (con cache)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out = DATA_DIR / "ueno_articles.json"

    if out.exists():
        print(f"📂 Usando cache: {out}")
        return json.loads(out.read_text())

    session = requests.Session()

    # Nivel 1: secciones
    sections = discover_sections(session)
    print(f"📁 {len(sections)} secciones encontradas")
    time.sleep(DELAY)

    # Nivel 2: sub-secciones
    article_queue: list[tuple[str, str]] = []
    for sec_url in sections:
        subsections = discover_subsections(sec_url, session)
        time.sleep(DELAY)
        # Nivel 3: artículos en cada sub-sección
        for sub_url in subsections:
            articles_found = discover_articles(sub_url, session)
            article_queue.extend(articles_found)
            time.sleep(DELAY)

    # Deduplicar por URL
    seen: set[str] = set()
    unique_articles = []
    for url, cat in article_queue:
        if url not in seen:
            seen.add(url)
            unique_articles.append((url, cat))

    print(f"📄 {len(unique_articles)} artículos únicos descubiertos\n")

    # Scraping de cada artículo
    articles = []
    for i, (url, category) in enumerate(unique_articles, 1):
        print(f"[{i}/{len(unique_articles)}] {url}")
        soup = fetch(url, session)
        if soup:
            article = extract_article(soup, url, category)
            if article:
                articles.append(article)
                print(f"  ✅ '{article['title']}' ({len(article['content'].split())} palabras)")
            else:
                print(f"  ⚠ Sin contenido útil")
        time.sleep(DELAY)

    out.write_text(json.dumps(articles, ensure_ascii=False, indent=2))
    print(f"\n✅ {len(articles)} artículos guardados en {out}")
    return articles


# ─── 4. CHUNKING ─────────────────────────────────────────────────────────────

def chunk_articles(articles: list[dict]) -> list[dict]:
    """Divide artículos en fragmentos de ~400 tokens."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,      # ~375 tokens (1 token ≈ 4 chars en español)
        chunk_overlap=200,    # ~50 tokens de overlap
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for art in articles:
        texts = splitter.split_text(art["content"])
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
                }
            })

    print(f"✂️  {len(chunks)} chunks generados desde {len(articles)} artículos")
    return chunks


# ─── 5. EMBEDDINGS + CHROMADB ─────────────────────────────────────────────────

def embed_and_store(chunks: list[dict]):
    """Genera embeddings y los almacena en ChromaDB."""
    if not chunks:
        print("⚠ Sin chunks — abortando embed_and_store")
        return None

    print(f"\n🤖 Cargando modelo de embeddings ({EMBED_MODEL})...")
    print("   Primera vez descarga ~118MB — luego queda en cache")
    model = SentenceTransformer(EMBED_MODEL)

    print(f"🔢 Generando embeddings para {len(chunks)} chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=32)

    print(f"💾 Guardando en ChromaDB en {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        collection.add(
            ids=[c["id"] for c in batch],
            embeddings=embeddings[i:i + batch_size].tolist(),
            documents=[c["text"] for c in batch],
            metadatas=[c["metadata"] for c in batch],
        )
        print(f"   Batch {i // batch_size + 1}/{(len(chunks) - 1) // batch_size + 1} ✓")

    print(f"\n🎉 ChromaDB lista: {collection.count()} chunks indexados")
    return collection


# ─── PIPELINE PRINCIPAL ──────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Pipeline de Ingesta — Uendi RAG")
    print("=" * 50 + "\n")

    articles = scrape()
    chunks = chunk_articles(articles)
    embed_and_store(chunks)

    print("\n✅ ¡Ingesta completa! Ahora corre: streamlit run mvp/app.py")

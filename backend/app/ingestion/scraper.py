"""
scraper.py — Descubrimiento y extracción de artículos desde ayuda.ueno.com.py

Flujo: secciones → sub-secciones → artículos → contenido limpio
Respeta robots.txt implícitamente: 1 req cada DELAY segundos.
"""
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://ayuda.ueno.com.py"
DELAY = 1.5
HEADERS = {"User-Agent": "UendiRAGBot/1.0 (academico)"}

_BOILERPLATE = {
    "Inicio", "Chateá con uendi", "Centro de ayuda", "Contactanos",
    "Los 7 días, las 24 horas.", "Llamanos al", "+595 21 618 8000",
    "© 2025 ueno bank S.A.", "Todos los derechos reservados.",
}


def _fetch(url: str, session: requests.Session) -> BeautifulSoup | None:
    """Descarga una URL y retorna BeautifulSoup, o None si falla."""
    try:
        r = session.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except Exception as e:
        print(f"  ⚠ {url}: {e}")
        return None


def _strip_query(url: str) -> str:
    p = urlparse(url)
    return urlunparse((p.scheme, p.netloc, p.path, "", "", ""))


def _discover_sections(session: requests.Session) -> list[str]:
    soup = _fetch(BASE_URL, session)
    if not soup:
        return []
    return list(dict.fromkeys(
        urljoin(BASE_URL, a["href"])
        for a in soup.find_all("a", href=True)
        if "/section/" in a["href"] and BASE_URL in urljoin(BASE_URL, a["href"])
    ))


def _discover_subsections(section_url: str, session: requests.Session) -> list[str]:
    soup = _fetch(section_url, session)
    if not soup:
        return []
    return list(dict.fromkeys(
        urljoin(BASE_URL, a["href"])
        for a in soup.find_all("a", href=True)
        if "/sub-section/" in a["href"] and BASE_URL in urljoin(BASE_URL, a["href"])
    ))


def _discover_articles(subsection_url: str, session: requests.Session) -> list[tuple[str, str]]:
    soup = _fetch(subsection_url, session)
    if not soup:
        return []
    path = urlparse(subsection_url).path
    category = (
        path.split("/sub-section/")[-1].replace("%20", " ")
        if "/sub-section/" in path else "General"
    )
    seen: set[str] = set()
    result = []
    for a in soup.find_all("a", href=True):
        full = urljoin(BASE_URL, a["href"])
        if "/article/" in full and BASE_URL in full:
            clean = _strip_query(full)
            if clean not in seen:
                seen.add(clean)
                result.append((clean, category))
    return result


def _extract_article(soup: BeautifulSoup, url: str, category: str) -> dict | None:
    title_el = soup.select_one("h1")
    if not title_el:
        return None
    main = soup.select_one("main")
    if not main:
        return None
    for tag in main.find_all(["script", "style", "nav", "button", "footer"]):
        tag.decompose()
    lines = [
        el.get_text(strip=True)
        for el in main.find_all(["p", "li", "h1", "h2", "h3"])
        if el.get_text(strip=True) not in _BOILERPLATE and len(el.get_text(strip=True)) > 5
    ]
    content = "\n".join(lines)
    if len(content) < 50:
        return None
    return {
        "id": hashlib.md5(url.encode()).hexdigest(),
        "url": url,
        "title": title_el.get_text(strip=True),
        "content": content,
        "category": category,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def scrape(data_dir: Path) -> list[dict]:
    """
    Scrapea todo ayuda.ueno.com.py y guarda en JSON.
    Si el JSON ya existe lo usa como cache.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / "ueno_articles.json"

    if out.exists():
        print(f"📂 Cache encontrado: {out}")
        return json.loads(out.read_text())

    session = requests.Session()
    sections = _discover_sections(session)
    print(f"📁 {len(sections)} secciones")
    time.sleep(DELAY)

    article_queue: list[tuple[str, str]] = []
    for sec_url in sections:
        for sub_url in _discover_subsections(sec_url, session):
            time.sleep(DELAY)
            article_queue.extend(_discover_articles(sub_url, session))
            time.sleep(DELAY)

    seen: set[str] = set()
    unique = []
    for u, c in article_queue:
        if u not in seen:
            seen.add(u)
            unique.append((u, c))
    print(f"📄 {len(unique)} artículos únicos")

    articles = []
    for i, (url, category) in enumerate(unique, 1):
        print(f"[{i}/{len(unique)}] {url}")
        soup = _fetch(url, session)
        if soup:
            art = _extract_article(soup, url, category)
            if art:
                articles.append(art)
        time.sleep(DELAY)

    out.write_text(json.dumps(articles, ensure_ascii=False, indent=2))
    print(f"✅ {len(articles)} artículos guardados en {out}")
    return articles

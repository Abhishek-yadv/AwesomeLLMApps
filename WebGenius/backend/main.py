import asyncio
import datetime
import os
import json
import logging
import sys
from urllib.parse import urljoin, urlparse
from contextlib import asynccontextmanager
from collections import OrderedDict
from typing import Dict, Optional, Set, List, Tuple

import aiofiles
import httpx
from bs4 import BeautifulSoup, SoupStrainer, NavigableString
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# ✅ Load environment variables from a .env file for security
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'), override=True)

# Logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Models ---
class ScrapeRequest(BaseModel):
    url: HttpUrl

class ScrapeResponse(BaseModel):
    status: str
    message: str
    pages_found: int
    results: Optional[Dict[str, str]] = None
    pdf_filename: Optional[str] = None


# --- Global State & Lifespan Management ---
_browser = None

async def get_browser():
    global _browser
    if _browser is None:
        playwright = await async_playwright().start()
        _browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',  # Prevents /dev/shm issues in containers
                '--no-sandbox',  # Required for some container environments
                '--disable-gpu',  # Reduce memory usage
                '--disable-extensions',
                '--disable-background-networking',
                '--disable-sync',
                '--disable-translate',
                # NOTE: --single-process and --no-zygote removed - they cause crashes
            ]
        )
    return _browser

async def shutdown_browser():
    global _browser
    if _browser:
        await _browser.close()
        _browser = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Browser will be initialized on first use
    yield
    # This block runs on shutdown
    await shutdown_browser()

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Documentation Scraper API",
    description="An API to scrape and process documentation websites",
    version="2.1.0",  # ⚡ Updated: Performance optimizations applied
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("scraped_data", exist_ok=True)

# --- Enhanced Scraping Logic ---

async def extract_links_from_section(page, section_url, section_prefix):
    """Extract all documentation links from a section page"""
    # Normalize section_url by removing fragment if present
    parsed_section = urlparse(section_url)
    section_url = parsed_section._replace(fragment='').geturl()
    
    logger.info(f"Navigating to section: {section_url}")
    try:
        # Use 'domcontentloaded' for fastest load (no waiting for images/scripts)
        # This is most reliable on low-memory environments like Render free tier
        await page.goto(section_url, timeout=30000, wait_until="domcontentloaded")
        
        # Wait for common documentation containers
        try:
            await page.wait_for_selector('article, main, .content, #content', timeout=5000)
        except:
            logger.debug("No common content containers found, proceeding anyway")
        
    except Exception as e:
        logger.warning(f"Error navigating to {section_url}: {str(e)}")
        return []

    links = []
    seen = {section_url}  # Add the starting URL to avoid scraping it twice if linked
    base_domain = urlparse(section_url).netloc
    
    # Try multiple strategies to find links
    selectors = [
        'a[href]',  # All links
        'nav a[href]',  # Navigation links
        '.sidebar a[href]',  # Sidebar links
        '[role="navigation"] a[href]',  # Accessible navigation
        '.docs-sidebar a[href]',  # Common docs pattern
        '.menu a[href]',  # Menu links
    ]
    
    all_hrefs = set()
    # Use page.evaluate to extract hrefs directly, avoiding element handle issues
    try:
        for selector in selectors:
            try:
                hrefs = await page.evaluate('''
                    (selector) => {
                        const elements = document.querySelectorAll(selector);
                        return Array.from(elements).map(el => el.getAttribute('href')).filter(href => href);
                    }
                ''', selector)
                all_hrefs.update(hrefs)
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
    except Exception as e:
        logger.warning(f"Error extracting links: {e}")
        # Fallback: try to get at least some links
        return [section_url]
    
    for href in all_hrefs:
        if not href:
            continue
        
        # Skip anchor links that only have fragments (like #section)
        if href.startswith('#'):
            continue
        
        full_url = urljoin(section_url, href)
        parsed_url = urlparse(full_url)
        
        # Remove fragment (anchor) from URL to avoid duplicates
        # e.g., https://docs.agno.com/page#section becomes https://docs.agno.com/page
        url_without_fragment = parsed_url._replace(fragment='').geturl()
        
        # More flexible filter: same domain, part of the same doc section, and not yet seen
        if (parsed_url.netloc == base_domain and
            parsed_url.path.startswith(f"/{section_prefix}") and
            url_without_fragment not in seen and
            not url_without_fragment.endswith(('.pdf', '.zip', '.png', '.jpg', '.jpeg', '.gif'))):  # Skip non-HTML resources
            links.append(url_without_fragment)
            seen.add(url_without_fragment)
    
    logger.info(f"Found {len(links)} unique links in section {section_prefix}")
    
    # Ensure the initial page is first in the list (only if not already present)
    if section_url not in links:
        return [section_url] + links
    else:
        # Move section_url to the front if it's in links
        links.remove(section_url)
        return [section_url] + links


def _normalize_url_no_fragment(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    return parsed._replace(fragment='').geturl()


def extract_links_from_section_html(section_url: str, section_prefix: str, html: str) -> List[str]:
    """Extract documentation links from a section page HTML (fast path, no browser)."""
    section_url = _normalize_url_no_fragment(section_url)
    base_domain = urlparse(section_url).netloc

    # Parse only <a> tags for speed
    try:
        soup = BeautifulSoup(html, "lxml", parse_only=SoupStrainer("a"))
    except Exception:
        soup = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer("a"))

    links: List[str] = []
    seen = {section_url}
    for a in soup.find_all("a", href=True):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("#"):
            continue

        full_url = urljoin(section_url, href)
        full_url = _normalize_url_no_fragment(full_url)
        parsed_url = urlparse(full_url)

        if parsed_url.netloc != base_domain:
            continue
        if not parsed_url.path.startswith(f"/{section_prefix}"):
            continue
        if full_url in seen:
            continue
        if full_url.endswith((".pdf", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
            continue

        seen.add(full_url)
        links.append(full_url)

    if section_url in links:
        links.remove(section_url)
    return [section_url] + links


def extract_content_from_html_sync(url: str, html: str) -> str:
    """Extract and convert page content to markdown from raw HTML (CPU-bound, sync)."""
    try:
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")

        main_content = None
        content_selectors = [
            'article.bd-article',
            '.bd-article',
            '.bd-content',
            '.bd-article-container',
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.documentation',
            '.docs-content',
            '.markdown-body',
            '#content',
            '.doc-content',
            '.page-content'
        ]

        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.body

        if not main_content:
            return "No main content container found."

        selectors_to_remove = [
            "nav", ".nav", ".navbar", ".navigation", "[role='navigation']",
            ".sidebar", ".side-bar", ".menu", ".toc", ".table-of-contents",
            ".breadcrumb", ".breadcrumbs", ".pagination",
            ".bd-sidebar", ".bd-sidebar-primary", ".bd-sidebar-secondary",
            ".bd-toc", ".toc-tree", ".header-article__inner",
            "header", ".header", "footer", ".footer", "[role='contentinfo']", "[role='banner']",
            ".cookie", ".modal", ".popup", ".lightbox", ".overlay",
            ".search", ".search-box", ".site-search", ".search-form",
            ".edit-page-link", ".edit-link", ".github-link", ".edit-on-github",
            ".ad", ".advertisement", ".sponsored", ".promo", ".banner", ".announcement",
            ".hidden", "[style*='display:none']", "[style*='visibility:hidden']",
            "script", "style", "noscript",
            ".social", ".share", ".sharing", ".follow",
            ".page-controls", ".utility", ".tools", ".actions",
            ".sticky-header", ".floating", ".fixed",
            ".comments", ".feedback", ".rating"
        ]

        for selector in selectors_to_remove:
            for unwanted in main_content.select(selector):
                if unwanted.name in ['span', 'strong', 'em', 'b', 'i', 'code']:
                    continue
                if len(unwanted.get_text(strip=True)) > 30:
                    continue
                unwanted.decompose()

        title = soup.find("title")
        if title:
            title_text = title.get_text(strip=True)
            title_text = title_text.split('|')[0].split('-')[0].strip()
        else:
            h1_tag = main_content.find("h1")
            if h1_tag:
                title_text = h1_tag.get_text(strip=True)
            else:
                title_text = urlparse(url).path.split('/')[-1] or "Untitled Page"

        text_parts = [f"# {title_text}"]
        processed_elements: Set[int] = set()
        seen_content: Set[str] = set()

        def process_inline_elements(element):
            if isinstance(element, NavigableString):
                return str(element).strip()
            result = []
            for child in element.children:
                if isinstance(child, NavigableString):
                    text = str(child).strip()
                    if text:
                        result.append(text)
                elif hasattr(child, 'name'):
                    if child.name in ['ul', 'ol', 'table', 'pre', 'blockquote', 'div', 'section', 'article']:
                        continue
                    if child.name in ["strong", "b"]:
                        inner_content = process_inline_elements(child) or child.get_text(strip=True)
                        if inner_content:
                            result.append(f"**{inner_content}**")
                    elif child.name in ["em", "i"]:
                        inner_content = process_inline_elements(child) or child.get_text(strip=True)
                        if inner_content:
                            result.append(f"*{inner_content}*")
                    elif child.name == "code":
                        text = child.get_text(strip=True)
                        if text:
                            result.append(f"`{text}`")
                    elif child.name == "a":
                        href = child.get('href')
                        text = child.get_text(strip=True)
                        if text:
                            if href and not href.startswith('#'):
                                full_url = urljoin(url, href)
                                result.append(f"[{text}]({full_url})")
                            else:
                                result.append(text)
                    elif child.name == "br":
                        result.append("\n")
                    elif child.name == "span":
                        span_content = process_inline_elements(child)
                        if span_content:
                            result.append(span_content)
                    elif child.name in ["p", "div"]:
                        nested_content = process_inline_elements(child)
                        if nested_content:
                            result.append(nested_content)
                    else:
                        nested_content = process_inline_elements(child)
                        if nested_content:
                            result.append(nested_content)
                        else:
                            text = child.get_text(strip=True)
                            if text:
                                result.append(text)
            return " ".join(filter(None, result))

        def process_list(ul_ol, ordered=False, depth=0):
            items = []
            counter = 1
            for li in ul_ol.find_all("li", recursive=False):
                if id(li) in processed_elements:
                    continue
                processed_elements.add(id(li))

                li_content = process_inline_elements(li)

                nested_lists = []
                for child in li.find_all(["ul", "ol"], recursive=False):
                    if id(child) not in processed_elements:
                        nested = process_list(child, ordered=(child.name == "ol"), depth=depth + 1)
                        if nested:
                            nested_lists.append(nested)

                if li_content or nested_lists:
                    indent = "  " * depth
                    if ordered:
                        item_text = f"{indent}{counter}. {li_content}"
                        counter += 1
                    else:
                        item_text = f"{indent}- {li_content}"

                    items.append(item_text)
                    for nested in nested_lists:
                        items.append(nested)

            return "\n".join(items) + "\n" if items else ""

        def process_table(table):
            rows = []
            headers = []

            thead = table.find("thead")
            if thead:
                for th in thead.find_all("th"):
                    header_content = process_inline_elements(th)
                    headers.append(header_content or th.get_text(strip=True))
            else:
                first_row = table.find("tr")
                if first_row:
                    ths = first_row.find_all("th")
                    if ths:
                        for th in ths:
                            header_content = process_inline_elements(th)
                            headers.append(header_content or th.get_text(strip=True))

            if headers:
                rows.append("| " + " | ".join(headers) + " |")
                rows.append("|" + "|".join(["---" for _ in headers]) + "|")

            tbody = table.find("tbody") or table
            for tr in tbody.find_all("tr"):
                cells = []
                for td in tr.find_all(["td", "th"]):
                    cell_content = process_inline_elements(td) or td.get_text(strip=True)
                    cell_text = cell_content.replace("|", "\\|")
                    cells.append(cell_text)
                if cells and not (headers and cells == headers):
                    rows.append("| " + " | ".join(cells) + " |")

            return "\n" + "\n".join(rows) + "\n" if rows else ""

        def process_definition_list(dl):
            result = []
            dl_classes = dl.get('class', [])
            is_sphinx_def = any(cls.startswith('py') for cls in dl_classes) if dl_classes else False

            for child in dl.children:
                if hasattr(child, 'name'):
                    if id(child) not in processed_elements:
                        processed_elements.add(id(child))

                        if child.name == "dt":
                            sig_classes = child.get('class', [])
                            is_signature = 'sig' in sig_classes if sig_classes else False

                            if is_signature or is_sphinx_def:
                                sig_text = child.get_text(strip=True)
                                sig_text = sig_text.replace('[source]', '').replace('[#]', '').strip()
                                if sig_text:
                                    result.append(f"\n## {sig_text}\n")
                            else:
                                content = process_inline_elements(child)
                                if content:
                                    result.append(f"\n**{content}**")
                                else:
                                    term_text = child.get_text(strip=True)
                                    if term_text:
                                        result.append(f"\n**{term_text}**")

                        elif child.name == "dd":
                            dd_parts = []
                            for dd_child in child.children:
                                if hasattr(dd_child, 'name'):
                                    if id(dd_child) not in processed_elements:
                                        child_result = process_element(dd_child, depth=0)
                                        if child_result and child_result.strip():
                                            dd_parts.append(child_result)
                                elif isinstance(dd_child, NavigableString):
                                    text = str(dd_child).strip()
                                    if text and len(text) > 1:
                                        dd_parts.append(text)

                            if dd_parts:
                                result.append("\n".join(dd_parts))
                            else:
                                content = process_inline_elements(child)
                                if content:
                                    result.append(f": {content}")

            return "\n".join(result) + "\n" if result else ""

        def process_element(el, parent_processed=False, depth=0):
            if id(el) in processed_elements:
                return None
            element_text = el.get_text(strip=True)
            if not element_text:
                return None
            processed_elements.add(id(el))

            if el.name == "h1":
                text = el.get_text(strip=True)
                if text != title_text:
                    return f"\n# {text}\n"
            elif el.name == "h2":
                return f"\n## {el.get_text(strip=True)}\n"
            elif el.name == "h3":
                return f"\n### {el.get_text(strip=True)}\n"
            elif el.name == "h4":
                return f"\n#### {el.get_text(strip=True)}\n"
            elif el.name == "h5":
                return f"\n##### {el.get_text(strip=True)}\n"
            elif el.name == "h6":
                return f"\n###### {el.get_text(strip=True)}\n"
            elif el.name == "p":
                content = process_inline_elements(el)
                return content + "\n" if content else None
            elif el.name == "pre":
                code = el.find("code")
                if code:
                    lang = ""
                    if code.get("class"):
                        classes = code.get("class")
                        for cls in classes:
                            if "language-" in cls:
                                lang = cls.split("language-")[1].split()[0]
                                break
                    return f"\n```{lang}\n{code.get_text()}\n```\n"
                return f"\n```\n{el.get_text()}\n```\n"
            elif el.name == "code" and not parent_processed:
                return f"`{el.get_text(strip=True)}`"
            elif el.name == "ul":
                return process_list(el, ordered=False, depth=depth)
            elif el.name == "ol":
                return process_list(el, ordered=True, depth=depth)
            elif el.name == "blockquote":
                blockquote_parts = []
                for child in el.children:
                    if hasattr(child, 'name'):
                        if id(child) not in processed_elements:
                            child_result = process_element(child, parent_processed=True, depth=depth)
                            if child_result:
                                for line in child_result.split('\n'):
                                    if line.strip():
                                        blockquote_parts.append(f"> {line}")
                    elif isinstance(child, NavigableString):
                        text = str(child).strip()
                        if text:
                            blockquote_parts.append(f"> {text}")
                return "\n".join(blockquote_parts) + "\n" if blockquote_parts else None
            elif el.name == "table":
                return process_table(el)
            elif el.name in ["strong", "b"]:
                content = process_inline_elements(el)
                if content:
                    if not content.startswith('**'):
                        return f"**{content}**"
                    return content
            elif el.name in ["em", "i"]:
                content = process_inline_elements(el)
                if content:
                    if not content.startswith('*'):
                        return f"*{content}*"
                    return content
            elif el.name == "a" and not parent_processed:
                href = el.get('href')
                text = el.get_text(strip=True)
                if href and not href.startswith('#'):
                    full_url = urljoin(url, href)
                    return f"[{text}]({full_url})"
                return text
            elif el.name == "img":
                alt_text = el.get('alt', '')
                src = el.get('src', '')
                if src:
                    full_url = urljoin(url, src)
                    return f"![{alt_text or 'Image'}]({full_url})"
            elif el.name == "hr":
                return "\n---\n"
            elif el.name == "span":
                content = process_inline_elements(el)
                if content:
                    return content
            elif el.name in ["div", "section", "article", "main", "aside", "tip", "note", "warning", "info"]:
                element_class = el.get('class', [])
                is_tip = el.name.lower() == 'tip' or 'tip' in str(element_class).lower()
                is_note = el.name.lower() == 'note' or 'note' in str(element_class).lower()
                is_warning = el.name.lower() == 'warning' or 'warning' in str(element_class).lower()

                results = []
                if is_tip:
                    results.append("\n💡 **Tip:**\n")
                elif is_note:
                    results.append("\n📝 **Note:**\n")
                elif is_warning:
                    results.append("\n⚠️ **Warning:**\n")

                for child in el.children:
                    if hasattr(child, 'name'):
                        if id(child) not in processed_elements:
                            result = process_element(child, depth=depth)
                            if result:
                                results.append(result)
                    elif isinstance(child, NavigableString):
                        text = str(child).strip()
                        if text and len(text) > 1:
                            results.append(text)
                return "\n".join(results) if results else None
            elif el.name == "dl":
                return process_definition_list(el)
            elif el.name == "details":
                summary = el.find("summary")
                if summary:
                    details_content = f"\n<details>\n<summary>{summary.get_text(strip=True)}</summary>\n\n"
                    for child in el.children:
                        if hasattr(child, 'name') and child.name != "summary":
                            if id(child) not in processed_elements:
                                result = process_element(child, depth=depth)
                                if result:
                                    details_content += result
                    details_content += "\n</details>\n"
                    return details_content
            else:
                content = process_inline_elements(el)
                if content:
                    return content
            return None

        for element in main_content.children:
            if hasattr(element, 'name') and element.name:
                if id(element) not in processed_elements:
                    result = process_element(element)
                    if result and result.strip():
                        normalized = result.strip().lower()
                        if normalized not in seen_content:
                            text_parts.append(result)
                            seen_content.add(normalized)

        content = "\n".join(text_parts)

        import re
        content = re.sub(r'\n{3,}', '\n\n', content)

        lines = content.split('\n')
        cleaned_lines = []
        prev_line = None
        for line in lines:
            stripped_line = line.strip()
            if stripped_line == '' and prev_line == '':
                continue
            if stripped_line != prev_line:
                cleaned_lines.append(line.rstrip())
            prev_line = stripped_line
        content = "\n".join(cleaned_lines)

        content = re.sub(r'(```[\s\S]*?)\n(\1)', r'\1', content)
        content = re.sub(r'(#+\s+[^\n]+)\n+\1', r'\1', content)
        content = re.sub(r'(\[[^\]]+\]\([^)]+\))\s+\1', r'\1', content)

        paragraphs = content.split('\n\n')
        unique_paragraphs = []
        seen_paragraph_hashes = set()
        for paragraph in paragraphs:
            normalized_para = paragraph.strip().lower()
            para_hash = hash(normalized_para)
            if para_hash not in seen_paragraph_hashes and normalized_para:
                unique_paragraphs.append(paragraph)
                seen_paragraph_hashes.add(para_hash)
        content = '\n\n'.join(unique_paragraphs)

        lines = content.split('\n')
        seen_line_hashes = set()
        unique_lines = []
        in_code_block = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                unique_lines.append(line)
                continue
            if in_code_block:
                unique_lines.append(line)
                continue
            if stripped:
                line_hash = hash(stripped.lower())
                if line_hash not in seen_line_hashes or len(stripped) < 3:
                    unique_lines.append(line)
                    seen_line_hashes.add(line_hash)
            else:
                if unique_lines and unique_lines[-1].strip():
                    unique_lines.append(line)

        return '\n'.join(unique_lines).strip()

    except Exception as e:
        logger.error(f"Failed to extract content from html for {url}: {str(e)}", exc_info=True)
        return f"⚠️ Failed to process {url}: {str(e)}"


async def extract_content_from_html(url: str, html: str) -> str:
    # BeautifulSoup parsing is CPU-bound; run off the event loop to keep concurrency high
    return await asyncio.to_thread(extract_content_from_html_sync, url, html)


async def extract_content_from_page(page, url):
    """Extract and convert page content to markdown with improved parsing"""
    try:
        logger.info(f"Extracting content from: {url}")
        # Use 'domcontentloaded' for fastest load - most reliable on low-memory environments
        await page.goto(url, timeout=30000, wait_until="domcontentloaded")
        
        # Wait for content to load
        try:
            await page.wait_for_selector('article, main, .content, #content, .documentation-content, .markdown-body', timeout=5000)
        except:
            logger.debug(f"No specific content container found for {url}, using body")

        html = await page.content()
        content = await extract_content_from_html(url, html)

        logger.info(f"Successfully extracted {len(content)} characters from {url}")
        return content

    except Exception as e:
        logger.error(f"Failed to extract content from {url}: {str(e)}", exc_info=True)
        return f"⚠️ Failed to process {url}: {str(e)}"


def convert_to_markdown(results: Dict[str, str]) -> str:
    """Convert the scraped results to a clean Markdown format"""
    markdown_content = []
    
    for url, content in results.items():
        # Add a heading with the URL as a link
        markdown_content.append(f"# Source: [{url}]({url})\n")
        # Add the content with proper formatting
        markdown_content.append(content)
        # Add a horizontal separator between different pages
        markdown_content.append("\n---\n")
    
    return "\n".join(markdown_content)


async def scrape_section(base_url, section):
    """Main function to scrape a documentation section"""
    section_url = f"{base_url}/{section}"
    ordered_results = OrderedDict()
    user_agent = os.getenv(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )

    max_concurrent = int(os.getenv("SCRAPER_MAX_CONCURRENT", "20"))
    max_concurrent = max(1, min(max_concurrent, 50))
    http_only = os.getenv("SCRAPER_HTTP_ONLY", "0") == "1"
    fallback_to_playwright = os.getenv("SCRAPER_FALLBACK_PLAYWRIGHT", "1") != "0"

    timeout = httpx.Timeout(connect=10.0, read=30.0, write=30.0, pool=10.0)
    limits = httpx.Limits(
        max_connections=max_concurrent * 4,
        max_keepalive_connections=max_concurrent * 2,
        keepalive_expiry=30.0,
    )
    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async def fetch_html(client: httpx.AsyncClient, url: str, max_retries: int = 2) -> Optional[str]:
        url = _normalize_url_no_fragment(url)
        last_error: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            try:
                resp = await client.get(url)
                # Some docs return 403 without a UA; treat non-2xx as failure
                resp.raise_for_status()
                # Skip non-HTML
                ctype = (resp.headers.get("content-type") or "").lower()
                if "text/html" not in ctype and "application/xhtml" not in ctype and "application/xml" not in ctype:
                    return None
                return resp.text
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    await asyncio.sleep(0.3 * (2 ** attempt))
                else:
                    logger.warning(f"HTTP fetch failed for {url}: {e}")
        logger.debug(f"HTTP fetch failed (final) for {url}: {last_error}")
        return None

    links: List[str] = []
    try:
        client_cm = httpx.AsyncClient(
            http2=True,
            follow_redirects=True,
            timeout=timeout,
            limits=limits,
            headers=headers,
        )
    except (RuntimeError, ImportError) as e:
        # httpx raises at client construction time when http2=True but 'h2' isn't installed.
        msg = str(e)
        if "http2" in msg.lower() and "h2" in msg.lower():
            logger.warning("HTTP/2 requested but 'h2' is not installed; falling back to HTTP/1.1")
            client_cm = httpx.AsyncClient(
                http2=False,
                follow_redirects=True,
                timeout=timeout,
                limits=limits,
                headers=headers,
            )
        else:
            raise

    async with client_cm as client:
        section_html = await fetch_html(client, section_url)
        if section_html:
            links = extract_links_from_section_html(section_url, section, section_html)
            logger.info(f"(HTTP) Found {len(links)} page(s) under section /{section}")

        # Fallback for link discovery on JS-heavy docs
        context = None
        if (not links) and fallback_to_playwright and not http_only:
            browser = await get_browser()
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent=user_agent,
                locale='en-US',
                timezone_id='America/New_York',
                ignore_https_errors=True,
                java_script_enabled=True,
            )

            blocked_resources = ["image", "stylesheet", "font", "media", "websocket", "manifest", "other"]
            await context.route("**/*", lambda route: (
                route.abort() if route.request.resource_type in blocked_resources
                else route.continue_()
            ))
            page = await context.new_page()
            try:
                links = await extract_links_from_section(page, section_url, section)
                logger.info(f"(Playwright) Found {len(links)} page(s) under section /{section}")
            finally:
                await page.close()

        if not links:
            links = [section_url]

        semaphore = asyncio.Semaphore(max_concurrent)

        async def scrape_one(link: str) -> Tuple[str, str]:
            link = _normalize_url_no_fragment(link)
            async with semaphore:
                html = await fetch_html(client, link)
                if html:
                    content = await extract_content_from_html(link, html)
                    # If extraction looks empty, optionally fall back to Playwright
                    if (len(content.strip()) >= 50) or http_only or not fallback_to_playwright:
                        return (link, content)

                if http_only or not fallback_to_playwright:
                    return (link, f"⚠️ Failed to fetch/parse {link} via HTTP")

                nonlocal context
                if context is None:
                    browser = await get_browser()
                    context = await browser.new_context(
                        viewport={"width": 1280, "height": 720},
                        user_agent=user_agent,
                        locale='en-US',
                        timezone_id='America/New_York',
                        ignore_https_errors=True,
                        java_script_enabled=True,
                    )
                    blocked_resources = ["image", "stylesheet", "font", "media", "websocket", "manifest", "other"]
                    await context.route("**/*", lambda route: (
                        route.abort() if route.request.resource_type in blocked_resources
                        else route.continue_()
                    ))

                page = await context.new_page()
                try:
                    content = await extract_content_from_page(page, link)
                    return (link, content)
                finally:
                    await page.close()

        # Fire off concurrent tasks, then re-order by the original link order
        tasks = [asyncio.create_task(scrape_one(link)) for link in links]
        results = await asyncio.gather(*tasks)

        results_map = {link: content for link, content in results}
        for link in links:
            content = results_map.get(_normalize_url_no_fragment(link))
            if content and len(content.strip()) > 50:
                ordered_results[_normalize_url_no_fragment(link)] = content
            else:
                logger.warning(f"Skipping {link} - insufficient content extracted")

        if context is not None:
            await context.close()

    # Save results
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON version
    json_filename = f"scraped_data/{section.replace('/', '_')}_{timestamp}.json"
    async with aiofiles.open(json_filename, "w", encoding="utf-8") as f:
        await f.write(json.dumps(ordered_results, ensure_ascii=False, indent=2))
    
    # Save Markdown version
    markdown_content = convert_to_markdown(ordered_results)
    md_filename = f"scraped_data/{section.replace('/', '_')}_{timestamp}.md"
    async with aiofiles.open(md_filename, "w", encoding="utf-8") as f:
        await f.write(markdown_content)
    
    logger.info(f"Saved {len(ordered_results)} pages to {json_filename} and {md_filename}")

    return ordered_results, json_filename


# --- External Services (Groq API - Optional) ---

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

async def chunk_text(text: str, max_chunk_size: int = 10000) -> list:
    """Split text into chunks of specified size without breaking sentences"""
    if len(text) <= max_chunk_size:
        return [text]
    
    chunks = []
    paragraphs = text.split('\n\n')
    
    current_chunk = ""
    for paragraph in paragraphs:
        if len(current_chunk + paragraph) <= max_chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if len(paragraph) > max_chunk_size:
                sentences = paragraph.split('.')
                temp_chunk = ""
                for sentence in sentences:
                    sentence += '.'
                    if len(temp_chunk + sentence) <= max_chunk_size:
                        temp_chunk += sentence
                    else:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                            temp_chunk = sentence
                        else:
                            chunks.append(sentence.strip())
                            temp_chunk = ""
                if temp_chunk:
                    chunks.append(temp_chunk.strip())
            else:
                current_chunk = paragraph + "\n\n"
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


# --- API Routes ---

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.get("/api/list-scraped-data")
async def list_scraped_data():
    try:
        files = []
        for f in os.listdir("scraped_data"):
            if f.endswith(('.json', '.pdf', '.md')):
                file_path = os.path.join("scraped_data", f)
                file_stats = os.stat(file_path)
                files.append({
                    "filename": f,
                    "size": file_stats.st_size,
                    "modified": datetime.datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                })
        return {"files": files}
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing files: {str(e)}"
        )

@app.get("/api/get-scraped-data/{filename}")
async def get_scraped_data(filename: str):
    try:
        file_path = os.path.join("scraped_data", filename)
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"File {filename} not found"
            )

        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            if filename.endswith('.json'):
                data = json.loads(await f.read())
            else:
                data = await f.read()

        return {"filename": filename, "content": data}
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )

@app.post("/api/scrape", response_model=ScrapeResponse)
async def scrape_endpoint(scrape_req: ScrapeRequest):
    try:
        url = str(scrape_req.url)
        
        # Robust URL parsing
        parsed_url = urlparse(url.rstrip('/'))
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        path_parts = [part for part in parsed_url.path.split('/') if part]
        
        if not path_parts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL must include a section path (e.g., https://docs.example.com/section)"
            )
        
        # Handle multi-level paths
        section = '/'.join(path_parts)
        
        logger.info(f"Starting scrape - URL: {url}, Base: {base_url}, Section: {section}")

        # Scrape the section
        results, json_filename = await scrape_section(base_url, section)

        if not results:
            return ScrapeResponse(
                status="warning",
                message=f"No content could be extracted from {url}",
                pages_found=0,
                results=None,
                pdf_filename=None
            )

        return ScrapeResponse(
            status="success",
            message=f"Successfully scraped {len(results)} pages from {base_url}/{section}",
            pages_found=len(results),
            results=results,
            pdf_filename=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scrape endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal error occurred: {str(e)}"
        )

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("scraped_data", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if filename.endswith(".pdf"):
        media_type = "application/pdf"
    elif filename.endswith(".json"):
        media_type = "application/json"
    elif filename.endswith(".md"):
        media_type = "text/markdown"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(file_path, media_type=media_type, filename=filename)


# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*50)
    print("📚 Documentation Scraper API v2.0")
    print("="*50)
    print("\n✅ Server starting...")
    
    if not GROQ_API_KEY:
        print("⚠️  WARNING: GROQ_API_KEY not set (content enhancement disabled)")
    else:
        print("✅ GROQ API key loaded")
    
    print("\n📍 Access points:")
    print("   • API endpoint: http://localhost:5000")
    print("   • API documentation: http://localhost:5000/docs")
    print("   • Health check: http://localhost:5000/api/health")
    print("\n" + "="*50 + "\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=5000,
        log_level="info"
    )
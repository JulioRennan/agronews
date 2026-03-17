"""
Módulo de Busca de Notícias - Google News Fetcher
Busca notícias sobre IA no Google News via RSS e extrai o conteúdo completo
"""

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pygooglenews import GoogleNews
from newspaper import Article, Config
from googlenewsdecoder import new_decoderv1
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import requests

# Configurações
TOPICOS = [
    # Foundation Models
    'OpenAI',              # GPT, o1, Sora
    'Anthropic Claude',    # Claude models
    'Google Gemini',       # Gemini models
    'Meta Llama AI',       # Open-source leader
    # Trends & Applications
    'AI agents',           # Autonomous agents
    'AI coding tools',     # Cursor, Copilot, etc.
    'multimodal AI',       # Vision, audio, video
    # Business & Policy
    'AI regulation',       # Governance
    'AI startup funding',  # Investment flow
    # Infrastructure
    'NVIDIA AI chips',     # Compute backbone
]
MAX_RESULTS = 5   # por tópico
PERIOD = '1d'     # últimas 24 horas


HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )
}


def resolver_url(url):
    """
    Decodifica a URL do Google News para obter a URL real do artigo.
    """
    try:
        result = new_decoderv1(url)
        if result.get('status'):
            print(f"  [decoded] {result['decoded_url'][:80]}")
            return result['decoded_url']
        print(f"  [decode falhou] {url[:60]}")
        return url
    except Exception as e:
        print(f"  [decode erro] {e}")
        return url


NEWSPAPER_CONFIG = Config()
NEWSPAPER_CONFIG.browser_user_agent = HEADERS['User-Agent']
NEWSPAPER_CONFIG.request_timeout = 15


def extrair_conteudo_headless(url_real):
    """
    Fallback: extrai o conteúdo usando Playwright com stealth (headless browser).
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS['User-Agent'],
                viewport={'width': 1280, 'height': 800},
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                }
            )
            page = context.new_page()
            Stealth().apply_stealth_sync(page)
            page.goto(url_real, timeout=20000, wait_until='networkidle')
            html = page.content()
            browser.close()

        article = Article(url_real, config=NEWSPAPER_CONFIG)
        article.download(input_html=html)
        article.parse()
        print(f"  [headless] {len(article.text)} chars de {url_real[:60]}")
        return article.text
    except Exception as e:
        print(f"  [headless erro] {e}")
        return ''


def extrair_conteudo(url_real):
    """
    Extrai o conteúdo completo do artigo. Usa newspaper3k e cai para
    Playwright se o conteúdo vier vazio.

    Returns:
        tuple: (content: str, method: str) onde method é 'direto', 'fallback' ou 'falhou'
    """
    try:
        article = Article(url_real, config=NEWSPAPER_CONFIG)
        article.download()
        article.parse()
        if article.text:
            print(f"  [conteudo] {len(article.text)} chars de {url_real[:60]}")
            return article.text, 'direto'
    except Exception as e:
        print(f"  [conteudo erro] {e}")

    print(f"  [fallback headless] {url_real[:60]}")
    texto = extrair_conteudo_headless(url_real)
    method = 'fallback' if texto else 'falhou'
    return texto, method


def buscar_noticias_por_topico(topico, max_results):
    """
    Busca notícias de um tópico específico no Google News e extrai o conteúdo completo.

    Args:
        topico (str): Tópico a ser buscado
        max_results (int): Número máximo de resultados

    Returns:
        list: Lista de dicionários com as notícias encontradas
    """
    try:
        gn = GoogleNews(lang='en', country='US')
        results = gn.search(topico, when=PERIOD)
        entries = results.get('entries', [])[:max_results]

        noticias = []
        for entry in entries:
            url_google = entry.get('link', '')
            url_real = resolver_url(url_google)
            conteudo, method = extrair_conteudo(url_real)

            noticias.append({
                'title': entry.get('title', ''),
                'description': entry.get('summary', ''),
                'url': url_real,
                'source': entry.get('source', {}).get('title', ''),
                'published_date': entry.get('published', ''),
                'topic': topico,
                'content': conteudo,
                '_extraction_method': method,
            })

        return noticias

    except Exception as e:
        print(f"Erro ao buscar notícias para '{topico}': {e}")
        return []


def remover_duplicatas(noticias):
    """
    Remove notícias duplicadas por URL.

    Args:
        noticias (list): Lista de notícias

    Returns:
        list: Lista de notícias sem duplicatas
    """
    urls_vistas = set()
    noticias_unicas = []

    for noticia in noticias:
        url = noticia.get('url', '')
        if url and url not in urls_vistas:
            urls_vistas.add(url)
            noticias_unicas.append(noticia)

    return noticias_unicas


def buscar_todas_noticias():
    """
    Busca notícias de todos os tópicos em paralelo e extrai o conteúdo completo.

    Returns:
        dict: Dicionário com timestamp, total e lista de notícias com conteúdo
    """
    todas_noticias = []

    print("Buscando notícias e extraindo conteúdo...")
    with ThreadPoolExecutor(max_workers=len(TOPICOS)) as executor:
        futures = {
            executor.submit(buscar_noticias_por_topico, topico, MAX_RESULTS): topico
            for topico in TOPICOS
        }

        for future in as_completed(futures):
            try:
                noticias = future.result()
                todas_noticias.extend(noticias)
            except Exception as e:
                print(f"Erro ao processar resultado: {e}")

    noticias_unicas = remover_duplicatas(todas_noticias)

    stats = {
        'direct': sum(1 for n in noticias_unicas if n['_extraction_method'] == 'direto'),
        'fallback': sum(1 for n in noticias_unicas if n['_extraction_method'] == 'fallback'),
        'failed': sum(1 for n in noticias_unicas if n['_extraction_method'] == 'falhou'),
    }

    for noticia in noticias_unicas:
        del noticia['_extraction_method']

    print(f"✓ Done: {len(noticias_unicas)} news | direct: {stats['direct']} | fallback: {stats['fallback']} | failed: {stats['failed']}")

    return {
        'timestamp': datetime.now().isoformat(),
        'total_news': len(noticias_unicas),
        'extraction_stats': stats,
        'news': noticias_unicas
    }

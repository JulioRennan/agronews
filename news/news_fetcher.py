"""
Módulo de Busca de Notícias - Google News Fetcher
Busca notícias sobre IA no Google News via RSS e extrai o conteúdo completo
"""

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from pygooglenews import GoogleNews

# Configurações
TOPICOS = [
    'OpenAI',              # GPT, DALL-E
    'Anthropic',           # Claude
    'Google DeepMind',     # Gemini, pesquisar
    'AI agents',           # tendência de agentes (pega OpenClaw também)
    'AI regulation',       # governança e política
    'AI breakthrough',     # descobertas científicas
]
MAX_RESULTS = 2   # por tópico
PERIOD = '1d'     # últimas 24 horas




def buscar_noticias_por_topico(topico, max_results):
    """
    Busca notícias de um tópico específico no Google News e extrai o conteúdo completo

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
            noticias.append({
                'title': entry.get('title', ''),
                'description': entry.get('summary', ''),
                'url': entry.get('link', ''),
                'source': entry.get('source', {}).get('title', ''),
                'published_date': entry.get('published', ''),
                'topic': topico,
            })

        return noticias

    except Exception as e:
        print(f"Erro ao buscar notícias para '{topico}': {e}")
        return []


def remover_duplicatas(noticias):
    """
    Remove notícias duplicadas por URL

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
    Busca notícias de todos os tópicos em paralelo e extrai o conteúdo completo

    Returns:
        dict: Dicionário com timestamp, total e lista de notícias com conteúdo
    """
    todas_noticias = []

    # Buscar notícias (com conteúdo) em paralelo usando ThreadPoolExecutor
    print("Buscando notícias e extraindo conteúdo...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submeter todas as buscas (scraping incluído)
        futures = {
            executor.submit(buscar_noticias_por_topico, topico, MAX_RESULTS): topico
            for topico in TOPICOS
        }

        # Coletar resultados conforme completam
        for future in as_completed(futures):
            try:
                noticias = future.result()
                todas_noticias.extend(noticias)
            except Exception as e:
                print(f"Erro ao processar resultado: {e}")
    
    # Remover duplicatas
    noticias_unicas = remover_duplicatas(todas_noticias)


    print(f"✓ Concluído: {len(noticias_unicas)} notícias únicas com conteúdo")

    return {
        'timestamp': datetime.now().isoformat(),
        'total_news': len(noticias_unicas),
        'news': noticias_unicas
    }

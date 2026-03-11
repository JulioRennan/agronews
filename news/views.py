from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .news_fetcher import buscar_todas_noticias


@api_view(['GET'])
def get_news(request):
    """
    Endpoint para buscar notícias sobre IA

    GET /api/news/

    Returns:
        JSON com timestamp, total_news e lista de notícias
    """
    try:
        dados = buscar_todas_noticias()
        return Response(dados, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """
    Endpoint de health check

    GET /api/health/
    """
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)

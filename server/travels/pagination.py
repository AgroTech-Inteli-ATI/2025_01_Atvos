from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Paginação customizada com:
    - 20 itens por página (padrão)
    - Possibilidade de customizar via ?limit=
    - Máximo de 100 itens por página
    """
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        Retorna resposta paginada no formato padrão do projeto
        """
        return {
            'success': True,
            'data': data,
            'pagination': {
                'page': self.page.number,
                'limit': self.page.paginator.per_page,
                'total': self.page.paginator.count,
                'totalPages': self.page.paginator.num_pages
            }
        }
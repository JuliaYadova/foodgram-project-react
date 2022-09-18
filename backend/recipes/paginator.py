from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPagination(PageNumberPagination):
    """Согласно ТЗ внесены правки в родительский класс пагинатора.
    Определены параметры для вывода требуемого количества страниц.
    """
    page_size = 6
    page_size_query_param = 'limit'

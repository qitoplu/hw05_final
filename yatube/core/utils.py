from django.core.paginator import Paginator

POSTS_QUANTITY = 10


def paginatorr(post_list, request):
    paginator = Paginator(post_list, POSTS_QUANTITY)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

from django.core.paginator import Paginator

from yatube.settings import POSTS_LIMIT


def get_page_object(post_list, request):
    paginator = Paginator(post_list, POSTS_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj

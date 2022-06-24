from django.core.paginator import Paginator
from django.conf import settings


def posts_paginator(request, post_list):
    paginator = Paginator(post_list, settings.CONSTANTS['POSTS_PER_PAGE'])
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
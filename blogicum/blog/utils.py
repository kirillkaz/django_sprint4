from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Post


def post_all_query():
    query_set = (
        Post.objects.select_related(
            "category",
            "location",
            "author",
        )
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )
    return query_set


def post_published_query():
    """Вернуть опубликованные посты."""
    query_set = post_all_query().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    return query_set


def get_post_data(post_data):
    """Вернуть данные поста"""
    post = get_object_or_404(
        Post,
        pk=post_data["pk"],
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    return post

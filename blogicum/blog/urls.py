from django.urls import path

from . import views

app_name = "blog"

main_urls = [
    path(
        "",
        views.MainPostListView.as_view(),
        name="index",
    ),
]

category_urls = [
    path(
        "category/<slug:category_slug>/",
        views.CategoryPostListView.as_view(),
        name="category_posts",
    ),
]

posts_urls = [
    path(
        "posts/<int:pk>/",
        views.PostDetailView.as_view(),
        name="post_detail",
    ),
    path(
        "posts/create/",
        views.PostCreateView.as_view(),
        name="create_post",
    ),
    path(
        "posts/<int:pk>/edit/",
        views.PostUpdateView.as_view(),
        name="edit_post",
    ),
    path(
        "posts/<int:pk>/delete/",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
]

comment_urls = [
    # Добавить комментарий.
    path(
        "posts/<int:pk>/comment/",
        views.CommentCreateView.as_view(),
        name="add_comment",
    ),
    # Редактировать комментарий.
    path(
        "posts/<int:pk>/edit_comment/<int:comment_pk>/",
        views.CommentUpdateView.as_view(),
        name="edit_comment",
    ),
    # Удалить комментарий
    path(
        "posts/<int:pk>/delete_comment/<int:comment_pk>/",
        views.CommentDeleteView.as_view(),
        name="delete_comment",
    ),
]

user_urls = [
    path(
        "profile/<slug:username>/",
        views.UserPostsListView.as_view(),
        name="profile",
    ),
    # Редактировать профиля пользователя.
    path(
        "edit_profile/",
        views.UserProfileUpdateView.as_view(),
        name="edit_profile",
    ),
]

urlpatterns = sum(
    [
        main_urls,
        category_urls,
        posts_urls,
        comment_urls,
        user_urls,
    ],
    list(),
)

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentEditForm, PostEditForm, UserEditForm
from .models import Category, Comment, Post, User
from .utils import get_post_data, post_all_query, post_published_query


class CommentMixinView(LoginRequiredMixin, View):
    """Mixin для редактирования и удаления комментария"""

    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_pk"

    def dispatch(self, request, *args, **kwargs):
        """Проверка на то, является ли пользователь автором коммента"""
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        get_post_data(self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("blog:post_detail", kwargs={"pk": pk})


class MainPostListView(ListView):
    """Главная страница со списком постов"""

    model = Post
    template_name = "blog/index.html"
    queryset = post_published_query()
    paginate_by = 10


class CategoryPostListView(MainPostListView):
    """Страница со списком постов выбранной категории"""

    template_name = "blog/category.html"
    category = None

    def get_queryset(self):
        slug = self.kwargs["category_slug"]
        self.category = get_object_or_404(
            Category,
            slug=slug,
            is_published=True,
        )
        return super().get_queryset().filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class UserPostsListView(MainPostListView):
    """Страница со списком постов пользователя"""

    template_name = "blog/profile.html"
    author = None

    def get_queryset(self):
        username = self.kwargs["username"]
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            return post_all_query().filter(author=self.author)
        return super().get_queryset().filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.author
        return context


class PostDetailView(DetailView):
    """Страница выбранного поста"""

    model = Post
    template_name = "blog/detail.html"
    post_data = None

    def get_queryset(self):
        self.post_data = get_object_or_404(Post, pk=self.kwargs["pk"])
        if self.post_data.author == self.request.user:
            return post_all_query().filter(pk=self.kwargs["pk"])
        return post_published_query().filter(pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentEditForm()
        context["comments"] = (self.object
                               .comments.all()
                               .select_related("author"))
        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление профиля пользователя"""

    model = User
    form_class = UserEditForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста"""

    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse("blog:profile", kwargs={"username": username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование поста"""

    model = Post
    form_class = PostEditForm
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("blog:post_detail", kwargs={"pk": pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление поста"""

    model = Post
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return redirect("blog:post_detail", pk=self.kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostEditForm(instance=self.object)
        return context

    def get_success_url(self):
        username = self.request.user
        return reverse_lazy("blog:profile", kwargs={"username": username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария"""

    model = Comment
    form_class = CommentEditForm
    template_name = "blog/comment.html"
    post_data = None

    def dispatch(self, request, *args, **kwargs):
        self.post_data = get_post_data(self.kwargs)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_data
        if self.post_data.author != self.request.user:
            self.send_author_email()
        return super().form_valid(form)

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return reverse("blog:post_detail", kwargs={"pk": pk})

    def send_author_email(self):
        post_url = self.request.build_absolute_uri(self.get_success_url())
        recipient_email = self.post_data.author.email
        subject = "New comment"
        message = (
            f"Пользователь {self.request.user} добавил "
            f"комментарий к посту {self.post_data.title}.\n"
            f"Читать комментарий {post_url}"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email="from@example.com",
            recipient_list=[recipient_email],
            fail_silently=True,
        )


class CommentUpdateView(CommentMixinView, UpdateView):
    """Редактирование комментария.

    CommentMixinView: Базовый класс, предоставляющий функциональность.

    Атрибуты:
        - form_class: Класс формы, используемый для редактирования
        комментария.
    """

    form_class = CommentEditForm


class CommentDeleteView(CommentMixinView, DeleteView):
    """Удаление комментария.

    CommentMixinView: Базовый класс, предоставляющий функциональность.
    """

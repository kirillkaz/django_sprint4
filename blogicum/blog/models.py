from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=256,
        verbose_name="Название места",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=256,
        verbose_name="Заголовок",
    )
    description = models.TextField(
        verbose_name="Описание",
    )
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text="Идентификатор страницы для URL;"
        " разрешены символы латиницы, цифры, дефис и подчёркивание.",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=256,
        verbose_name="Заголовок",
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text="Если установить дату и время в будущем"
        " — можно делать отложенные публикации.",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    image = models.ImageField(
        upload_to="images",
        blank=True,
        verbose_name="Изображение",
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"


class Comment(models.Model):
    text = models.TextField(
        verbose_name="Комментарий",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено",
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        default_related_name = "comments"
        ordering = ("created_at",)

    def __str__(self):
        return f"Комментарий пользователя {self.author}"

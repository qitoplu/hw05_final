from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

CONSTANT_SYMBOLS = 15


class Post(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = ('Посты')
        verbose_name_plural = ('Посты')
        ordering = ['pub_date']

    def __str__(self):
        return self.text[:CONSTANT_SYMBOLS]


class Group(models.Model):
    title = models.CharField(verbose_name='Заголовок', max_length=200)
    slug = models.SlugField(verbose_name='Слаг', unique=True)
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = ('Группы')
        verbose_name_plural = ('Группы')

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации комментария',
        db_index=True
    )

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        unique_together = ['user', 'author']

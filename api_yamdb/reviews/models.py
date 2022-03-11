from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year


class User(AbstractUser):
    """Настраиваемая модель пользователя"""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]
    email = models.EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль пользователя',
        max_length=12,
        choices=ROLE_CHOICES,
        default=USER
    )
    REQUIRED_FIELDS = ['email', ]

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email',
            )
        ]

    def __str__(self):
        return f'{self.username} {self.email} {self.role}'


class Category(models.Model):
    """Модель категорий для произведений"""
    name = models.CharField(max_length=30, verbose_name='category name')
    slug = models.SlugField(
        max_length=30,
        unique=True,
        verbose_name='category slug'
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель жанров для произведений"""
    name = models.CharField(max_length=30, verbose_name='genre name')
    slug = models.SlugField(
        max_length=30,
        unique=True,
        verbose_name='genre slug'
    )

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведений"""
    name = models.CharField(max_length=90, verbose_name='title name')
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='create year'
    )
    description = models.TextField(
        max_length=200,
        blank=True,
        db_index=True,
        verbose_name='description'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='genre'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='titles',
        verbose_name='category'
    )

    class Meta:
        ordering = ('year',)
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self):
        return self.name[:10]


class Review(models.Model):
    """Модель отзывов на произведения"""
    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField(verbose_name='review text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='review author'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='score',
        validators=[MinValueValidator(1, 'Слишком маленькая оценка!'),
                    MaxValueValidator(10, 'Слишком большая оценка!')]
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author'
            )
        ]
        ordering = ['-pub_date']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев к отзывам"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='review'
    )
    text = models.TextField(verbose_name='comment text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='comment author'
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self):
        return self.text

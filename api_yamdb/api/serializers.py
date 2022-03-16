from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User


class SingUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации"""

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        """
        Проверяет невозможность создания пользователя с ником 'me'
        """
        if value == 'me':
            raise serializers.ValidationError('Недопустимое имя пользователя')
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=self.validated_data['username'],
            email=self.validated_data['email'],
        )
        return user


class ConfirmationCodeSerializer(serializers.Serializer):
    """Сериализатор для получения кода подтверждения"""
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена при регистрации"""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )


class MeSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей"""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role',
        )
        read_only_fields = ('role',)


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания отзывов"""
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,)
    score = serializers.IntegerField(max_value=10, min_value=1)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only = ('id',)

    def validate(self, data):
        request = self.context.get('request')
        title = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(author=request.user, title=title).exists():
            raise serializers.ValidationError('Your review on this title is '
                                              'already exists')
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с отзывами"""
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,)
    score = serializers.IntegerField(max_value=10, min_value=1)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only = ('id',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для описания жанров"""

    class Meta:
        exclude = ('id',)
        lookup_field = 'slug'
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для описания категорий"""

    class Meta:
        exclude = ('id',)
        lookup_field = 'slug'
        model = Category


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для описания произведений(только чтение)"""
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для описания произведений(на запись)"""
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        read_only = ('id',)

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title, User

from api_yamdb.settings import DEFAULT_FROM_EMAIL

from .filters import FilterForTitle
from .mixins import ModelSetCLD
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsStaffOrAuthorOrReadOnly, MePermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          ConfirmationCodeSerializer, GenreSerializer,
                          GetTokenSerializer, MeSerializer,
                          ReviewCreateSerializer, ReviewSerializer,
                          SingUpSerializer, TitleReadSerializer,
                          TitleWriteSerializer, UserSerializer)


def sent_confirmation_code(request):
    """Функция отправки кода подтверждения при регистрации"""
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    email = serializer.validated_data.get('email')
    user = get_object_or_404(User, username=username)
    confirmation_code = default_token_generator.make_token(user)
    return send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {confirmation_code}',
        [DEFAULT_FROM_EMAIL],
        [email],
        fail_silently=False,
    )


class SignUp(APIView):
    """Функция регистрации новых пользователей"""
    queryset = User.objects.all()
    serializer_class = SingUpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        sent_confirmation_code(request)
        return Response(request.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_token(request):
    """Функция получения токена при регистрации"""
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.validated_data.get('confirmation_code')
    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
    return Response({'confirmation_code': 'Неверный код подтверждения!'},
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Отображение действий с пользователями"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('username',)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        detail=False, methods=['get', 'patch'],
        permission_classes=[MePermission]
    )
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = MeSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = MeSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    """Отображение действий с отзывами"""
    serializer_class = ReviewSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        title = get_object_or_404(
            Title, id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title, id=self.kwargs.get('title_id')
        )
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """Отображение действий с комментариями"""
    serializer_class = CommentSerializer
    permission_classes = (IsStaffOrAuthorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title_id=self.kwargs.get('title_id'),
        )
        serializer.save(review=review, author=self.request.user)


class GenreViewSet(ModelSetCLD):
    """Отображение действий с жанрами для произведений"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    pagination_class = PageNumberPagination
    search_fields = ['=name']
    lookup_field = 'slug'


class CategoryViewSet(ModelSetCLD):
    """Отображение действий с категориями для произведений"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    pagination_class = PageNumberPagination
    search_fields = ['=name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """Отображение действий с произведениями"""
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterForTitle

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer

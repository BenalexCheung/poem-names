"""
视图模块
定义API端点和视图逻辑
"""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from django.contrib.auth import get_user_model
from .models import Surname, Poetry, Word, Name, UserFavorite

User = get_user_model()
from .serializers import (
    UserSerializer, UserRegistrationSerializer, SurnameSerializer,
    PoetrySerializer, WordSerializer, NameSerializer, NameGenerationSerializer,
    UserFavoriteSerializer, NameSearchSerializer
)
from .generator import generate_multiple_names


class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """用户登录"""
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': '请提供用户名和密码'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        return Response(
            {'error': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class SurnameViewSet(viewsets.ReadOnlyModelViewSet):
    """姓氏视图集"""
    queryset = Surname.objects.all()
    serializer_class = SurnameSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """获取热门姓氏"""
        surnames = self.get_queryset().order_by('-frequency')[:20]
        serializer = self.get_serializer(surnames, many=True)
        return Response(serializer.data)


class PoetryViewSet(viewsets.ReadOnlyModelViewSet):
    """诗词视图集"""
    queryset = Poetry.objects.all()
    serializer_class = PoetrySerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """按类型获取诗词"""
        poetry_type = request.query_params.get('type')
        if poetry_type in ['shijing', 'chuci']:
            poems = self.get_queryset().filter(poetry_type=poetry_type)
            serializer = self.get_serializer(poems, many=True)
            return Response(serializer.data)
        return Response(
            {'error': '无效的诗词类型'},
            status=status.HTTP_400_BAD_REQUEST
        )


class WordViewSet(viewsets.ReadOnlyModelViewSet):
    """字词视图集"""
    queryset = Word.objects.all()
    serializer_class = WordSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def by_gender(self, request):
        """按性别获取字词"""
        gender = request.query_params.get('gender')
        if gender in ['male', 'female', 'neutral']:
            words = self.get_queryset().filter(gender_preference=gender)
            serializer = self.get_serializer(words, many=True)
            return Response(serializer.data)
        return Response(
            {'error': '无效的性别参数'},
            status=status.HTTP_400_BAD_REQUEST
        )


class NameViewSet(viewsets.ModelViewSet):
    """名字视图集"""
    serializer_class = NameSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Name.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """生成名字"""
        serializer = NameGenerationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # 获取姓氏对象
            surname = None
            if data.get('surname'):
                surname = Surname.objects.get(name=data['surname'])

            # 生成名字
            generated_names = generate_multiple_names(
                surname=surname,
                gender=data['gender'],
                count=data['count'],
                length=data['length'],
                preferences={
                    'tone_preference': data.get('tone_preference', 'unknown'),
                    'meaning_tags': data.get('meaning_tags', [])
                }
            )

            # 转换为Name对象并保存
            saved_names = []
            for name_data in generated_names:
                # 创建Name对象时，需要正确处理surname字段
                name_dict = name_data.copy()
                # surname已经是Surname对象，不需要额外处理
                name_obj = Name.objects.create(
                    created_by=request.user,
                    surname=name_dict['surname'],
                    given_name=name_dict['given_name'],
                    gender=name_dict['gender'],
                    meaning=name_dict['meaning'],
                    origin=name_dict['origin']
                )
                # 设置tags（JSONField）
                name_obj.tags = name_dict.get('tags', [])
                name_obj.save()
                saved_names.append(name_obj)

            result_serializer = NameSerializer(
                saved_names,
                many=True,
                context={'request': request}
            )
            return Response(result_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def search(self, request):
        """搜索名字"""
        serializer = NameSearchSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            queryset = Name.objects.filter(created_by=request.user)

            # 关键词搜索
            if data.get('keyword'):
                queryset = queryset.filter(
                    Q(given_name__icontains=data['keyword']) |
                    Q(meaning__icontains=data['keyword']) |
                    Q(origin__icontains=data['keyword'])
                )

            # 性别过滤
            if data.get('gender'):
                queryset = queryset.filter(gender=data['gender'])

            # 姓氏过滤
            if data.get('surname'):
                queryset = queryset.filter(surname__name__icontains=data['surname'])

            # 标签过滤
            if data.get('tags'):
                for tag in data['tags']:
                    queryset = queryset.filter(tags__contains=[tag])

            # 限制数量
            queryset = queryset[:data.get('limit', 20)]

            result_serializer = NameSerializer(
                queryset,
                many=True,
                context={'request': request}
            )
            return Response(result_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """收藏/取消收藏名字"""
        name = self.get_object()
        favorite, created = UserFavorite.objects.get_or_create(
            user=request.user,
            name=name
        )

        if not created:
            # 已经收藏，取消收藏
            favorite.delete()
            return Response({'message': '已取消收藏'})

        serializer = UserFavoriteSerializer(favorite, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """获取收藏的名字"""
        favorites = UserFavorite.objects.filter(user=request.user)
        names = [fav.name for fav in favorites]
        serializer = NameSerializer(names, many=True, context={'request': request})
        return Response(serializer.data)


class UserFavoriteViewSet(viewsets.ModelViewSet):
    """用户收藏视图集"""
    serializer_class = UserFavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# 兼容旧API的视图
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_name_view(request):
    """兼容旧的API接口"""
    if request.method == 'POST':
        # 调用新的名字生成逻辑
        generated_names = generate_multiple_names(count=1)

        if generated_names:
            name_data = generated_names[0]
            return Response({
                'status': 200,
                'message': 'OK',
                'data': {
                    'name': name_data['given_name'],
                    'meaning': name_data['meaning'],
                    'origin': name_data['origin']
                }
            })

        return Response({
            'status': 500,
            'message': '生成失败',
            'data': {'name': '诗韵'}
        })

    return Response({
        'status': 400,
        'message': '无效的请求方法'
    })

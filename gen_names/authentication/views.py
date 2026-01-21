"""
认证相关的视图
"""
from rest_framework import status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import secrets

from .serializers import (
    CustomTokenObtainPairSerializer, UserProfileSerializer,
    ChangePasswordSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    自定义JWT Token获取视图
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    用户资料视图
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """
    修改密码视图
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 更新密码
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'message': '密码修改成功'})


class PasswordResetView(generics.GenericAPIView):
    """
    密码重置请求视图
    """
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)

        # 生成重置token（简化版，生产环境应该使用更安全的方式）
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token  # 需要在User模型中添加reset_token字段
        user.save()

        # 发送重置邮件（这里是模拟，实际需要配置邮件服务）
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token}"

        try:
            send_mail(
                '密码重置',
                f'请点击以下链接重置密码：{reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({'message': '重置邮件已发送'})
        except Exception as e:
            return Response(
                {'error': '邮件发送失败'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    密码重置确认视图
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(reset_token=token)
            user.set_password(new_password)
            user.reset_token = None  # 清除token
            user.save()

            return Response({'message': '密码重置成功'})
        except User.DoesNotExist:
            return Response(
                {'error': '无效的重置链接'},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    用户登出视图
    JWT是无状态的，这里主要用于客户端清理token
    """
    return Response({'message': '登出成功'})
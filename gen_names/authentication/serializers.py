"""
认证相关的序列化器
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    自定义JWT Token获取序列化器
    支持用户名或邮箱登录
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        # 添加用户信息到响应中
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'phone': self.user.phone,
        }

        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'avatar', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("新密码不匹配")

        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError("旧密码错误")

        return data


class PasswordResetSerializer(serializers.Serializer):
    """密码重置序列化器"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("该邮箱未注册")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """密码重置确认序列化器"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("新密码不匹配")
        return data
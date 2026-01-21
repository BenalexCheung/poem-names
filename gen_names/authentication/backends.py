"""
自定义认证后端
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(BaseBackend):
    """
    自定义认证后端：支持用户名或邮箱登录
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            # 尝试通过用户名或邮箱查找用户
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )

            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        except User.DoesNotExist:
            return None

        return None

    def user_can_authenticate(self, user):
        """
        复写用户认证检查
        """
        return getattr(user, 'is_active', True)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
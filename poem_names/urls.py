"""poem_names URL Configuration"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from gen_names import views
from gen_names.authentication import views as auth_views

# 创建路由器
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'surnames', views.SurnameViewSet, basename='surname')
router.register(r'poetry', views.PoetryViewSet, basename='poetry')
router.register(r'words', views.WordViewSet, basename='word')
router.register(r'names', views.NameViewSet, basename='name')
router.register(r'favorites', views.UserFavoriteViewSet, basename='favorite')

urlpatterns = [
    path('admin/', admin.site.urls),

    # API路由
    path('api/', include(router.urls)),

    # JWT认证路由
    path('api/auth/token/', auth_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 用户认证相关路由
    path('api/auth/profile/', auth_views.UserProfileView.as_view(), name='user_profile'),
    path('api/auth/change-password/', auth_views.ChangePasswordView.as_view(), name='change_password'),
    path('api/auth/password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('api/auth/password-reset-confirm/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/auth/logout/', auth_views.logout_view, name='logout'),

    # 兼容旧API的路由
    path('api/generate-name', views.generate_name_view, name='generate_name_legacy'),

    # API文档
    path('api/docs/', include('rest_framework.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
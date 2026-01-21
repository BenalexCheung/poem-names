from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Surname, Poetry, Word, Name, UserFavorite


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """自定义用户管理"""
    list_display = ('username', 'email', 'phone', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_active', 'is_staff', 'date_joined')


@admin.register(Surname)
class SurnameAdmin(admin.ModelAdmin):
    """姓氏管理"""
    list_display = ('name', 'pinyin', 'meaning', 'frequency')
    search_fields = ('name', 'pinyin', 'meaning')
    list_filter = ('frequency',)
    ordering = ('-frequency', 'name')


@admin.register(Poetry)
class PoetryAdmin(admin.ModelAdmin):
    """诗词管理"""
    list_display = ('title', 'poetry_type', 'author', 'section')
    search_fields = ('title', 'content', 'author')
    list_filter = ('poetry_type', 'section')
    ordering = ('poetry_type', 'title')


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    """字词管理"""
    list_display = ('character', 'pinyin', 'gender_preference', 'frequency', 'meaning')
    search_fields = ('character', 'pinyin', 'meaning')
    list_filter = ('gender_preference', 'tone', 'frequency')
    ordering = ('-frequency', 'character')


@admin.register(Name)
class NameAdmin(admin.ModelAdmin):
    """名字管理"""
    list_display = ('full_name', 'gender', 'meaning', 'created_by', 'created_at')
    search_fields = ('given_name', 'full_name', 'meaning', 'origin')
    list_filter = ('gender', 'created_at', 'is_favorite')
    ordering = ('-created_at',)
    readonly_fields = ('full_name',)


@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    """用户收藏管理"""
    list_display = ('user', 'name', 'created_at')
    search_fields = ('user__username', 'name__full_name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

"""
缓存管理器 - 优化数据访问性能
"""
import functools
import time
from django.core.cache import cache
from django.conf import settings


class CacheManager:
    """缓存管理器"""

    # 缓存键前缀
    CACHE_PREFIX = 'poem_names:'

    # 缓存时间（秒）
    CACHE_TIMEOUT = {
        'word_data': 3600,  # 字词数据缓存1小时
        'user_prefs': 1800,  # 用户偏好缓存30分钟
        'popular_names': 900,  # 热门名字缓存15分钟
        'surnames': 7200,  # 姓氏数据缓存2小时
        'poetry': 3600,  # 诗词数据缓存1小时
    }

    @classmethod
    def get_cache_key(cls, key_type, *args):
        """生成缓存键"""
        return f"{cls.CACHE_PREFIX}{key_type}:{':'.join(str(arg) for arg in args)}"

    @classmethod
    def get_cached_data(cls, key_type, *args, default=None):
        """获取缓存数据"""
        key = cls.get_cache_key(key_type, *args)
        return cache.get(key, default)

    @classmethod
    def set_cached_data(cls, key_type, data, *args):
        """设置缓存数据"""
        key = cls.get_cache_key(key_type, *args)
        timeout = cls.CACHE_TIMEOUT.get(key_type, 300)  # 默认5分钟
        cache.set(key, data, timeout)

    @classmethod
    def delete_cache(cls, key_type, *args):
        """删除缓存"""
        key = cls.get_cache_key(key_type, *args)
        cache.delete(key)

    @classmethod
    def clear_cache_pattern(cls, pattern):
        """清除匹配模式的缓存"""
        # Django默认cache backend不支持模式删除，这里使用简单实现
        # 在生产环境中建议使用Redis等支持模式删除的缓存后端
        pass


def cached_method(timeout_key):
    """
    方法缓存装饰器

    Args:
        timeout_key: 缓存时间键
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # 生成缓存键
            key_parts = [func.__name__, str(self.__class__.__name__)]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))

            cache_key = CacheManager.get_cache_key('method', *key_parts)

            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result

            # 执行方法
            result = func(self, *args, **kwargs)

            # 缓存结果
            timeout = CacheManager.CACHE_TIMEOUT.get(timeout_key, 300)
            cache.set(cache_key, result, timeout)

            return result

        return wrapper
    return decorator


class OptimizedQueryManager:
    """优化查询管理器"""

    @staticmethod
    def get_popular_names(limit=10, days=7):
        """获取热门名字（带缓存）"""
        cache_key = f"popular_names_{days}_{limit}"

        cached_result = CacheManager.get_cached_data('popular_names', cache_key)
        if cached_result:
            return cached_result

        from .models import Name, UserFavorite
        from django.db.models import Count
        from datetime import datetime, timedelta

        since_date = datetime.now() - timedelta(days=days)

        popular_names = Name.objects.filter(
            favorited_by__created_at__gte=since_date
        ).annotate(
            favorite_count=Count('favorited_by')
        ).order_by('-favorite_count')[:limit]

        result = list(popular_names)
        CacheManager.set_cached_data('popular_names', result, cache_key)

        return result

    @staticmethod
    def get_user_favorites(user, use_cache=True):
        """获取用户收藏（优化查询）"""
        if use_cache:
            cache_key = f"user_favorites_{user.id}"
            cached_result = CacheManager.get_cached_data('user_prefs', cache_key)
            if cached_result:
                return cached_result

        from .models import UserFavorite

        # 使用select_related优化查询
        favorites = UserFavorite.objects.filter(
            user=user
        ).select_related('name').order_by('-created_at')

        result = list(favorites)
        if use_cache:
            CacheManager.set_cached_data('user_prefs', result, cache_key)

        return result

    @staticmethod
    def get_words_by_attributes(wuxing=None, gender_preference=None, min_frequency=1):
        """根据属性获取字词（优化查询）"""
        from .models import Word
        from django.db.models import Q

        # 构建查询条件
        query = Q(frequency__gte=min_frequency)

        if wuxing and wuxing != 'unknown':
            query &= Q(wuxing=wuxing)

        if gender_preference and gender_preference != 'neutral':
            query &= Q(gender_preference=gender_preference)

        # 使用索引优化查询
        return Word.objects.filter(query).order_by('-frequency')

    @staticmethod
    def bulk_create_names(name_data_list):
        """批量创建名字（优化性能）"""
        from .models import Name

        # 分批处理以避免内存溢出
        batch_size = 100
        created_names = []

        for i in range(0, len(name_data_list), batch_size):
            batch = name_data_list[i:i + batch_size]
            names = Name.objects.bulk_create([
                Name(**data) for data in batch
            ])
            created_names.extend(names)

        return created_names

    @staticmethod
    def invalidate_user_cache(user):
        """清除用户相关缓存"""
        # 清除用户收藏缓存
        CacheManager.delete_cache('user_prefs', f"user_favorites_{user.id}")

        # 清除用户偏好缓存
        CacheManager.delete_cache('user_prefs', f"user_prefs_{user.id}")

    @staticmethod
    def get_name_with_related(name_id):
        """获取名字及其相关数据（优化查询）"""
        from .models import Name

        return Name.objects.select_related(
            'surname', 'created_by'
        ).prefetch_related(
            'favorited_by'
        ).get(id=name_id)


# 全局缓存管理器实例
cache_manager = CacheManager()
query_manager = OptimizedQueryManager()
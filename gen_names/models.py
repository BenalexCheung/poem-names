from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    """自定义用户模型"""
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="手机号")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="头像")
    reset_token = models.CharField(max_length=100, blank=True, null=True, verbose_name="密码重置令牌")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class Surname(models.Model):
    """姓氏表"""
    name = models.CharField(max_length=10, unique=True, verbose_name="姓氏")
    pinyin = models.CharField(max_length=50, blank=True, null=True, verbose_name="拼音")
    origin = models.TextField(blank=True, null=True, verbose_name="来源")
    meaning = models.TextField(blank=True, null=True, verbose_name="含义")
    frequency = models.IntegerField(default=0, verbose_name="使用频率")

    class Meta:
        verbose_name = "姓氏"
        verbose_name_plural = verbose_name
        ordering = ['-frequency', 'name']

    def __str__(self):
        return self.name


class Poetry(models.Model):
    """诗词表 - 存储《诗经》和《楚辞》内容"""
    POETRY_TYPES = [
        ('shijing', '诗经'),
        ('chuci', '楚辞'),
    ]

    title = models.CharField(max_length=100, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    author = models.CharField(max_length=50, blank=True, null=True, verbose_name="作者")
    poetry_type = models.CharField(max_length=20, choices=POETRY_TYPES, verbose_name="类型")
    section = models.CharField(max_length=50, blank=True, null=True, verbose_name="章节")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "诗词"
        verbose_name_plural = verbose_name
        ordering = ['poetry_type', 'title']

    def __str__(self):
        return f"{self.get_poetry_type_display()} - {self.title}"


class Word(models.Model):
    """字词表 - 存储诗词中的字词及其属性"""
    GENDERS = [
        ('male', '男性'),
        ('female', '女性'),
        ('neutral', '中性'),
    ]

    TONES = [
        ('ping', '平声'),
        ('ze', '仄声'),
        ('unknown', '未知'),
    ]

    WUXING = [
        ('jin', '金'),
        ('mu', '木'),
        ('shui', '水'),
        ('huo', '火'),
        ('tu', '土'),
        ('unknown', '未知'),
    ]

    character = models.CharField(max_length=5, unique=True, verbose_name="汉字")
    pinyin = models.CharField(max_length=20, verbose_name="拼音")
    wuxing = models.CharField(max_length=10, choices=WUXING, default='unknown', verbose_name="五行属性")
    meaning = models.TextField(verbose_name="含义")
    gender_preference = models.CharField(max_length=10, choices=GENDERS, default='neutral', verbose_name="性别倾向")
    tone = models.CharField(max_length=10, choices=TONES, default='unknown', verbose_name="声调")
    frequency = models.IntegerField(default=0, verbose_name="出现频率")
    from_poetry = models.ManyToManyField(Poetry, related_name='words', verbose_name="来源诗词")
    tags = models.JSONField(default=list, verbose_name="标签")  # 如：美好、勇敢、聪明等

    class Meta:
        verbose_name = "字词"
        indexes = [
            models.Index(fields=['frequency']),  # 频率索引
            models.Index(fields=['wuxing']),  # 五行索引
            models.Index(fields=['gender_preference']),  # 性别倾向索引
        ]
        verbose_name_plural = verbose_name
        ordering = ['-frequency', 'character']

    def __str__(self):
        return f"{self.character} ({self.pinyin})"


class Name(models.Model):
    """名字表 - 存储生成的名字"""
    GENDERS = [
        ('M', '男'),
        ('F', '女'),
    ]

    surname = models.ForeignKey(Surname, on_delete=models.CASCADE, related_name='names', verbose_name="姓氏")
    given_name = models.CharField(max_length=20, verbose_name="名字")
    full_name = models.CharField(max_length=50, verbose_name="全名")
    gender = models.CharField(max_length=1, choices=GENDERS, verbose_name="性别")
    pinyin = models.CharField(max_length=100, blank=True, null=True, verbose_name="拼音")
    meaning = models.TextField(verbose_name="含义")
    origin = models.TextField(verbose_name="词源")
    reference_poetry = models.ManyToManyField(Poetry, related_name='generated_names', verbose_name="参考诗词")
    tags = models.JSONField(default=list, verbose_name="标签")
    wuxing_analysis = models.JSONField(default=dict, verbose_name="五行分析")
    phonology_analysis = models.JSONField(default=dict, verbose_name="音韵分析")
    bagua_suggestions = models.JSONField(default=dict, verbose_name="八卦建议")
    name_score = models.JSONField(default=dict, verbose_name="名字评分")
    is_favorite = models.BooleanField(default=False, verbose_name="是否收藏")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_names', verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_by', '-created_at']),  # 用户生成记录索引
            models.Index(fields=['gender']),  # 性别索引
            models.Index(fields=['-created_at']),  # 创建时间索引
        ]

    class Meta:
        verbose_name = "名字"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        unique_together = ['full_name', 'created_by']  # 同一个用户不能生成重复的名字

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        # 自动生成全名
        self.full_name = f"{self.surname.name}{self.given_name}"
        super().save(*args, **kwargs)


class UserFavorite(models.Model):
    """用户收藏表"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites', verbose_name="用户")
    name = models.ForeignKey(Name, on_delete=models.CASCADE, related_name='favorites', verbose_name="收藏的名字")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "用户收藏"
        verbose_name_plural = verbose_name
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', '-created_at']),  # 用户收藏时间索引
            models.Index(fields=['-created_at']),  # 全局时间索引
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 收藏 {self.name.full_name}"

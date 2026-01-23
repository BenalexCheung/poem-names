"""
序列化器模块
定义API数据序列化和反序列化
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Surname, Poetry, Word, Name, UserFavorite


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'phone', 'avatar', 'password',
                 'is_active', 'date_joined')
        read_only_fields = ('id', 'is_active', 'date_joined')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'phone', 'password', 'password_confirm')

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("密码不匹配")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return super().create(validated_data)


class SurnameSerializer(serializers.ModelSerializer):
    """姓氏序列化器"""

    class Meta:
        model = Surname
        fields = '__all__'


class PoetrySerializer(serializers.ModelSerializer):
    """诗词序列化器"""

    class Meta:
        model = Poetry
        fields = '__all__'


class WordSerializer(serializers.ModelSerializer):
    """字词序列化器"""

    class Meta:
        model = Word
        fields = '__all__'


class NameSerializer(serializers.ModelSerializer):
    """名字序列化器"""
    surname = SurnameSerializer(read_only=True)
    surname_id = serializers.IntegerField(write_only=True, required=False)
    created_by = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Name
        fields = ('id', 'surname', 'surname_id', 'given_name', 'full_name', 'gender',
                 'pinyin', 'meaning', 'origin', 'reference_poetry', 'tags',
                 'wuxing_analysis', 'phonology_analysis', 'bagua_suggestions', 'name_score',
                 'shengxiao', 'shichen', 'birth_month', 'is_lunar_month', 'traditional_analysis',
                 'is_favorite', 'is_favorited', 'created_by', 'created_at', 'updated_at')
        read_only_fields = ('id', 'full_name', 'pinyin', 'created_by', 'created_at', 'updated_at')

    def get_is_favorited(self, obj):
        """检查当前用户是否收藏了这个名字"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFavorite.objects.filter(
                user=request.user,
                name=obj
            ).exists()
        return False

    def create(self, validated_data):
        # 设置创建者
        validated_data['created_by'] = self.context['request'].user

        # 处理姓氏
        surname_id = validated_data.pop('surname_id', None)
        if surname_id:
            try:
                surname = Surname.objects.get(id=surname_id)
                validated_data['surname'] = surname
            except Surname.DoesNotExist:
                raise serializers.ValidationError("姓氏不存在")

        return super().create(validated_data)


class NameGenerationSerializer(serializers.Serializer):
    """名字生成请求序列化器"""
    surname = serializers.CharField(max_length=10, required=False)
    gender = serializers.ChoiceField(choices=[('M', '男'), ('F', '女')], default='M')
    count = serializers.IntegerField(min_value=1, max_value=20, default=5)
    length = serializers.IntegerField(min_value=1, max_value=3, default=2)
    tone_preference = serializers.ChoiceField(
        choices=[('ping', '平声'), ('ze', '仄声'), ('unknown', '任意')],
        default='unknown',
        required=False
    )
    meaning_tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    # 传统元素参数
    shengxiao = serializers.CharField(max_length=20, required=False, help_text="生肖，如：rat, ox, tiger等")
    shichen = serializers.CharField(max_length=20, required=False, help_text="时辰，如：zi, chou, yin等")
    birth_month = serializers.IntegerField(min_value=1, max_value=12, required=False, help_text="出生月份（1-12）")
    is_lunar_month = serializers.BooleanField(default=True, required=False, help_text="是否为农历月份")
    use_ai = serializers.BooleanField(default=True, required=False)

    def validate_surname(self, value):
        """验证姓氏是否存在"""
        if value:
            try:
                Surname.objects.get(name=value)
            except Surname.DoesNotExist:
                raise serializers.ValidationError("姓氏不存在")
        return value


class UserFavoriteSerializer(serializers.ModelSerializer):
    """用户收藏序列化器"""
    name = NameSerializer(read_only=True)
    name_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserFavorite
        fields = ('id', 'name', 'name_id', 'created_at')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NameSearchSerializer(serializers.Serializer):
    """名字搜索序列化器"""
    keyword = serializers.CharField(required=False, allow_blank=True)
    gender = serializers.ChoiceField(
        choices=[('M', '男'), ('F', '女')],
        required=False
    )
    surname = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    limit = serializers.IntegerField(min_value=1, max_value=100, default=20)
"""
API测试
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from ..models import Surname, Poetry, Name

User = get_user_model()


class AuthenticationTestCase(APITestCase):
    """认证测试"""

    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_registration(self):
        """测试用户注册"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post('/api/users/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', response.data)

    def test_user_login(self):
        """测试用户登录"""
        response = self.client.post('/api/auth/token/', self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class NameGenerationTestCase(APITestCase):
    """名字生成测试"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

        # 创建测试姓氏
        self.surname = Surname.objects.create(
            name='王',
            pinyin='wang',
            meaning='统治者',
            origin='古代帝王姓氏'
        )

    def test_generate_names(self):
        """测试名字生成"""
        data = {
            'surname': '王',
            'gender': 'M',
            'count': 3,
            'length': 2
        }
        response = self.client.post('/api/names/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertLessEqual(len(response.data), 3)


class DataAPITestCase(APITestCase):
    """数据API测试"""

    def test_get_surnames(self):
        """测试获取姓氏列表"""
        response = self.client.get('/api/surnames/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_poetry(self):
        """测试获取诗词列表"""
        response = self.client.get('/api/poetry/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ModelTestCase(TestCase):
    """模型测试"""

    def test_surname_creation(self):
        """测试姓氏创建"""
        surname = Surname.objects.create(
            name='李',
            pinyin='li',
            meaning='李子树',
            origin='源于植物'
        )
        self.assertEqual(surname.name, '李')
        self.assertEqual(str(surname), '李')

    def test_poetry_creation(self):
        """测试诗词创建"""
        poetry = Poetry.objects.create(
            title='关雎',
            content='关关雎鸠，在河之洲。',
            poetry_type='shijing',
            section='国风·周南'
        )
        self.assertEqual(poetry.title, '关雎')
        self.assertEqual(str(poetry), '诗经 - 关雎')
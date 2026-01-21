# Poem Names API 文档

## 概述

Poem Names 是一个基于《诗经》和《楚辞》的智能名字生成器API。本API提供了完整的用户认证、名字生成、收藏管理等功能。

## 基础信息

- **Base URL**: `http://localhost:8000/api/`
- **认证方式**: JWT (JSON Web Token)
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

### 用户注册

```http
POST /api/users/
```

**请求体**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "phone": "13800138000"
}
```

**响应**:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "phone": "13800138000",
  "is_active": true,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

### 用户登录

```http
POST /api/auth/token/
```

**请求体**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**响应**:
```json
{
  "refresh": "eyJ0eXAi...",
  "access": "eyJ0eXAi...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com"
  }
}
```

### 刷新Token

```http
POST /api/auth/token/refresh/
```

**请求体**:
```json
{
  "refresh": "eyJ0eXAi..."
}
```

**响应**:
```json
{
  "access": "eyJ0eXAi..."
}
```

## 名字生成

### 生成名字

```http
POST /api/names/generate/
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "surname": "王",
  "gender": "M",
  "count": 5,
  "length": 2,
  "tone_preference": "ping",
  "meaning_tags": ["勇敢", "智慧"]
}
```

**参数说明**:
- `surname`: 姓氏（可选）
- `gender`: 性别 ("M" 男, "F" 女)
- `count`: 生成数量 (1-20)
- `length`: 名字长度 (1-3字)
- `tone_preference`: 声调偏好 ("ping", "ze", "unknown")
- `meaning_tags`: 含义标签数组

**响应**:
```json
[
  {
    "id": 1,
    "surname": {
      "id": 1,
      "name": "王",
      "pinyin": "wang"
    },
    "given_name": "诗韵",
    "full_name": "王诗韵",
    "gender": "M",
    "meaning": "诗意美好",
    "origin": "源自古典诗词",
    "tags": ["美好", "诗意"],
    "is_favorite": false,
    "created_by": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### 搜索名字

```http
POST /api/names/search/
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "keyword": "诗",
  "gender": "F",
  "surname": "李",
  "tags": ["美好"],
  "limit": 10
}
```

**响应**: 同生成名字响应格式

## 收藏管理

### 获取收藏列表

```http
GET /api/names/favorites/
Authorization: Bearer {access_token}
```

### 收藏/取消收藏名字

```http
POST /api/names/{id}/favorite/
Authorization: Bearer {access_token}
```

## 数据浏览

### 获取姓氏列表

```http
GET /api/surnames/
```

**查询参数**:
- `search`: 搜索关键词

### 获取热门姓氏

```http
GET /api/surnames/popular/
```

### 获取诗词列表

```http
GET /api/poetry/
```

**查询参数**:
- `type`: 诗词类型 ("shijing", "chuci")
- `search`: 搜索关键词

### 获取字词列表

```http
GET /api/words/
```

**查询参数**:
- `gender`: 性别倾向 ("male", "female", "neutral")
- `search`: 搜索关键词

## 用户管理

### 获取用户资料

```http
GET /api/auth/profile/
Authorization: Bearer {access_token}
```

### 更新用户资料

```http
PATCH /api/auth/profile/
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "email": "newemail@example.com",
  "phone": "13900139000"
}
```

### 修改密码

```http
POST /api/auth/change-password/
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "old_password": "oldpassword",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

### 密码重置请求

```http
POST /api/auth/password-reset/
```

**请求体**:
```json
{
  "email": "user@example.com"
}
```

### 密码重置确认

```http
POST /api/auth/password-reset-confirm/
```

**请求体**:
```json
{
  "token": "reset_token_from_email",
  "new_password": "newpassword123",
  "new_password_confirm": "newpassword123"
}
```

## 错误响应

所有API在出错时都会返回适当的HTTP状态码和错误信息：

```json
{
  "detail": "错误描述",
  "code": "error_code"
}
```

常见HTTP状态码：
- `400`: 请求参数错误
- `401`: 未认证或认证失败
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## SDK 和示例

### Python 示例

```python
import requests

# 登录获取token
login_data = {
    'username': 'testuser',
    'password': 'password123'
}
response = requests.post('http://localhost:8000/api/auth/token/', json=login_data)
tokens = response.json()

# 使用token生成名字
headers = {
    'Authorization': f'Bearer {tokens["access"]}'
}
generate_data = {
    'gender': 'M',
    'count': 3
}
response = requests.post(
    'http://localhost:8000/api/names/generate/',
    json=generate_data,
    headers=headers
)
names = response.json()
```

### JavaScript 示例

```javascript
// 登录
const loginData = {
  username: 'testuser',
  password: 'password123'
};

fetch('/api/auth/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(loginData)
})
.then(response => response.json())
.then(data => {
  const token = data.access;

  // 生成名字
  const generateData = {
    gender: 'F',
    count: 5
  };

  return fetch('/api/names/generate/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(generateData)
  });
})
.then(response => response.json())
.then(names => {
  console.log('生成的诗意名字:', names);
});
```

## 兼容性说明

为了向后兼容，API保留了以下旧接口：

```http
POST /api/generate-name
```

该接口不需要认证，仅用于测试目的。
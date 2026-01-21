# 诗楚名 - Poem Names

基于古典文学的AI智能名字生成器，融合五行八卦、音韵学和机器学习技术，从73篇经典作品中生成具有文化内涵的名字。

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- PostgreSQL (生产环境) 或 SQLite (开发环境)

### 后端设置

1. **克隆项目**
```bash
git clone <repository-url>
cd poem-names
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **数据库迁移**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **导入数据**
```bash
# 导入诗词和姓氏数据
python manage.py import_data --poetry
python manage.py import_data --surnames
python manage.py import_data --words
```

6. **创建超级用户**
```bash
python manage.py createsuperuser
```

7. **运行后端服务器**
```bash
python manage.py runserver
```

### 前端设置

1. **安装前端依赖**
```bash
cd frontend
npm install
```

2. **启动前端开发服务器**
```bash
npm start
```

### 使用Docker (可选)

```bash
# 构建并运行
docker-compose up --build

# 后台运行
docker-compose up -d
```

## 📋 功能特性

### 核心功能
- ✅ 基于古典文学的智能名字生成（诗经、楚辞、论语、孟子、唐诗等73篇经典作品）
- ✅ 五行八卦分析系统（金木水火土五行平衡、八卦方位建议）
- ✅ 古汉语音韵学系统（完整的声韵调分析、平仄和谐度计算）
- ✅ AI智能推荐引擎（基于用户行为的个性化推荐算法）
- ✅ 智能音韵匹配和平仄协调
- ✅ 性别倾向分析和推荐
- ✅ 含义标签系统
- ✅ 用户收藏系统
- ✅ 高性能缓存和数据库优化

### 用户系统
- ✅ JWT Token认证
- ✅ 用户注册和登录
- ✅ 个人资料管理
- ✅ 密码重置功能

### API接口
- ✅ RESTful API设计
- ✅ 完整的CRUD操作
- ✅ 请求分页和过滤
- ✅ 错误处理和验证

## 🌟 智能功能

### 五行八卦分析
- **五行属性**：基于汉字的五行属性（金木水火土）进行平衡度分析
- **八卦方位**：根据五行缺失提供八卦方位的吉祥建议
- **平衡评分**：计算名字的五行平衡度并提供优化建议

### 古汉语音韵系统
- **声调分析**：完整的古汉语声调系统（平声、上声、去声、入声）
- **韵律和谐**：基于平仄相间的传统韵律美学进行评分
- **音韵协调**：检测头韵、韵律等和谐现象

### AI智能推荐
- **个性化推荐**：基于用户收藏历史的学习推荐算法
- **协同过滤**：分析其他用户的偏好模式
- **智能排序**：结合五行、音韵等多维度综合评分

## 🔧 API文档

### 认证接口

#### 用户注册
```http
POST /api/users/
```

#### 用户登录
```http
POST /api/auth/token/
```

#### 刷新Token
```http
POST /api/auth/token/refresh/
```

### 名字生成接口

#### 生成名字
```http
POST /api/names/generate/
Authorization: Bearer {token}
```

请求示例：
```json
{
  "surname": "王",
  "gender": "M",
  "count": 5,
  "length": 2,
  "tone_preference": "ping",
  "meaning_tags": ["勇敢", "智慧"],
  "use_ai": true
}
```

响应示例：
```json
[
  {
    "id": 1,
    "full_name": "王彦博",
    "gender": "M",
    "pinyin": "wáng yàn bó",
    "meaning": "诗词用字",
    "tags": ["古典", "诗意"],
    "wuxing_analysis": {
      "wuxing_percentages": {"jin": 0.0, "mu": 50.0, "shui": 0.0, "huo": 50.0, "tu": 0.0},
      "balance_score": 75.0,
      "balance_level": {"level": "良好", "color": "blue"}
    },
    "phonology_analysis": {
      "rhythm_score": 85.0,
      "rhythm_level": {"level": "优秀", "color": "green"}
    },
    "bagua_suggestions": {
      "suggestions": [
        {"bagua": "离", "direction": "南", "meaning": "火、中女、光明"}
      ]
    },
    "name_score": {
      "total_score": 78.5,
      "wuxing_score": 75.0,
      "phonology_score": 82.0,
      "level": {"grade": "B", "description": "良好"}
    }
  }
]
```

#### 搜索名字
```http
POST /api/names/search/
Authorization: Bearer {token}
```

### 数据接口

#### 获取姓氏列表
```http
GET /api/surnames/
```

#### 获取诗词列表
```http
GET /api/poetry/?type=shijing
```

#### 获取字词列表
```http
GET /api/words/?gender=male
```

## 🗂️ 项目结构

```
poem-names/
├── gen_names/              # Django主应用
│   ├── authentication/     # 认证模块
│   ├── data_processor.py   # 数据处理
│   ├── generator.py        # 名字生成器
│   ├── models.py          # 数据模型
│   ├── serializers.py     # API序列化器
│   ├── views.py           # API视图
│   └── management/        # 管理命令
├── frontend/              # React前端
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── pages/         # 页面
│   │   ├── store/         # Redux状态管理
│   │   └── App.js         # 主应用组件
│   └── package.json
├── data/                  # 数据文件
│   ├── poetry/            # 诗词数据
│   └── surnames.txt       # 姓氏数据
├── requirements.txt       # Python依赖
├── manage.py             # Django管理脚本
├── docker-compose.yml    # Docker配置
└── API.md                # 详细API文档
```

## 🧪 测试

### 运行单元测试
```bash
python manage.py test
```

### API测试
```bash
# 使用curl测试API
curl -X POST http://localhost:8000/api/generate-name \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 🚀 部署

### 生产环境部署

1. **设置环境变量**
```bash
export DJANGO_SETTINGS_MODULE=poem_names.settings.production
export SECRET_KEY=your-secret-key
export DATABASE_URL=postgresql://user:pass@host:port/db
```

2. **收集静态文件**
```bash
python manage.py collectstatic
```

3. **使用Gunicorn运行**
```bash
gunicorn poem_names.wsgi:application --bind 0.0.0.0:8000
```

### Docker部署
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📝 许可证

本项目采用GPL-3.0许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

**享受融合传统文化与AI技术的智能名字生成体验！** 🎭🤖
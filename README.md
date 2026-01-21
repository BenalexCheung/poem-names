# 诗楚名 - Poem Names

基于《诗经》和《楚辞》的智能名字生成器，通过输入一些关键词或条件，程序能够根据古典诗词自动生成符合条件的名字。

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
- ✅ 基于《诗经》和《楚辞》的名字生成
- ✅ 智能音韵匹配和平仄协调
- ✅ 性别倾向分析和推荐
- ✅ 含义标签系统
- ✅ 用户收藏系统

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
  "meaning_tags": ["勇敢", "智慧"]
}
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

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 邮箱: your-email@example.com

---

**享受古典诗词带来的名字灵感！** 🎭📖

## 需求分析

1. 该项目能够根据用户输入的参数，生成符合用户要求的姓名。参数包括：
   - 姓氏
   - 性别，男性或女性，决定了从《诗经》或《楚辞》中选取名字的范围。
   - 希望名称的音韵，例如清音、浊音、轻声、阳平、上声等，用户可以根据个人喜好选择。
   - 希望名称的含义，例如喜庆、吉祥、聪明、勇敢等，用户可以根据自己的需要选择。
   - 其他特殊需求，例如名字的简繁体字形式，用户可以根据自己的需要选择。
2. 该项目需要支持前后端分离，前端采用React，后端采用Django Rest Framework。
3. 接口需要授权才能使用，采用OAuth2.0或JWT Token进行授权认证。
4. 该项目需要提供名称的相关信息，包括：
   - 名称的字形
   - 名称的语义
   - 名称的词源
   - 名称的寓意
5. 该项目需要使用《诗经》和《楚辞》的内容作为基础，生成符合要求的名称。
6. 该项目需要保证生成的名称不会重复，可以考虑使用区块链技术或其他简单的方案。
7. 该项目需要提供用户管理模块，包括用户注册、登录、修改密码等功能。
8. 该项目需要提供管理员管理模块，包括添加、修改、删除名称、管理用户等功能。
9. 该项目需要部署在本地服务器上，数据库采用PostgreSQL。

## 技术选型

- 编程语言：Python

- 前端框架：Django Rest Framework

- 后端框架：React

- 数据库：PostgreSQL


## 开发计划

- 根据需求设计数据库结构，并创建对应的数据表；
- 需要实现生成随机名字的算法，这个算法需要根据用户输入的参数，从《诗经》和《楚辞》中获取相应的音、韵、含义等信息，然后进行组合生成名字，并且需要保证生成的名字符合一定的规则和美学标准；
- 需要设计和实现用户认证和授权的功能，可以选择OAuth2.0或JWT Token；
- 需要编写前端和后端代码，并且进行集成测试和部署。

在这个过程中，我们需要不断迭代和优化，根据实际情况进行调整和改进。

### 数据库设计

#### [数据清洗入库](DATACLEAN.md)

首先，需要将《诗经》和《楚辞》的内容进行清洗和整理，提取出每一首诗歌和文言文段落，将其存储在数据库中。具体的清洗和整理方式需要参考具体的数据格式和需要提取的信息，这里不做过多讨论。

#### 表结构设计

(1) 名字表

用于存储生成的名字，包括名字的拼音、字形、含义、词源、寓意等信息。表结构设计如下：

| 字段名     | 类型     | 描述                         |
| ---------- | -------- | ---------------------------- |
| id         | Integer  | 名字id，主键                 |
| name       | Char     | 名字                         |
| pinyin     | Char     | 名字的拼音                   |
| gender     | Char     | 名字的性别（男/女）          |
| meaning    | Text     | 名字的含义                   |
| origin     | Text     | 名字的词源                   |
| reference  | Text     | 名字参考的《诗经》或《楚辞》 |
| created_at | DateTime | 名字创建时间                 |

(2) 用户表

用于存储用户信息和访问令牌，表结构设计如下：

| 字段名     | 类型     | 描述                   |
| ---------- | -------- | ---------------------- |
| id         | Integer  | 用户id，主键           |
| username   | Char     | 用户名                 |
| password   | Char     | 用户密码（加密后的）   |
| email      | Char     | 用户邮箱               |
| is_active  | Boolean  | 用户是否激活           |
| created_at | DateTime | 用户创建时间           |
| token      | Char     | 用户访问令牌           |
| expired_at | DateTime | 用户访问令牌的过期时间 |

### 名字生成算法

生成名字的算法可以基于以下几个步骤：

1. 根据性别选择诗经或楚辞作为文本数据来源。
2. 对文本数据进行清洗和预处理，例如去除停用词、标点符号等，保留词语和字词。
3. 利用自然语言处理技术，例如NLTK等库，对预处理后的文本进行分词、词性标注等操作，以提取有意义的词语。
4. 通过对文本数据的分析，选取合适的词语作为候选名字，并结合相关的音、韵、含义等因素进行筛选和排序。
5. 根据用户指定的名字长度和字数，随机从候选名字中选取一定数量的名字作为推荐结果。
6. 对于用户选择的名字，提供字形、语义、词源、寓意等相关信息。

这里提供一个简单的示例代码，用于根据输入的性别和指定的名字长度生成对应的名字：

```python
pythonCopy code
import random

def generate_name(gender, length):
    # 读取相应的诗经或楚辞文件
    if gender == 'male':
        with open('shijing.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    elif gender == 'female':
        with open('chuci.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        return 'Invalid gender'

    # 根据文件内容生成所有可能的名字
    names = []
    for i in range(len(content) - length):
        name = content[i:i+length]
        if name not in names:
            names.append(name)

    # 随机选取一个名字并返回
    return random.choice(names)
```

这是一个简单的实现，具体实现方式可以根据需求进行调整。

### [接口设计](API.md)和接口认证

针对这个需求，一个比较简单的方案是使用 OAuth 2.0 授权框架来进行用户认证和授权，并结合 JWT（JSON Web Token）来实现无状态认证。具体流程如下：

1. 用户使用用户名和密码进行登录，后端服务器校验用户身份并生成一个 JWT 令牌，将令牌发送给客户端；
2. 客户端将 JWT 令牌保存在本地，每次访问需要授权的接口时，将令牌作为 Authorization 头部发送给后端服务器；
3. 后端服务器验证 JWT 令牌的合法性，如果合法，则允许用户访问接口，否则返回 401 错误。

## CI & CD

1. 首先，需要创建一个 `docker-compose.yml` 文件，用于定义 Docker Compose 的服务和相关配置。示例文件如下：

```
yamlCopy code
version: '3'
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    environment:
      - REACT_APP_API_URL=http://backend:8000
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - POSTGRES_USER=username
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
      - DATABASE_HOST=db
    depends_on:
      - db
    links:
      - db
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_USER=username
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=dbname
volumes:
  postgres_data:
```

1. 在本地电脑上创建 `frontend` 和 `backend` 目录，并在各自目录下创建 `Dockerfile` 文件，用于构建镜像。示例文件如下：

`frontend/Dockerfile` 文件：

```
sqlCopy code
FROM node:16-alpine

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install

COPY . .

EXPOSE 3000

CMD ["yarn", "start"]
```

`backend/Dockerfile` 文件：

```
sqlCopy code
FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk --purge del .build-deps

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

1. 在 `frontend` 目录下运行 `npm run build` 命令，生成静态文件。
2. 在项目根目录下运行 `docker-compose up` 命令，启动容器。
3. 访问 `http://localhost:3000` 即可查看前端应用，访问 `http://localhost:8000` 可以查看后端应用。

### 运行和测试

一个简单的Makefile，可以用于编译，运行，测试和部署您的应用程序：

```
makefileCopy code
# Makefile for Poem Names project

# Variables
DOCKER_COMPOSE_FILE=docker-compose.yaml
DOCKER_COMPOSE_DEV_FILE=docker-compose.dev.yaml

# Commands
.PHONY: build
build:
    docker-compose -f $(DOCKER_COMPOSE_FILE) build

.PHONY: run
run:
    docker-compose -f $(DOCKER_COMPOSE_FILE) up

.PHONY: test
test:
    docker-compose -f $(DOCKER_COMPOSE_DEV_FILE) run --rm backend python manage.py test

.PHONY: deploy
deploy:
    docker-compose -f $(DOCKER_COMPOSE_FILE) up -d
```

您可以使用`make build`命令来构建Docker镜像，使用`make run`命令来运行Docker容器，使用`make test`命令来运行单元测试，使用`make deploy`命令来部署Docker容器
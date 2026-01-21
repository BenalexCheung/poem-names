"""
AI智能推荐系统
基于用户行为、机器学习和大语言模型的智能名字推荐
"""
import math
import random
import json
import requests
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .models import Name, UserFavorite, Word
from .cache_manager import cache_manager, query_manager


class AIRecommender:
    """AI智能推荐器 - 集成大语言模型增强功能"""

    def __init__(self):
        self.user_preferences = {}
        self.name_features = {}
        self.similarity_matrix = None

        # 大语言模型配置（可选）
        self.llm_config = {
            'enabled': True,  # 默认关闭，需要用户主动启用
            'api_url': 'https://api.siliconflow.cn/v1/chat/completions',  # 默认OpenAI
            'api_key': 'sk-gznzglkoliugsnfkafeykswvfsltpgittxvhebszgqqhnbhq',
            'model': 'deepseek-ai/DeepSeek-R1',
            'max_tokens': 500,
            'temperature': 0.7
        }

        self._build_recommendation_model()

    def configure_llm(self, api_key=None, api_url=None, model=None, enabled=True):
        """配置大语言模型参数"""
        if api_key:
            self.llm_config['api_key'] = api_key
        if api_url:
            self.llm_config['api_url'] = api_url
        if model:
            self.llm_config['model'] = model
        self.llm_config['enabled'] = enabled and bool(api_key)

        return self.llm_config['enabled']

    def _build_recommendation_model(self):
        """构建推荐模型"""
        try:
            # 构建名字特征矩阵
            self._build_name_features()
            # 计算相似度矩阵
            self._calculate_similarity_matrix()
            # 分析用户偏好
            self._analyze_user_preferences()
        except Exception as e:
            print(f"构建推荐模型失败: {e}")

    def _build_name_features(self):
        """构建名字特征向量"""
        names = Name.objects.all()[:1000]  # 限制处理数量以提高性能

        for name in names:
            features = []

            # 基本特征
            features.append(name.gender == 'M' and 1 or 0)  # 性别
            features.append(len(name.given_name))  # 名字长度

            # 五行特征
            wuxing_analysis = name.wuxing_analysis or {}
            wuxing_counts = wuxing_analysis.get('wuxing_counts', {})
            for wuxing in ['jin', 'mu', 'shui', 'huo', 'tu']:
                features.append(wuxing_counts.get(wuxing, 0))

            # 音韵特征
            phonology_analysis = name.phonology_analysis or {}
            tone_analysis = phonology_analysis.get('tone_analysis', {})
            tone_counts = tone_analysis.get('tone_counts', {})
            for tone in ['ping', 'shang', 'qu', 'ru']:
                features.append(tone_counts.get(tone, 0))

            # 评分特征
            name_score = name.name_score or {}
            features.append(name_score.get('total_score', 50))

            self.name_features[name.id] = features

    def _calculate_similarity_matrix(self):
        """计算名字相似度矩阵"""
        if not self.name_features:
            return

        # 转换为特征矩阵
        name_ids = list(self.name_features.keys())
        feature_matrix = np.array([self.name_features[nid] for nid in name_ids])

        # 计算余弦相似度
        if len(feature_matrix) > 1:
            self.similarity_matrix = cosine_similarity(feature_matrix)
        else:
            self.similarity_matrix = np.array([[1.0]])

    def _analyze_user_preferences(self):
        """分析用户偏好模式"""
        # 检查缓存
        cache_key = "user_preferences_analysis"
        cached_result = cache_manager.get_cached_data('user_prefs', cache_key)
        if cached_result:
            self.user_preferences = cached_result
            return

        # 分析收藏数据
        favorites = UserFavorite.objects.select_related('user', 'name').all()

        user_stats = defaultdict(lambda: {
            'gender_pref': Counter(),
            'length_pref': Counter(),
            'wuxing_pref': Counter(),
            'score_pref': [],
            'favorite_names': []
        })

        for fav in favorites:
            user_id = fav.user.id
            name = fav.name

            stats = user_stats[user_id]

            # 性别偏好
            stats['gender_pref'][name.gender] += 1

            # 长度偏好
            stats['length_pref'][len(name.given_name)] += 1

            # 五行偏好
            wuxing_counts = (name.wuxing_analysis or {}).get('wuxing_counts', {})
            for wuxing, count in wuxing_counts.items():
                stats['wuxing_pref'][wuxing] += count

            # 评分偏好
            score = (name.name_score or {}).get('total_score', 50)
            stats['score_pref'].append(score)

            stats['favorite_names'].append(name.id)

        # 计算偏好权重
        for user_id, stats in user_stats.items():
            # 性别偏好权重
            total_gender = sum(stats['gender_pref'].values())
            if total_gender > 0:
                stats['gender_weights'] = {
                    gender: count / total_gender
                    for gender, count in stats['gender_pref'].items()
                }

            # 长度偏好权重
            total_length = sum(stats['length_pref'].values())
            if total_length > 0:
                stats['length_weights'] = {
                    length: count / total_length
                    for length, count in stats['length_pref'].items()
                }

            # 五行偏好权重
            total_wuxing = sum(stats['wuxing_pref'].values())
            if total_wuxing > 0:
                stats['wuxing_weights'] = {
                    wuxing: count / total_wuxing
                    for wuxing, count in stats['wuxing_pref'].items()
                }

            # 评分偏好
            if stats['score_pref']:
                stats['avg_score_pref'] = sum(stats['score_pref']) / len(stats['score_pref'])

        self.user_preferences = dict(user_stats)

        # 缓存结果
        cache_manager.set_cached_data('user_prefs', self.user_preferences, cache_key)

    def get_personalized_recommendations(self, user, base_names, limit=10):
        """
        获取个性化推荐

        Args:
            user: 用户对象
            base_names: 基础名字列表（字典格式）
            limit: 返回数量限制

        Returns:
            list: 排序后的推荐名字列表
        """
        if user.id not in self.user_preferences:
            # 新用户，返回基于评分的推荐
            return self._get_score_based_recommendations(base_names, limit)

        user_prefs = self.user_preferences[user.id]

        # 计算每个名字的个性化评分
        scored_names = []
        for name_data in base_names:
            score = self._calculate_personalized_score_from_data(name_data, user_prefs)
            scored_names.append((name_data, score))

        # 按评分排序
        scored_names.sort(key=lambda x: x[1], reverse=True)

        return [name for name, score in scored_names[:limit]]

    def _calculate_personalized_score_from_data(self, name_data, user_prefs):
        """从名字数据字典计算个性化评分"""
        score = 0

        # 基础评分（名字综合评分）
        base_score = (name_data.get('name_score') or {}).get('total_score', 50)
        score += base_score * 0.3

        # 性别匹配度
        gender_weights = user_prefs.get('gender_weights', {})
        gender = name_data.get('gender', 'M')
        gender_match = gender_weights.get(gender, 0.5)  # 默认中性权重
        score += gender_match * 20

        # 长度偏好
        length_weights = user_prefs.get('length_weights', {})
        name_length = len(name_data.get('given_name', ''))
        length_match = length_weights.get(name_length, 0.2)  # 默认权重
        score += length_match * 15

        # 五行偏好匹配
        wuxing_weights = user_prefs.get('wuxing_weights', {})
        wuxing_counts = (name_data.get('wuxing_analysis') or {}).get('wuxing_counts', {})
        wuxing_score = 0

        for wuxing, count in wuxing_counts.items():
            wuxing_weight = wuxing_weights.get(wuxing, 0.2)
            wuxing_score += wuxing_weight * count

        score += wuxing_score * 10

        # 评分偏好匹配
        avg_score_pref = user_prefs.get('avg_score_pref', 70)
        score_diff = abs(base_score - avg_score_pref)
        score_penalty = max(0, score_diff - 10) * 0.5  # 超过10分差的惩罚
        score -= score_penalty

        return round(score, 2)

    def _calculate_personalized_score(self, name, user_prefs):
        """计算个性化评分"""
        score = 0

        # 基础评分（名字综合评分）
        base_score = (name.name_score or {}).get('total_score', 50)
        score += base_score * 0.3

        # 性别匹配度
        gender_weights = user_prefs.get('gender_weights', {})
        gender_match = gender_weights.get(name.gender, 0.5)  # 默认中性权重
        score += gender_match * 20

        # 长度偏好
        length_weights = user_prefs.get('length_weights', {})
        name_length = len(name.given_name)
        length_match = length_weights.get(name_length, 0.2)  # 默认权重
        score += length_match * 15

        # 五行偏好匹配
        wuxing_weights = user_prefs.get('wuxing_weights', {})
        wuxing_counts = (name.wuxing_analysis or {}).get('wuxing_counts', {})
        wuxing_score = 0

        for wuxing, count in wuxing_counts.items():
            wuxing_weight = wuxing_weights.get(wuxing, 0.2)
            wuxing_score += wuxing_weight * count

        score += wuxing_score * 10

        # 评分偏好匹配
        avg_score_pref = user_prefs.get('avg_score_pref', 70)
        score_diff = abs(base_score - avg_score_pref)
        score_penalty = max(0, score_diff - 10) * 0.5  # 超过10分差的惩罚
        score -= score_penalty

        # 相似度奖励（喜欢类似的名字）
        favorite_names = user_prefs.get('favorite_names', [])
        if favorite_names and self.similarity_matrix is not None:
            try:
                name_idx = list(self.name_features.keys()).index(name.id)
                max_similarity = 0

                for fav_id in favorite_names:
                    if fav_id in self.name_features:
                        fav_idx = list(self.name_features.keys()).index(fav_id)
                        similarity = self.similarity_matrix[name_idx][fav_idx]
                        max_similarity = max(max_similarity, similarity)

                score += max_similarity * 25  # 相似度奖励
            except (ValueError, IndexError):
                pass

        return round(score, 2)

    def _get_score_based_recommendations(self, base_names, limit):
        """基于评分的通用推荐"""
        scored_names = []
        for name_data in base_names:
            score = (name_data.get('name_score') or {}).get('total_score', 50)
            scored_names.append((name_data, score))

        scored_names.sort(key=lambda x: x[1], reverse=True)
        return [name for name, score in scored_names[:limit]]

    def get_collaborative_recommendations(self, user, candidate_names, limit=5):
        """
        基于协同过滤的推荐（其他用户喜欢的名字）

        Args:
            user: 用户对象
            candidate_names: 候选名字列表
            limit: 返回数量

        Returns:
            list: 推荐的名字列表
        """
        # 获取其他用户的收藏数据
        other_favorites = UserFavorite.objects.exclude(user=user).values_list('name_id', flat=True)
        favorite_counts = Counter(other_favorites)

        # 计算流行度评分
        recommendations = []
        for name in candidate_names:
            popularity_score = favorite_counts.get(name.id, 0)
            # 添加一些随机性避免总是推荐最流行的
            random_factor = random.uniform(0.8, 1.2)
            final_score = popularity_score * random_factor

            recommendations.append((name, final_score))

        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [name for name, score in recommendations[:limit]]

    def update_user_model(self, user):
        """
        更新用户模型（在用户收藏新名字时调用）

        Args:
            user: 用户对象
        """
        # 清除用户相关缓存
        query_manager.invalidate_user_cache(user)

        # 清除用户偏好分析缓存
        cache_manager.delete_cache('user_prefs', "user_preferences_analysis")

        # 重新分析用户偏好
        self._analyze_user_preferences()

        # 可以在这里添加实时学习逻辑
        # 比如更新用户的偏好向量、重新计算相似度等

    def get_trending_names(self, days=7, limit=10):
        """
        获取热门名字（最近几天最受欢迎的）

        Args:
            days: 天数
            limit: 返回数量

        Returns:
            list: 热门名字列表
        """
        # 使用优化的查询管理器
        return query_manager.get_popular_names(limit, days)

    def get_similar_names(self, base_name, limit=5):
        """
        获取相似名字推荐

        Args:
            base_name: 基准名字
            limit: 返回数量

        Returns:
            list: 相似名字列表
        """
        if not self.similarity_matrix or base_name.id not in self.name_features:
            return []

        try:
            base_idx = list(self.name_features.keys()).index(base_name.id)
            similarities = self.similarity_matrix[base_idx]

            # 获取最相似的名字
            similar_indices = np.argsort(similarities)[::-1][1:limit+1]  # 排除自己

            similar_names = []
            name_ids = list(self.name_features.keys())

            for idx in similar_indices:
                try:
                    name_id = name_ids[idx]
                    name = Name.objects.get(id=name_id)
                    similarity_score = similarities[idx]
                    similar_names.append((name, similarity_score))
                except Name.DoesNotExist:
                    continue

            return [name for name, score in similar_names]

        except (ValueError, IndexError):
            return []

    # ==================== 大语言模型增强功能 ====================

    def _call_llm_api(self, prompt, max_retries=2):
        """调用大语言模型API"""
        if not self.llm_config['enabled'] or not self.llm_config['api_key']:
            return None

        headers = {
            'Authorization': f"Bearer {self.llm_config['api_key']}",
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.llm_config['model'],
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': self.llm_config['max_tokens'],
            'temperature': self.llm_config['temperature']
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.llm_config['api_url'],
                    headers=headers,
                    json=data,
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()

            except Exception as e:
                print(f"LLM API调用失败 (尝试 {attempt + 1}): {e}")
                continue

        return None

    def generate_name_explanation(self, name, user=None):
        """
        使用大语言模型生成名字的诗意解释

        Args:
            name: Name对象
            user: 用户对象（可选，用于个性化）

        Returns:
            str: 生成的解释文本
        """
        if not self.llm_config['enabled']:
            return self._generate_basic_explanation(name)

        # 构建提示词
        prompt = f"""
你是一个专业的中国古典文化专家，请为名字"{name.full_name}"生成一段优美的解释。

基本信息：
- 姓氏：{name.surname.name if hasattr(name, 'surname') else '未知'}
- 名字：{name.given_name}
- 性别：{'男' if name.gender == 'M' else '女'}
- 含义：{name.meaning}
- 出处：{name.origin[:100] if name.origin else '源自古典诗词'}

请从以下几个方面进行解释（总字数控制在200字以内）：
1. 名字的字面含义和文化内涵
2. 相关的古典文学典故或诗词引用
3. 名字的音韵和谐度分析
4. 五行属性的象征意义
5. 适合的名字性格特征

要求：
- 语言优美，富有诗意
- 准确把握古典文化内涵
- 突出名字的独特魅力
- 适合家长选择新生儿名字

请直接给出解释内容，不要添加多余的标题或格式。
"""

        explanation = self._call_llm_api(prompt)

        if explanation:
            return explanation
        else:
            # LLM调用失败，回退到基础解释
            return self._generate_basic_explanation(name)

    def _generate_basic_explanation(self, name):
        """生成基础的名字解释（当LLM不可用时使用）"""
        return f"""名字"{name.full_name}"寓意{name.meaning}。{name.origin[:100] if name.origin else '源自古典诗词'}。这个名字音韵和谐，富有文化内涵，适合培养孩子{name.gender == 'M' and '勇敢坚毅' or '温柔贤惠'}的性格。"""

    def generate_creative_names(self, preferences=None, count=5, user=None):
        """
        使用大语言模型生成创意名字

        Args:
            preferences: 用户偏好字典
            count: 生成数量
            user: 用户对象

        Returns:
            list: 生成的创意名字列表
        """
        if not self.llm_config['enabled']:
            return []

        # 解析偏好
        gender = preferences.get('gender', 'M') if preferences else 'M'
        meaning_tags = preferences.get('meaning_tags', []) if preferences else []
        tone_preference = preferences.get('tone_preference', 'ping') if preferences else 'ping'

        # 构建创意名字生成的提示词
        prompt = f"""
你是一个专业的中国名字专家，请根据以下要求生成{count}个创意中文名字：

要求：
- 性别：{'男' if gender == 'M' else '女'}孩
- 风格：古典诗词风格，富有文化内涵
- 字数：2字名
- 偏好主题：{', '.join(meaning_tags) if meaning_tags else '美好、智慧、勇敢等正面品质'}
- 声调偏好：{tone_preference}声为主

请生成{count}个名字，每个名字包含：
1. 完整名字
2. 简要含义解释
3. 文化出处或典故

格式要求：
名字1: [名字] - [含义] ([出处])
名字2: [名字] - [含义] ([出处])
...

确保名字优美、吉祥，避免生僻字。
"""

        response = self._call_llm_api(prompt)
        print("============")
        print(response)
        if response:
            try:
                # 解析生成的创意名字
                creative_names = []
                lines = response.strip().split('\n')

                for line in lines:
                    if ':' in line and len(line.split(':')) >= 2:
                        name_part = line.split(':', 1)[1].strip()
                        # 尝试提取名字和解释
                        if ' - ' in name_part:
                            name, explanation = name_part.split(' - ', 1)
                            creative_names.append({
                                'name': name.strip(),
                                'explanation': explanation.strip(),
                                'source': 'llm_generated'
                            })

                return creative_names[:count]

            except Exception as e:
                print(f"解析LLM创意名字失败: {e}")
                return []

        return []

    def enhance_name_analysis(self, name, user=None):
        """
        使用大语言模型增强名字分析

        Args:
            name: Name对象
            user: 用户对象

        Returns:
            dict: 增强的分析结果
        """
        if not self.llm_config['enabled']:
            return {}

        # 分析名字的文化内涵和现代适用性
        prompt = f"""
请分析名字"{name.full_name}"的文化内涵和现代适用性：

分析维度：
1. 文化传承价值
2. 现代社会适应性
3. 性格培养导向
4. 职业发展启示
5. 潜在优势和局限

请给出客观、建设性的分析意见。
"""

        enhanced_analysis = self._call_llm_api(prompt)

        if enhanced_analysis:
            return {
                'cultural_value': '从分析中提取文化价值...',
                'modern_adaptability': '从分析中提取现代适用性...',
                'personality_guidance': '从分析中提取性格培养建议...',
                'career_insights': '从分析中提取职业发展启示...',
                'full_analysis': enhanced_analysis
            }

        return {}

    def get_llm_status(self):
        """获取LLM功能状态"""
        return {
            'enabled': self.llm_config['enabled'],
            'configured': bool(self.llm_config['api_key']),
            'model': self.llm_config['model'],
            'status': 'ready' if self.llm_config['enabled'] else 'disabled'
        }


# 全局AI推荐器实例
ai_recommender = AIRecommender()
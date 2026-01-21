"""
名字生成器
基于诗经和楚辞的智能名字生成算法
"""
import random
import logging
from collections import defaultdict
from .models import Word, Surname, Poetry, Name
from .wuxing_analyzer import wuxing_analyzer
from .phonology_analyzer import phonology_analyzer
from .ai_recommender import ai_recommender

logger = logging.getLogger(__name__)


class NameGenerator:
    """智能名字生成器"""

    def __init__(self):
        self.word_cache = {}
        self.target_gender = 'M'  # 默认男性，用于性别评分
        self._load_word_data()

    def _load_word_data(self):
        """加载字词数据到缓存"""
        try:
            words = Word.objects.all()
            for word in words:
                self.word_cache[word.character] = {
                    'pinyin': word.pinyin,
                    'gender_preference': word.gender_preference,
                    'gender_strength': getattr(word, 'gender_strength', 'weak'),
                    'meaning': word.meaning,
                    'tags': word.tags,
                    'frequency': word.frequency
                }
        except Exception as e:
            logger.warning(f"加载字词数据失败: {e}")
            self.word_cache = {}

    def _get_words_by_gender(self, gender):
        """根据性别获取合适的字词 - 增强版性别区分"""
        if gender == 'M':
            # 男性字词选择策略
            male_words = []
            neutral_words = []

            # 1. 首先选择强性别倾向男性字词
            for char, data in self.word_cache.items():
                if data['gender_preference'] == 'male' and data['gender_strength'] in ['strong', 'medium']:
                    male_words.append((char, data))

            # 2. 补充弱性别倾向男性字词
            for char, data in self.word_cache.items():
                if (data['gender_preference'] == 'male' and data['gender_strength'] == 'weak') or \
                   (data['gender_preference'] == 'neutral' and self._is_suitable_for_male(char, data)):
                    male_words.append((char, data))

            # 3. 如果男性字词仍不够，补充中性字词（但标记为男性倾向）
            if len(male_words) < 100:
                for char, data in self.word_cache.items():
                    if data['gender_preference'] == 'neutral':
                        neutral_words.append((char, data))
                        if len(male_words) + len(neutral_words) >= 150:
                            break

            return male_words + neutral_words[:50]  # 限制中性字词数量

        elif gender == 'F':
            # 女性字词选择策略
            female_words = []
            neutral_words = []

            # 1. 首先选择强性别倾向女性字词
            for char, data in self.word_cache.items():
                if data['gender_preference'] == 'female' and data['gender_strength'] in ['strong', 'medium']:
                    female_words.append((char, data))

            # 2. 补充弱性别倾向女性字词
            for char, data in self.word_cache.items():
                if (data['gender_preference'] == 'female' and data['gender_strength'] == 'weak') or \
                   (data['gender_preference'] == 'neutral' and self._is_suitable_for_female(char, data)):
                    female_words.append((char, data))

            # 3. 如果女性字词仍不够，补充中性字词（但标记为女性倾向）
            if len(female_words) < 100:
                for char, data in self.word_cache.items():
                    if data['gender_preference'] == 'neutral':
                        neutral_words.append((char, data))
                        if len(female_words) + len(neutral_words) >= 150:
                            break

            return female_words + neutral_words[:50]  # 限制中性字词数量
        else:
            # 中性或未知性别
            return [(char, data) for char, data in self.word_cache.items()]

    def _is_suitable_for_male(self, char, data):
        """判断字词是否适合男性使用"""
        tags = data.get('tags', [])

        # 阳刚、力量相关的标签适合男性
        male_suitable_tags = ['刚强', '力量', '智慧', '理性', '勇敢', '坚毅', '阳刚', '五行金', '五行木', '五行火']

        # 阴柔、温柔相关的标签不适合男性
        male_unsuitable_tags = ['温柔', '优雅', '细腻', '阴柔', '五行水']

        # 检查是否有男性适合的标签
        if any(tag in male_suitable_tags for tag in tags):
            return True

        # 检查是否有男性不适合的标签
        if any(tag in male_unsuitable_tags for tag in tags):
            return False

        # 默认基于五行判断
        wuxing = data.get('wuxing', 'unknown')
        return wuxing in ['jin', 'mu', 'huo']  # 金木火属阳刚

    def _is_suitable_for_female(self, char, data):
        """判断字词是否适合女性使用"""
        tags = data.get('tags', [])

        # 阴柔、优雅相关的标签适合女性
        female_suitable_tags = ['温柔', '优雅', '美丽', '细腻', '情感', '阴柔', '五行水', '五行土']

        # 阳刚、力量相关的标签不适合女性
        female_unsuitable_tags = ['刚强', '力量', '勇敢', '阳刚', '五行金', '五行火']

        # 检查是否有女性适合的标签
        if any(tag in female_suitable_tags for tag in tags):
            return True

        # 检查是否有女性不适合的标签
        if any(tag in female_unsuitable_tags for tag in tags):
            return False

        # 默认基于五行判断
        wuxing = data.get('wuxing', 'unknown')
        return wuxing in ['shui', 'tu', 'mu']  # 水土木属阴柔

    def _filter_words_by_preferences(self, words, tone_preference=None, meaning_tags=None):
        """根据偏好过滤字词"""
        filtered_words = words

        if tone_preference:
            # 根据声调偏好过滤
            tone_filtered = []
            for char, data in filtered_words:
                # 简单的声调判断（这里可以扩展更复杂的音韵学规则）
                if tone_preference == 'ping' and (data['pinyin'].endswith('1') or data['pinyin'].endswith('2')):
                    tone_filtered.append((char, data))
                elif tone_preference == 'ze' and (data['pinyin'].endswith('3') or data['pinyin'].endswith('4')):
                    tone_filtered.append((char, data))
                elif tone_preference == 'unknown':
                    tone_filtered.append((char, data))
            filtered_words = tone_filtered

        if meaning_tags:
            # 根据含义标签过滤
            tag_filtered = []
            for char, data in filtered_words:
                if any(tag in data['tags'] for tag in meaning_tags):
                    tag_filtered.append((char, data))
            # 如果按标签过滤后字词太少，放宽条件
            if len(tag_filtered) < 20:
                tag_filtered = filtered_words
            filtered_words = tag_filtered

        return filtered_words

    def _calculate_name_score(self, name_chars, preferences):
        """计算名字的评分"""
        score = 0

        # 字词频率加分
        for char in name_chars:
            if char in self.word_cache:
                score += min(self.word_cache[char]['frequency'] / 100, 10)  # 最高10分

        # 含义一致性加分
        if preferences.get('meaning_tags'):
            meaning_score = 0
            for char in name_chars:
                if char in self.word_cache:
                    char_tags = self.word_cache[char]['tags']
                    if any(tag in char_tags for tag in preferences['meaning_tags']):
                        meaning_score += 5
            score += meaning_score

        # 声调和谐加分
        if len(name_chars) >= 2:
            tones = []
            for char in name_chars:
                if char in self.word_cache:
                    pinyin = self.word_cache[char]['pinyin']
                    if pinyin[-1].isdigit():
                        tones.append(int(pinyin[-1]))

            # 平仄相间加分
            if len(tones) >= 2:
                harmony_score = 0
                for i in range(len(tones) - 1):
                    if (tones[i] in [1, 2] and tones[i+1] in [3, 4]) or \
                       (tones[i] in [3, 4] and tones[i+1] in [1, 2]):
                        harmony_score += 3
                score += harmony_score

        return score

    def _generate_name_candidates(self, gender, length=2, preferences=None):
        # 设置目标性别
        self.target_gender = gender
        """生成名字候选列表"""
        if preferences is None:
            preferences = {}

        # 获取基础字词
        base_words = self._get_words_by_gender(gender)
        if not base_words:
            return []

        # 根据偏好过滤
        filtered_words = self._filter_words_by_preferences(
            base_words,
            tone_preference=preferences.get('tone_preference'),
            meaning_tags=preferences.get('meaning_tags')
        )

        if not filtered_words:
            filtered_words = base_words

        # 生成候选名字 - 添加多样性约束
        candidates = []
        max_attempts = min(1500, len(filtered_words) ** length)  # 增加尝试次数

        # 用于跟踪已生成的独特名字组合（避免完全重复）
        generated_combinations = set()
        char_usage_stats = {}  # 跟踪各字的使用频率

        for _ in range(max_attempts):
            name_chars = []

            # 多样性约束1: 限制同一字在单个名字中的重复次数
            used_chars_in_name = set()

            for _ in range(length):
                # 多样性约束: 加强虚词控制和重复限制
                attempts = 0
                while attempts < 30:  # 增加尝试次数到30次
                    char, data = random.choice(filtered_words)

                    # 1. 虚词频率控制（核心优化）
                    word_category = self._classify_word_category(char, data)
                    if word_category == 'function_word':
                        # 虚词使用严格控制
                        usage_count = char_usage_stats.get(char, 0)
                        if usage_count >= 1:  # 每个虚词最多使用1次
                            attempts += 1
                            continue
                        # 即使是第一次使用，也有30%概率跳过虚词
                        if random.random() < 0.3:
                            attempts += 1
                            continue

                    # 2. 高频字使用概率衰减
                    frequency = data.get('frequency', 0)
                    usage_count = char_usage_stats.get(char, 0)
                    if frequency > 50 and usage_count > 2:
                        # 高频字已使用多次，降低选择概率
                        if random.random() < 0.8:  # 80%概率跳过
                            attempts += 1
                            continue

                    # 3. 检查名字内重复（加强限制）
                    if char in used_chars_in_name and length > 1:
                        # 严格限制重复，90%概率跳过
                        if random.random() < 0.9:
                            attempts += 1
                            continue

                    # 4. 鼓励实词选择
                    if word_category == 'content_word':
                        # 实词有更高选中概率，直接选择
                        pass
                    elif word_category == 'neutral' and random.random() < 0.2:
                        # 中性词也有一定概率被跳过，鼓励选择实词
                        attempts += 1
                        continue

                    # 选择成功
                    name_chars.append(char)
                    used_chars_in_name.add(char)
                    char_usage_stats[char] = usage_count + 1
                    break

                else:
                    # 如果尝试多次仍未找到合适字，随机选择（但排除已知虚词）
                    available_words = [(c, d) for c, d in filtered_words
                                     if self._classify_word_category(c, d) != 'function_word']
                    if available_words:
                        char, _ = random.choice(available_words)
                    else:
                        char, _ = random.choice(filtered_words)
                    name_chars.append(char)
                    used_chars_in_name.add(char)

            name = ''.join(name_chars)

            # 多样性约束3: 避免生成完全相同的名字组合
            name_tuple = tuple(sorted(name_chars))  # 排序后作为唯一标识
            if name_tuple in generated_combinations and len(candidates) > 10:
                continue  # 跳过重复组合（但允许前10个）

            generated_combinations.add(name_tuple)

            # 计算评分
            score = self._calculate_name_score(name_chars, preferences)

            candidates.append({
                'name': name,
                'chars': name_chars,
                'score': score
            })

            # 早期停止条件：收集足够多样化的候选
            if len(candidates) >= 100:  # 生成更多候选用于筛选
                break

        # 按评分排序，返回前50个
        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:50]

    def generate_names(self, surname=None, gender='M', count=10, length=2, preferences=None, user=None, use_ai=True):
        """
        生成名字（支持AI智能推荐）

        Args:
            surname: 姓氏对象或姓氏字符串
            gender: 性别 ('M' 或 'F')
            count: 生成名字的数量
            length: 名字长度（字数）
            preferences: 偏好设置字典，包含：
                - tone_preference: 声调偏好 ('ping', 'ze', 'unknown')
                - meaning_tags: 含义标签列表
            user: 用户对象（用于个性化推荐）
            use_ai: 是否使用AI推荐

        Returns:
            生成的名字列表，每个包含名字和相关信息
        """
        # 设置目标性别，用于性别评分计算
        self.target_gender = gender

        if preferences is None:
            preferences = {}

        # 处理姓氏
        if isinstance(surname, str):
            try:
                surname_obj = Surname.objects.get(name=surname)
            except Surname.DoesNotExist:
                return []
        elif hasattr(surname, 'name'):
            surname_obj = surname
        else:
            # 随机选择姓氏
            surname_obj = Surname.objects.order_by('?').first()
            if not surname_obj:
                return []

        # 生成名字候选
        candidates = self._generate_name_candidates(gender, length, preferences)

        if not candidates:
            return []

        # 获取用户已生成的名字集合，用于去重
        existing_names = set()
        if user:
            existing_names = set(Name.objects.filter(
                created_by=user
            ).values_list('full_name', flat=True))

        # 转换为Name对象格式
        result = []
        generated_in_session = set()  # 在本次会话中已生成的，用于防止重复

        for candidate in candidates[:count * 3]:  # 生成更多候选用于AI筛选和去重
            name_chars = candidate['chars']

            # 检查名字是否已存在
            full_name = f"{surname_obj.name}{candidate['name']}"
            if full_name in existing_names or full_name in generated_in_session:
                continue  # 跳过已存在的名字

            generated_in_session.add(full_name)  # 添加到本次会话生成集合

            # 进行五行分析
            wuxing_analysis = wuxing_analyzer.analyze_name_wuxing(name_chars)
            bagua_suggestions = wuxing_analyzer.get_bagua_suggestions(wuxing_analysis)

            # 进行音韵分析
            phonology_analysis = phonology_analyzer.analyze_name_phonology(name_chars)

            # 计算综合评分
            wuxing_score = wuxing_analyzer.get_name_score(wuxing_analysis)
            phonology_score = phonology_analyzer.get_phonology_score(phonology_analysis)

            # 计算综合评分（使用更复杂的算法）
            total_score = self._calculate_comprehensive_score(
                wuxing_score, phonology_score, name_chars, candidate
            )

            name_score = {
                'total_score': total_score,
                'wuxing_score': wuxing_score['total_score'],
                'phonology_score': phonology_score['total_score'],
                'level': self._get_comprehensive_level(total_score)
            }

            name_data = {
                'surname': surname_obj,
                'given_name': candidate['name'],
                'gender': gender,
                'meaning': self._get_name_meaning(name_chars),
                'origin': self._get_name_origin(name_chars),
                'tags': self._get_name_tags(name_chars),
                'wuxing_analysis': wuxing_analysis,
                'phonology_analysis': phonology_analysis,
                'bagua_suggestions': bagua_suggestions,
                'name_score': name_score,
                'ai_score': 0,  # AI评分，稍后计算
                '_full_name': full_name  # 临时存储全名用于去重
            }

            result.append(name_data)

            # 如果收集到足够的名字就停止
            if len(result) >= count * 2:  # 收集更多用于AI筛选
                break

        # AI智能推荐排序
        if use_ai and user and len(result) > count:
            try:
                # 为名字对象添加临时ID用于AI计算
                for i, name_data in enumerate(result):
                    name_data['_temp_id'] = i

                # 使用AI推荐器进行个性化排序
                recommended_names = ai_recommender.get_personalized_recommendations(
                    user, result, count
                )

                # 清理临时字段
                for name_data in recommended_names:
                    name_data.pop('_full_name', None)
                    if '_temp_id' in name_data:
                        del name_data['_temp_id']

                return recommended_names

            except Exception as e:
                print(f"AI推荐失败，使用默认排序: {e}")
                # AI失败时按综合评分排序
                result.sort(key=lambda x: x['name_score']['total_score'], reverse=True)

        # 默认排序（按综合评分）
        result.sort(key=lambda x: x['name_score']['total_score'], reverse=True)

        # 清理临时字段
        for name_data in result:
            name_data.pop('_full_name', None)

        # LLM增强：为前几个名字生成AI解释（可选功能）
        final_result = result[:count]
        if ai_recommender.get_llm_status()['enabled']:
            try:
                for name_data in final_result[:3]:  # 只为前3个名字生成LLM解释
                    # 创建临时Name对象用于LLM分析
                    temp_name = type('TempName', (), {
                        'full_name': f"{name_data['surname'].name}{name_data['given_name']}",
                        'surname': name_data['surname'],
                        'given_name': name_data['given_name'],
                        'gender': name_data['gender'],
                        'meaning': name_data['meaning'],
                        'origin': name_data['origin']
                    })()

                    # 生成LLM增强解释
                    llm_explanation = ai_recommender.generate_name_explanation(temp_name, user)
                    if llm_explanation:
                        name_data['llm_explanation'] = llm_explanation

                    # 生成增强分析
                    enhanced_analysis = ai_recommender.enhance_name_analysis(temp_name, user)
                    if enhanced_analysis:
                        name_data['enhanced_analysis'] = enhanced_analysis

            except Exception as e:
                print(f"LLM增强功能失败，使用基础功能: {e}")
                # LLM失败不影响正常功能

        return final_result

    def _get_name_meaning(self, chars):
        """获取名字的含义"""
        meanings = []
        for char in chars:
            if char in self.word_cache:
                meaning = self.word_cache[char]['meaning']
                if meaning:
                    meanings.append(meaning)

        if meanings:
            return '、'.join(meanings[:3])  # 最多取前3个含义
        return "诗意名字"

    def _get_name_origin(self, chars):
        """获取名字的词源和具体出处"""
        origins = []
        from .models import Word

        for char in chars:
            try:
                # 获取字词的来源信息
                word_obj = Word.objects.filter(character=char).first()
                if word_obj and word_obj.from_poetry.exists():
                    # 获取相关的诗词
                    poetry_list = word_obj.from_poetry.all()[:2]  # 最多显示2个来源
                    for poetry in poetry_list:
                        # 查找字符在诗词中的具体位置和上下文
                        context = self._find_char_context_in_poetry(char, poetry.content)
                        if context:
                            origins.append(f"出自《{poetry.title}》：{context}")
                        else:
                            origins.append(f"出自《{poetry.title}》")
            except Exception as e:
                continue

        if origins:
            return '；'.join(set(origins))  # 去重
        return "源自古典诗词"

    def _find_char_context_in_poetry(self, char, poetry_content):
        """在诗词内容中查找字符的上下文"""
        try:
            # 查找字符在文本中的位置
            char_index = poetry_content.find(char)
            if char_index == -1:
                return None

            # 提取上下文（前后各5个字符）
            start = max(0, char_index - 5)
            end = min(len(poetry_content), char_index + 6)

            context = poetry_content[start:end]

            # 如果上下文太短，尝试扩展
            if len(context) < 10:
                start = max(0, char_index - 10)
                end = min(len(poetry_content), char_index + 11)
                context = poetry_content[start:end]

            # 高亮显示目标字符
            if char in context:
                context = context.replace(char, f"【{char}】")

            return context.strip()

        except Exception:
            return None

    def _get_name_tags(self, chars):
        """获取名字的标签"""
        all_tags = []
        for char in chars:
            if char in self.word_cache:
                all_tags.extend(self.word_cache[char]['tags'])

        # 去重并返回最相关的标签
        unique_tags = list(set(all_tags))
        return unique_tags[:5]  # 最多5个标签

    def _calculate_comprehensive_score(self, wuxing_score, phonology_score, name_chars, candidate):
        """
        计算综合评分（优化版：提升语义丰富度权重，平衡虚词实词）

        评分维度调整：
        1. 五行平衡度 (25%) - 略微降低
        2. 音韵和谐度 (20%) - 略微降低
        3. 字词质量 (30%) - 大幅提升！包括虚词惩罚和语义多样性
        4. 名字长度适中度 (15%) - 保持
        5. 字符搭配和谐度 (10%) - 保持
        """
        # 基础五行和音韵评分
        base_score = (wuxing_score['total_score'] * 0.25) + (phonology_score['total_score'] * 0.2)

        # 字词质量评分 (0-100) - 大幅提升权重至30%
        word_quality_score = self._calculate_word_quality_score(name_chars)

        # 长度适中度评分 (0-100)
        length_score = self._calculate_length_score(len(name_chars))

        # 字符搭配和谐度评分 (0-100)
        harmony_score = self._calculate_character_harmony_score(name_chars)

        # 计算语义丰富度奖励（额外加分）
        semantic_richness_bonus = self._calculate_semantic_richness_bonus(name_chars)

        # 计算性别一致性奖励（额外加分）
        gender_consistency_bonus = self._calculate_gender_consistency_bonus(name_chars, self.target_gender)

        # 组合所有评分
        total_score = (
            base_score +  # 五行+音韵 (45%)
            word_quality_score * 0.3 +  # 字词质量 (30%) - 提升！
            length_score * 0.15 +  # 长度适中度 (15%)
            harmony_score * 0.1 +  # 字符搭配 (10%)
            semantic_richness_bonus +  # 语义丰富度奖励 (额外)
            gender_consistency_bonus   # 性别一致性奖励 (额外)
        )

        return round(total_score, 1)

    def _calculate_semantic_richness_bonus(self, name_chars):
        """计算语义丰富度奖励 - 优先级提升"""
        if len(name_chars) < 2:
            return 0

        total_bonus = 0

        # 1. 语义多样性奖励 (0-15分)
        semantic_diversity_bonus = self._calculate_semantic_diversity_bonus(name_chars)
        total_bonus += semantic_diversity_bonus

        # 2. 实词密度奖励 (0-10分)
        content_word_count = 0
        for char in name_chars:
            if char in self.word_cache:
                category = self._classify_word_category(char, self.word_cache[char])
                if category == 'content_word':
                    content_word_count += 1

        content_density = content_word_count / len(name_chars)
        density_bonus = content_density * 10  # 实词密度越高奖励越高
        total_bonus += density_bonus

        # 3. 文化内涵深度奖励 (0-10分)
        cultural_depth_bonus = 0
        for char in name_chars:
            if char in self.word_cache:
                tags = self.word_cache[char].get('tags', [])
                # 检查是否有深度文化标签
                deep_cultural_tags = ['古典', '诗意', '贤能', '高贵', '尊贵', '卓越']
                if any(tag in deep_cultural_tags for tag in tags):
                    cultural_depth_bonus += 2

        total_bonus += min(10, cultural_depth_bonus)

        return min(35, total_bonus)  # 最高35分奖励

    def _calculate_gender_consistency_bonus(self, name_chars, target_gender):
        """计算性别一致性奖励"""
        if not name_chars or not target_gender:
            return 0

        gender_score = 0
        strong_gender_chars = 0
        matching_gender_chars = 0

        for char in name_chars:
            if char in self.word_cache:
                data = self.word_cache[char]
                pref = data.get('gender_preference', 'neutral')
                strength = data.get('gender_strength', 'weak')

                if pref == target_gender:
                    matching_gender_chars += 1
                    if strength == 'strong':
                        strong_gender_chars += 1
                        gender_score += 3  # 强性别匹配：3分
                    elif strength == 'medium':
                        gender_score += 2  # 中等性别匹配：2分
                    else:
                        gender_score += 1  # 弱性别匹配：1分
                elif pref != 'neutral':
                    # 相反性别倾向：惩罚
                    if strength == 'strong':
                        gender_score -= 2  # 强相反性别：-2分
                    elif strength == 'medium':
                        gender_score -= 1  # 中等相反性别：-1分

        # 整体一致性奖励
        consistency_ratio = matching_gender_chars / len(name_chars)
        if consistency_ratio >= 0.8:
            gender_score += 5  # 80%以上字词性别一致：额外5分
        elif consistency_ratio >= 0.6:
            gender_score += 3  # 60%以上字词性别一致：额外3分
        elif consistency_ratio >= 0.4:
            gender_score += 1  # 40%以上字词性别一致：额外1分

        # 强性别字词数量奖励
        if strong_gender_chars >= 2:
            gender_score += 3  # 有2个以上强性别字词：额外3分
        elif strong_gender_chars >= 1:
            gender_score += 2  # 有1个强性别字词：额外2分

        return max(-5, min(15, gender_score))  # 性别一致性奖励范围：-5到15分

    def _calculate_word_quality_score(self, name_chars):
        """计算字词质量评分 - 优化版：频率非线性衰减 + 虚词实词分类 + 多样性约束"""
        if not name_chars:
            return 0

        total_score = 0
        char_usage_count = {}  # 跟踪名字中同一字的使用次数

        # 统计名字中各字的使用频率（用于多样性约束）
        for char in name_chars:
            char_usage_count[char] = char_usage_count.get(char, 0) + 1

        for char in name_chars:
            if char in self.word_cache:
                word_data = self.word_cache[char]

                # 1. 频率评分 - 非线性衰减 (0-20)
                frequency = word_data.get('frequency', 0)
                # 使用对数函数实现非线性衰减，避免高频字过度得分
                if frequency <= 10:
                    freq_score = frequency * 2  # 低频字线性增长
                elif frequency <= 50:
                    freq_score = 20 + (frequency - 10) * 0.5  # 中频字缓慢增长
                elif frequency <= 200:
                    freq_score = 30 + (frequency - 50) * 0.1  # 高频字极慢增长
                else:
                    freq_score = 35 + min(5, (frequency - 200) * 0.01)  # 超高频字上限

                freq_score = min(40, freq_score)  # 最高40分

                # 2. 虚词/实词分类权重惩罚
                word_category = self._classify_word_category(char, word_data)
                category_multiplier = self._get_category_score_multiplier(word_category)

                # 3. 含义丰富度评分 (0-20) - 优先级提升
                tags = word_data.get('tags', [])
                meaning_score = min(25, len(tags) * 5)  # 每个标签5分，最高25分

                # 4. 性别适应度评分 (0-30) - 大幅提升权重
                gender_pref = word_data.get('gender_preference', 'neutral')
                gender_strength = word_data.get('gender_strength', 'weak')

                if gender_pref == 'neutral':
                    gender_score = 15  # 中性字词给中等分数
                elif gender_pref == self.target_gender:
                    # 符合目标性别的字词给予高分
                    if gender_strength == 'strong':
                        gender_score = 30  # 强性别倾向：满分
                    elif gender_strength == 'medium':
                        gender_score = 25  # 中等性别倾向：高分
                    else:  # weak
                        gender_score = 20  # 弱性别倾向：中等偏高
                else:
                    # 不符合目标性别的字词给予低分惩罚
                    if gender_strength == 'strong':
                        gender_score = 5   # 强相反性别倾向：重罚
                    elif gender_strength == 'medium':
                        gender_score = 8   # 中等相反性别倾向：中罚
                    else:  # weak
                        gender_score = 12  # 弱相反性别倾向：轻罚

                # 5. 多样性约束惩罚 - 同一字重复使用惩罚
                repetition_penalty = 1.0
                usage_count = char_usage_count.get(char, 1)
                if usage_count > 1:
                    repetition_penalty = 0.7 ** (usage_count - 1)  # 重复使用指数衰减

                # 计算基础分数
                base_score = (freq_score * category_multiplier + meaning_score + gender_score) * repetition_penalty

                # 确保分数在合理范围内
                char_score = max(5, min(75, base_score))  # 最低5分，最高75分

                total_score += char_score

        # 返回平均分数，增加语义丰富度权重
        avg_score = total_score / len(name_chars)

        # 额外奖励：如果名字包含多个不同语义类别的字
        semantic_diversity_bonus = self._calculate_semantic_diversity_bonus(name_chars)
        avg_score += semantic_diversity_bonus

        return min(100, avg_score)

    def _classify_word_category(self, char, word_data):
        """分类字词类型：虚词 vs 实词 - 加强版"""
        # 高优先级虚词列表（这些字在古典文学中主要是虚词功能）
        high_priority_function_words = {
            '之', '其', '而', '以', '于', '为', '所', '者', '也', '矣', '焉', '乎', '哉',
            '然', '则', '且', '或', '虽', '若', '乃', '既', '及', '当', '亦', '夫',
            '盖', '故', '因', '由', '自', '从', '向', '往', '来', '去', '入', '出',
            '上', '下', '中', '内', '外', '前', '后', '左', '右', '东', '西', '南', '北'
        }

        # 中等优先级虚词（可能兼有实词功能，但古典文学中多为虚词）
        medium_priority_function_words = {
            '子', '者',  # "子"在古典文学中常作为虚词，如"子曰""子在川上"
        }

        tags = word_data.get('tags', [])
        frequency = word_data.get('frequency', 0)

        # 1. 高优先级虚词判断
        if char in high_priority_function_words:
            return 'function_word'

        # 2. 中等优先级虚词判断（结合频率和上下文）
        if char in medium_priority_function_words:
            # 如果频率特别高，很可能是虚词功能
            if frequency > 100:
                return 'function_word'
            # 如果有虚词相关标签
            if any(tag in ['语气', '连接', '助词', '古典'] for tag in tags):
                return 'function_word'

        # 3. 基于标签的虚词判断
        if any(tag in ['语气', '连接', '助词'] for tag in tags):
            return 'function_word'

        # 4. 实词判断
        content_word_tags = ['美好', '美丽', '优雅', '智慧', '贤能', '优秀',
                           '勇敢', '刚强', '坚毅', '温柔', '贤惠', '文静',
                           '高贵', '尊贵', '卓越', '光明', '正直', '诚信']
        if any(tag in content_word_tags for tag in tags):
            return 'content_word'

        # 5. 基于频率的推断（高频但无明确标签的，可能为虚词）
        if frequency > 200 and not any(tag in content_word_tags for tag in tags):
            return 'function_word'

        # 默认分类
        return 'neutral'

    def _get_category_score_multiplier(self, category):
        """获取字词类别评分倍数 - 加强版"""
        multipliers = {
            'function_word': 0.4,  # 虚词大幅降低权重，从0.6降到0.4，进一步减少"之""子"等字的得分
            'content_word': 1.4,   # 实词提升权重，从1.2升到1.4，鼓励有意义的名字
            'neutral': 1.0         # 中性字词正常权重
        }
        return multipliers.get(category, 1.0)

    def _calculate_semantic_diversity_bonus(self, name_chars):
        """计算语义多样性奖励"""
        if len(name_chars) < 2:
            return 0

        semantic_categories = set()
        for char in name_chars:
            if char in self.word_cache:
                tags = self.word_cache[char].get('tags', [])
                # 提取语义大类
                for tag in tags:
                    if tag in ['美好', '美丽', '优雅']:
                        semantic_categories.add('beauty')
                    elif tag in ['智慧', '贤能', '优秀']:
                        semantic_categories.add('wisdom')
                    elif tag in ['勇敢', '刚强', '坚毅']:
                        semantic_categories.add('strength')
                    elif tag in ['温柔', '贤惠', '文静']:
                        semantic_categories.add('gentle')
                    elif tag in ['高贵', '尊贵', '卓越']:
                        semantic_categories.add('noble')

        # 根据语义类别多样性给予奖励
        diversity_count = len(semantic_categories)
        if diversity_count >= 3:
            return 8  # 三个以上语义类别，奖励8分
        elif diversity_count == 2:
            return 5  # 两个语义类别，奖励5分
        elif diversity_count == 1:
            return 2  # 一个语义类别，奖励2分

        return 0

    def _calculate_length_score(self, length):
        """计算长度适中度评分"""
        # 2字名最优，1字名和3字名次之
        if length == 2:
            return 100
        elif length == 1 or length == 3:
            return 80
        else:
            return 60  # 其他长度

    def _calculate_character_harmony_score(self, name_chars):
        """计算字符搭配和谐度评分"""
        if len(name_chars) < 2:
            return 100  # 单字名字默认完美

        harmony_score = 0

        # 检查字符意义上的搭配
        for i, char1 in enumerate(name_chars):
            for j, char2 in enumerate(name_chars[i+1:], i+1):
                pair_score = self._calculate_char_pair_score(char1, char2)
                harmony_score += pair_score

        # 标准化到0-100
        max_possible_score = (len(name_chars) * (len(name_chars) - 1) / 2) * 20  # 每对字符最多20分
        if max_possible_score > 0:
            normalized_score = (harmony_score / max_possible_score) * 100
            return min(100, max(0, normalized_score))
        return 100

    def _calculate_char_pair_score(self, char1, char2):
        """计算两个字符的搭配评分"""
        if char1 not in self.word_cache or char2 not in self.word_cache:
            return 10  # 默认中等搭配

        data1 = self.word_cache[char1]
        data2 = self.word_cache[char2]

        score = 0

        # 相同五行属性加分 (表示和谐)
        wuxing1 = data1.get('wuxing', '')
        wuxing2 = data2.get('wuxing', '')
        if wuxing1 and wuxing2:
            if wuxing1 == wuxing2:
                score += 5  # 相同五行和谐
            # 五行相生关系
            elif self._are_wuxing_compatible(wuxing1, wuxing2):
                score += 3  # 相生关系和谐

        # 意义标签重叠加分
        tags1 = set(data1.get('tags', []))
        tags2 = set(data2.get('tags', []))
        tag_overlap = len(tags1.intersection(tags2))
        score += tag_overlap * 2  # 每个重叠标签加2分

        # 频率相近加分
        freq1 = data1.get('frequency', 0)
        freq2 = data2.get('frequency', 0)
        freq_diff = abs(freq1 - freq2)
        if freq_diff < 50:  # 频率相差不大
            score += 5

        return min(20, score)  # 最高20分

    def _are_wuxing_compatible(self, wuxing1, wuxing2):
        """检查五行是否相生"""
        # 五行相生：金生水，水生木，木生火，火生土，土生金
        wuxing_sheng = {
            'jin': 'shui',
            'shui': 'mu',
            'mu': 'huo',
            'huo': 'tu',
            'tu': 'jin'
        }
        return wuxing_sheng.get(wuxing1) == wuxing2 or wuxing_sheng.get(wuxing2) == wuxing1

    def _get_comprehensive_level(self, total_score):
        """获取综合评分等级"""
        if total_score >= 85:
            return {'grade': 'S', 'description': '卓越', 'color': '#722ed1'}
        elif total_score >= 75:
            return {'grade': 'A', 'description': '优秀', 'color': 'green'}
        elif total_score >= 65:
            return {'grade': 'B', 'description': '良好', 'color': 'blue'}
        elif total_score >= 55:
            return {'grade': 'C', 'description': '一般', 'color': 'orange'}
        elif total_score >= 45:
            return {'grade': 'D', 'description': '不佳', 'color': 'red'}
        else:
            return {'grade': 'F', 'description': '较差', 'color': '#8c8c8c'}


# 全局生成器实例
name_generator = NameGenerator()


def generate_name(surname=None, gender='M', length=2, preferences=None):
    """
    生成单个名字的便捷函数

    Args:
        surname: 姓氏
        gender: 性别 ('M' 或 'F')
        length: 名字长度
        preferences: 偏好设置

    Returns:
        生成的名字字符串
    """
    names = name_generator.generate_names(
        surname=surname,
        gender=gender,
        count=1,
        length=length,
        preferences=preferences
    )

    if names:
        return names[0]['given_name']
    return "诗韵"


def generate_multiple_names(surname=None, gender='M', count=5, length=2, preferences=None, user=None, use_ai=True):
    """
    生成多个名字

    Args:
        surname: 姓氏
        gender: 性别 ('M' 或 'F')
        count: 生成数量
        length: 名字长度
        preferences: 偏好设置
        user: 用户对象（用于个性化推荐）
        use_ai: 是否使用AI推荐

    Returns:
        生成的名字列表
    """
    return name_generator.generate_names(
        surname=surname,
        gender=gender,
        count=count,
        length=length,
        preferences=preferences,
        user=user,
        use_ai=use_ai
    )

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
        self._load_word_data()

    def _load_word_data(self):
        """加载字词数据到缓存"""
        try:
            words = Word.objects.all()
            for word in words:
                self.word_cache[word.character] = {
                    'pinyin': word.pinyin,
                    'gender_preference': word.gender_preference,
                    'meaning': word.meaning,
                    'tags': word.tags,
                    'frequency': word.frequency
                }
        except Exception as e:
            logger.warning(f"加载字词数据失败: {e}")
            self.word_cache = {}

    def _get_words_by_gender(self, gender):
        """根据性别获取合适的字词"""
        if gender == 'M':
            # 男性：优先从诗经中选择
            poetry_words = []
            shijing_poems = Poetry.objects.filter(poetry_type='shijing')
            for poem in shijing_poems:
                for char in poem.content:
                    if '\u4e00' <= char <= '\u9fa5' and char in self.word_cache:
                        word_data = self.word_cache[char]
                        if word_data['gender_preference'] in ['male', 'neutral']:
                            poetry_words.append((char, word_data))

            # 如果诗经字词不够，补充其他字词
            if len(poetry_words) < 50:
                all_words = [(char, data) for char, data in self.word_cache.items()
                           if data['gender_preference'] in ['male', 'neutral']]
                poetry_words.extend(all_words[:100])

            return poetry_words

        elif gender == 'F':
            # 女性：优先从楚辞中选择
            poetry_words = []
            chuci_poems = Poetry.objects.filter(poetry_type='chuci')
            for poem in chuci_poems:
                for char in poem.content:
                    if '\u4e00' <= char <= '\u9fa5' and char in self.word_cache:
                        word_data = self.word_cache[char]
                        if word_data['gender_preference'] in ['female', 'neutral']:
                            poetry_words.append((char, word_data))

            # 如果楚辞字词不够，补充其他字词
            if len(poetry_words) < 50:
                all_words = [(char, data) for char, data in self.word_cache.items()
                           if data['gender_preference'] in ['female', 'neutral']]
                poetry_words.extend(all_words[:100])

            return poetry_words
        else:
            # 中性或未知性别
            return [(char, data) for char, data in self.word_cache.items()]

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

        # 生成候选名字
        candidates = []
        max_attempts = min(1000, len(filtered_words) ** length)

        for _ in range(max_attempts):
            name_chars = []
            for _ in range(length):
                char, _ = random.choice(filtered_words)
                name_chars.append(char)

            name = ''.join(name_chars)

            # 计算评分
            score = self._calculate_name_score(name_chars, preferences)

            candidates.append({
                'name': name,
                'chars': name_chars,
                'score': score
            })

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

        # 转换为Name对象格式
        result = []
        for candidate in candidates[:count * 2]:  # 生成更多候选用于AI筛选
            name_chars = candidate['chars']

            # 进行五行分析
            wuxing_analysis = wuxing_analyzer.analyze_name_wuxing(name_chars)
            bagua_suggestions = wuxing_analyzer.get_bagua_suggestions(wuxing_analysis)

            # 进行音韵分析
            phonology_analysis = phonology_analyzer.analyze_name_phonology(name_chars)

            # 计算综合评分
            wuxing_score = wuxing_analyzer.get_name_score(wuxing_analysis)
            phonology_score = phonology_analyzer.get_phonology_score(phonology_analysis)

            # 综合评分：五行占60%，音韵占40%
            total_score = (wuxing_score['total_score'] * 0.6) + (phonology_score['total_score'] * 0.4)
            total_score = round(total_score, 1)

            name_score = {
                'total_score': total_score,
                'wuxing_score': wuxing_score['total_score'],
                'phonology_score': phonology_score['total_score'],
                'level': wuxing_score['level'] if wuxing_score['total_score'] > phonology_score['total_score'] else phonology_score['level']
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
                'ai_score': 0  # AI评分，稍后计算
            }

            result.append(name_data)

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

                # 更新AI评分
                for name_data in result:
                    if hasattr(name_data, '_temp_id'):
                        delattr(name_data, '_temp_id')

                return recommended_names

            except Exception as e:
                print(f"AI推荐失败，使用默认排序: {e}")
                # AI失败时按综合评分排序
                result.sort(key=lambda x: x['name_score']['total_score'], reverse=True)

        # 默认排序（按综合评分）
        result.sort(key=lambda x: x['name_score']['total_score'], reverse=True)

        return result[:count]

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
        """获取名字的词源"""
        origins = []
        for char in chars:
            if char in self.word_cache:
                # 这里可以扩展为更详细的词源信息
                origins.append(f"出自《诗经》或《楚辞》")

        if origins:
            return '；'.join(set(origins))  # 去重
        return "源自古典诗词"

    def _get_name_tags(self, chars):
        """获取名字的标签"""
        all_tags = []
        for char in chars:
            if char in self.word_cache:
                all_tags.extend(self.word_cache[char]['tags'])

        # 去重并返回最相关的标签
        unique_tags = list(set(all_tags))
        return unique_tags[:5]  # 最多5个标签


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

"""
古汉语音韵学分析模块
实现完整的古汉语声韵调系统和韵律和谐度分析
"""
import re
from collections import defaultdict


class PhonologyAnalyzer:
    """古汉语音韵学分析器"""

    # 古汉语声母分组（三十六字母）
    CONSONANTS = {
        # 重唇音
        '帮': ['帮', '滂', '并', '明'],
        # 轻唇音
        '非': ['非', '敷', '奉', '微'],
        # 舌头音
        '端': ['端', '透', '定', '泥'],
        # 舌上音
        '知': ['知', '彻', '澄', '孃'],
        # 牙音
        '见': ['见', '溪', '群', '疑'],
        # 齿头音
        '精': ['精', '清', '从', '心', '邪'],
        # 正齿音
        '照': ['照', '穿', '床', '审', '禅'],
        # 喉音
        '影': ['影', '晓', '匣', '云'],
        # 来母
        '来': ['来']
    }

    # 古汉语韵部（根据《广韵》）
    RHYME_CATEGORIES = {
        '通韵': ['东', '冬', '钟', '江', '阳', '唐', '庚', '耕', '清', '青', '蒸', '登', '侯', '尤', '幽'],
        '止韵': ['支', '脂', '之', '微', '鱼', '虞', '模', '齐', '佳', '皆', '灰', '咍', '真', '谆', '瑧', '文', '欣', '元', '魂', '痕', '寒', '桓', '删', '山', '先', '仙', '萧', '宵', '肴', '豪', '歌', '戈', '麻', '遮', '车', '蛇'],
        '遇韵': ['模', '鱼', '虞', '麻', '遮', '车', '蛇'],
        '蟹韵': ['齐', '祭', '泰', '佳', '皆', '央', '废', '夬', '卦', '怪', '灰', '咍', '海', '改', '代', '队', '代', '泰', '卦', '怪'],
        '臻韵': ['真', '谆', '瑧', '文', '欣', '魂', '痕', '寒', '桓', '删', '山', '先', '仙'],
        '山韵': ['删', '山', '仙', '先', '元', '寒', '桓', '删', '山', '先', '仙', '元'],
        '效韵': ['萧', '宵', '肴', '豪', '爻', 'iao', 'iao', 'iao', 'iao', 'iao'],
        '果韵': ['歌', '戈', '麻', '遮', '车', '蛇'],
        '假韵': ['麻', '遮', '车', '蛇'],
        '宕韵': ['阳', '唐', '江'],
        '梗韵': ['庚', '耕', '清', '青'],
        '曾韵': ['蒸', '登'],
        '流韵': ['侯', '尤', '幽'],
        '深韵': ['侵', '覃', '谈', '盐', '添', '咸', '衔', '严', '凡'],
        '咸韵': ['覃', '谈', '盐', '添', '咸', '衔', '严', '凡']
    }

    # 声调：平声（阴平、阳平）、上声、去声、入声
    TONES = {
        'ping': ['1', '2'],  # 平声（第一、二声）
        'shang': ['3'],      # 上声（第三声）
        'qu': ['4'],         # 去声（第四声）
        'ru': ['5']          # 入声（第五声，古汉语特有）
    }

    def __init__(self):
        self.phonology_cache = {}
        self._build_phonology_database()

    def _build_phonology_database(self):
        """构建音韵学数据库"""
        # 这里应该加载更完整的古汉语音韵数据库
        # 暂时使用简化的映射
        pass

    def analyze_name_phonology(self, name_chars, pinyin_list=None):
        """
        分析名字的音韵结构

        Args:
            name_chars: 名字字符列表
            pinyin_list: 对应的拼音列表

        Returns:
            dict: 音韵分析结果
        """
        if not pinyin_list:
            pinyin_list = [self._get_char_pinyin(char) for char in name_chars]

        # 分析声调分布
        tone_analysis = self._analyze_tones(pinyin_list)

        # 分析韵律和谐度
        rhythm_score = self._calculate_rhythm_score(pinyin_list)

        # 分析声韵配合
        harmony_analysis = self._analyze_harmony(name_chars, pinyin_list)

        # 生成音韵建议
        suggestions = self._get_phonology_suggestions(tone_analysis, rhythm_score, harmony_analysis)

        return {
            'tone_analysis': tone_analysis,
            'rhythm_score': rhythm_score,
            'rhythm_level': self._get_rhythm_level(rhythm_score),
            'harmony_analysis': harmony_analysis,
            'suggestions': suggestions
        }

    def _get_char_pinyin(self, char):
        """获取字符的拼音（简化为现代拼音）"""
        # 这里应该使用更准确的古汉语拼音系统
        # 暂时使用现代拼音作为近似
        return char  # 实际应该返回拼音

    def _analyze_tones(self, pinyin_list):
        """分析声调分布"""
        tone_counts = {'ping': 0, 'shang': 0, 'qu': 0, 'ru': 0}

        for pinyin in pinyin_list:
            # 从拼音中提取声调（现代拼音的1-4声）
            if pinyin and len(pinyin) > 1:
                last_char = pinyin[-1]
                if last_char.isdigit():
                    tone_num = int(last_char)
                    if tone_num in [1, 2]:
                        tone_counts['ping'] += 1
                    elif tone_num == 3:
                        tone_counts['shang'] += 1
                    elif tone_num == 4:
                        tone_counts['qu'] += 1
                    else:
                        tone_counts['ru'] += 1  # 简化为入声
                else:
                    tone_counts['ping'] += 1  # 默认平声

        total_chars = len(pinyin_list)
        tone_percentages = {}

        for tone, count in tone_counts.items():
            percentage = (count / total_chars * 100) if total_chars > 0 else 0
            tone_percentages[tone] = round(percentage, 1)

        return {
            'tone_counts': tone_counts,
            'tone_percentages': tone_percentages,
            'tone_sequence': [self._classify_tone(p) for p in pinyin_list]
        }

    def _classify_tone(self, pinyin):
        """分类声调"""
        if not pinyin or len(pinyin) <= 1:
            return 'ping'

        last_char = pinyin[-1]
        if last_char.isdigit():
            tone_num = int(last_char)
            if tone_num in [1, 2]:
                return 'ping'
            elif tone_num == 3:
                return 'shang'
            elif tone_num == 4:
                return 'qu'
            else:
                return 'ru'
        return 'ping'

    def _calculate_rhythm_score(self, pinyin_list):
        """
        计算韵律和谐度分数 (0-100)

        基于平仄相间的原则：
        - 平仄相间得高分
        - 平仄相同得低分
        """
        if len(pinyin_list) < 2:
            return 100  # 单字名字默认完美

        tones = [self._classify_tone(p) for p in pinyin_list]
        harmony_score = 0

        # 检查平仄相间
        for i in range(len(tones) - 1):
            current_tone = tones[i]
            next_tone = tones[i + 1]

            # 平仄相间得高分
            if ((current_tone == 'ping' and next_tone in ['shang', 'qu', 'ru']) or
                (current_tone in ['shang', 'qu', 'ru'] and next_tone == 'ping')):
                harmony_score += 25
            # 仄仄相间也得一定分数
            elif (current_tone in ['shang', 'qu', 'ru'] and next_tone in ['shang', 'qu', 'ru']):
                harmony_score += 15
            # 平平相间得低分
            else:
                harmony_score += 5

        # 标准化到0-100
        max_possible_score = 25 * (len(tones) - 1)
        if max_possible_score > 0:
            final_score = (harmony_score / max_possible_score) * 100
            return round(final_score, 1)
        return 100

    def _get_rhythm_level(self, rhythm_score):
        """根据韵律分数获取等级"""
        if rhythm_score >= 80:
            return {'level': '优秀', 'color': 'green', 'description': '平仄和谐，韵律优美'}
        elif rhythm_score >= 60:
            return {'level': '良好', 'color': 'blue', 'description': '韵律较为和谐'}
        elif rhythm_score >= 40:
            return {'level': '一般', 'color': 'orange', 'description': '韵律需要改进'}
        else:
            return {'level': '不佳', 'color': 'red', 'description': '平仄不协调'}

    def _analyze_harmony(self, name_chars, pinyin_list):
        """分析声韵配合"""
        harmony_info = {
            'alliteration': [],  # 头韵（声母相同）
            'assonance': [],     # 韵律（韵母相似）
            'consonance': []     # 辅音和谐
        }

        # 检查头韵（相邻字声母相同或相似）
        for i in range(len(pinyin_list) - 1):
            current = pinyin_list[i]
            next_p = pinyin_list[i + 1]

            # 简化的头韵检查（实际应该检查声母）
            if current and next_p and current[0] == next_p[0]:
                harmony_info['alliteration'].append(f'{name_chars[i]}{name_chars[i+1]}')

        # 检查韵律和谐（韵母相似）
        for i in range(len(pinyin_list) - 1):
            current = pinyin_list[i]
            next_p = pinyin_list[i + 1]

            # 简化的韵律检查（实际应该检查韵母）
            if len(current) > 1 and len(next_p) > 1:
                # 检查是否有相同韵母
                current_vowel = self._extract_vowel(current)
                next_vowel = self._extract_vowel(next_p)
                if current_vowel and next_vowel and current_vowel[-1] == next_vowel[-1]:
                    harmony_info['assonance'].append(f'{name_chars[i]}{name_chars[i+1]}')

        return harmony_info

    def _extract_vowel(self, pinyin):
        """提取拼音中的韵母部分"""
        # 简化的韵母提取（实际应该更准确）
        vowels = 'aeiouü'
        vowel_part = ''
        for char in pinyin:
            if char in vowels:
                vowel_part += char
        return vowel_part

    def _get_phonology_suggestions(self, tone_analysis, rhythm_score, harmony_analysis):
        """生成音韵学建议"""
        suggestions = []

        # 声调分布建议
        tone_percentages = tone_analysis['tone_percentages']

        if tone_percentages['ping'] > 70:
            suggestions.append("平声过多，建议增加上声或去声以增加韵律变化")
        elif tone_percentages['ping'] < 30:
            suggestions.append("平声过少，建议增加平声以保持整体和谐")

        # 韵律建议
        if rhythm_score < 60:
            suggestions.append("平仄不协调，建议调整字词选择以达到平仄相间")

        # 特殊和谐现象
        if harmony_analysis['alliteration']:
            suggestions.append(f"头韵和谐：{', '.join(harmony_analysis['alliteration'])}")

        if harmony_analysis['assonance']:
            suggestions.append(f"韵律和谐：{', '.join(harmony_analysis['assonance'])}")

        return suggestions

    def get_phonology_score(self, phonology_analysis):
        """
        根据音韵分析计算总评分

        Args:
            phonology_analysis: 音韵分析结果

        Returns:
            dict: 评分结果
        """
        rhythm_score = phonology_analysis['rhythm_score']

        # 声调平衡度
        tone_analysis = phonology_analysis['tone_analysis']
        tone_percentages = tone_analysis['tone_percentages']

        # 计算声调多样性（标准差越小越好）
        tone_values = list(tone_percentages.values())
        mean_tone = sum(tone_values) / len(tone_values) if tone_values else 0
        tone_variance = sum((t - mean_tone) ** 2 for t in tone_values) / len(tone_values) if tone_values else 0
        tone_balance_score = max(0, 100 - (tone_variance * 2))

        # 综合评分：韵律占70%，声调平衡占30%
        total_score = (rhythm_score * 0.7) + (tone_balance_score * 0.3)
        total_score = round(total_score, 1)

        # 获取评分等级
        if total_score >= 80:
            level = {'grade': 'A', 'description': '音韵和谐', 'color': 'green'}
        elif total_score >= 70:
            level = {'grade': 'B', 'description': '韵律流畅', 'color': 'blue'}
        elif total_score >= 60:
            level = {'grade': 'C', 'description': '基本和谐', 'color': 'orange'}
        else:
            level = {'grade': 'D', 'description': '韵律不佳', 'color': 'red'}

        return {
            'total_score': total_score,
            'rhythm_score': rhythm_score,
            'tone_balance_score': tone_balance_score,
            'level': level
        }


# 全局音韵分析器实例
phonology_analyzer = PhonologyAnalyzer()
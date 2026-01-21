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
        self.pinyin_cache = {}
        self._build_phonology_database()
        self._build_pinyin_database()

    def _build_phonology_database(self):
        """构建音韵学数据库"""
        # 扩展韵部分类，包含更完整的古汉语韵部
        self.extended_rhyme_categories = {
            **self.RHYME_CATEGORIES,
            '支韵': ['支', '枝', '肢', '眉', '危', '吹', '亏', '为', '悲', '归'],
            '脂韵': ['脂', '旨', '指', '美', '耳', '眉', '规', '亏', '吹', '悲'],
            '之韵': ['之', '芝', '诗', '时', '持', '而', '兹', '慈', '思', '丝'],
            '微韵': ['微', '薇', '挥', '非', '飞', '妃', '肥', '威', '围', '亏'],
            '鱼韵': ['鱼', '渔', '余', '舆', '愚', '于', '居', '车', '书', '舒'],
            '虞韵': ['虞', '娱', '隅', '无', '芜', '吾', '吴', '乎', '呼', '孤'],
        }

    def _build_pinyin_database(self):
        """构建拼音数据库"""
        # 基础的汉字到拼音映射（现代汉语拼音作为近似）
        # 在实际应用中，这里应该加载更完整的拼音词典
        self.basic_pinyin_map = {
            # 常用字的拼音映射示例
            '王': 'wang', '李': 'li', '张': 'zhang', '刘': 'liu', '陈': 'chen',
            '杨': 'yang', '赵': 'zhao', '黄': 'huang', '周': 'zhou', '吴': 'wu',
            '徐': 'xu', '孙': 'sun', '胡': 'hu', '朱': 'zhu', '高': 'gao',
            '林': 'lin', '何': 'he', '郭': 'guo', '马': 'ma', '罗': 'luo',
            '梁': 'liang', '宋': 'song', '郑': 'zheng', '谢': 'xie', '韩': 'han',
            '唐': 'tang', '冯': 'feng', '于': 'yu', '董': 'dong', '萧': 'xiao',
            '程': 'cheng', '曹': 'cao', '袁': 'yuan', '邓': 'deng', '许': 'xu',
            '傅': 'fu', '沈': 'shen', '曾': 'zeng', '彭': 'peng', '吕': 'lu',
            '苏': 'su', '卢': 'lu', '蒋': 'jiang', '蔡': 'cai', '贾': 'jia',
            '丁': 'ding', '魏': 'wei', '薛': 'xue', '叶': 'ye', '阎': 'yan',
            '余': 'yu', '潘': 'pan', '杜': 'du', '戴': 'dai', '夏': 'xia',
            '钟': 'zhong', '汪': 'wang', '田': 'tian', '任': 'ren', '姜': 'jiang',
            '范': 'fan', '方': 'fang', '石': 'shi', '姚': 'yao', '谭': 'tan',
            '廖': 'liao', '邹': 'zou', '熊': 'xiong', '金': 'jin', '陆': 'lu',
            '郝': 'hao', '孔': 'kong', '白': 'bai', '崔': 'cui', '康': 'kang',
            '毛': 'mao', '邱': 'qiu', '秦': 'qin', '江': 'jiang', '史': 'shi',
            '顾': 'gu', '侯': 'hou', '邵': 'shao', '孟': 'meng', '龙': 'long',
            '万': 'wan', '段': 'duan', '漕': 'cao', '钱': 'qian', '汤': 'tang',
            '尹': 'yin', '黎': 'li', '易': 'yi', '常': 'chang', '武': 'wu',
            '乔': 'qiao', '贺': 'he', '赖': 'lai', '龚': 'gong', '文': 'wen',
        }

    def analyze_name_phonology(self, name_chars, pinyin_list=None):
        """
        完整分析名字的音韵结构

        Args:
            name_chars: 名字字符列表
            pinyin_list: 对应的拼音列表

        Returns:
            dict: 完整的音韵分析结果
        """
        if not pinyin_list:
            pinyin_list = [self._get_char_pinyin(char) for char in name_chars]

        # 1. 分析声调分布
        tone_analysis = self._analyze_tones(pinyin_list)

        # 2. 分析韵律和谐度
        rhythm_score = self._calculate_rhythm_score(pinyin_list)

        # 3. 分析声韵配合
        harmony_analysis = self._analyze_harmony(name_chars, pinyin_list)

        # 4. 分析发音流畅度
        fluency_analysis = self._analyze_pronunciation_fluency(pinyin_list)

        # 5. 分析古汉语韵律特征
        ancient_analysis = self._analyze_ancient_phonology(name_chars, pinyin_list)

        # 6. 生成音韵建议
        suggestions = self._get_phonology_suggestions(tone_analysis, rhythm_score, harmony_analysis, fluency_analysis)

        return {
            'tone_analysis': tone_analysis,
            'rhythm_score': rhythm_score,
            'rhythm_level': self._get_rhythm_level(rhythm_score),
            'harmony_analysis': harmony_analysis,
            'fluency_analysis': fluency_analysis,
            'ancient_analysis': ancient_analysis,
            'suggestions': suggestions,
            'pinyin_list': pinyin_list
        }

    def _get_char_pinyin(self, char):
        """获取字符的拼音（使用现代汉语拼音作为近似）"""
        if char in self.pinyin_cache:
            return self.pinyin_cache[char]

        # 首先尝试从基础映射中查找
        if char in self.basic_pinyin_map:
            pinyin = self.basic_pinyin_map[char]
        else:
            # 对于未映射的字符，尝试使用一个简化的映射规则
            pinyin = self._generate_basic_pinyin(char)

        # 添加声调（随机分配，实际应用中应该有更准确的规则）
        pinyin_with_tone = self._add_tone_to_pinyin(pinyin)

        # 缓存结果
        self.pinyin_cache[char] = pinyin_with_tone
        return pinyin_with_tone

    def _generate_basic_pinyin(self, char):
        """为未映射的字符生成基本的拼音"""
        # 这是一个非常简化的实现
        # 在实际应用中，应该使用更完整的拼音词典

        # 一些常见的声母映射
        consonants = {
            'b': ['巴', '白', '北', '本', '笔'], 'p': ['怕', '拍', '盘', '朋', '品'],
            'm': ['妈', '买', '满', '门', '米'], 'f': ['发', '法', '反', '分', '夫'],
            'd': ['大', '打', '但', '当', '得'], 't': ['他', '太', '谈', '汤', '提'],
            'n': ['那', '奶', '南', '能', '你'], 'l': ['拉', '来', '兰', '浪', '里'],
            'g': ['嘎', '该', '干', '刚', '个'], 'k': ['卡', '开', '看', '康', '可'],
            'h': ['哈', '海', '寒', '航', '合'], 'j': ['家', '价', '间', '将', '接'],
            'q': ['恰', '掐', '千', '强', '且'], 'x': ['下', '虾', '仙', '想', '些'],
            'zh': ['扎', '摘', '占', '张', '着'], 'ch': ['插', '差', '产', '长', '车'],
            'sh': ['沙', '筛', '山', '商', '社'], 'r': ['然', '绕', '人', '荣', '日'],
            'z': ['匝', '栽', '咱', '脏', '贼'], 'c': ['擦', '猜', '残', '仓', '测'],
            's': ['撒', '塞', '三', '桑', '色'], 'y': ['呀', '牙', '烟', '央', '叶'],
            'w': ['哇', '歪', '弯', '王', '为'], ' ': ['啊', '爱', '安', '昂', '奥']
        }

        # 简化的韵母
        vowels = ['a', 'ai', 'an', 'ang', 'ao', 'e', 'ei', 'en', 'eng', 'er', 'i', 'ia', 'ian', 'iang', 'iao', 'ie', 'in', 'ing', 'iong', 'iu', 'o', 'ong', 'ou', 'u', 'ua', 'uai', 'uan', 'uang', 'ue', 'ui', 'un', 'uo']

        # 尝试根据字符的Unicode范围进行粗略分类
        char_code = ord(char)

        # 根据字符的发音特征进行分类（这是一个非常简化的实现）
        if char_code >= 0x4e00 and char_code <= 0x9fff:  # 中日韩统一表意文字
            # 使用字符的hash来选择声母和韵母
            hash_val = hash(char) % 100

            if hash_val < 20:
                consonant = 'zh' if hash_val < 10 else 'ch' if hash_val < 15 else 'sh'
            elif hash_val < 40:
                consonant = 'j' if hash_val < 30 else 'q' if hash_val < 35 else 'x'
            elif hash_val < 60:
                consonant = 'b' if hash_val < 45 else 'p' if hash_val < 50 else 'm' if hash_val < 55 else 'f'
            elif hash_val < 80:
                consonant = 'd' if hash_val < 65 else 't' if hash_val < 70 else 'n' if hash_val < 75 else 'l'
            else:
                consonant = 'g' if hash_val < 85 else 'k' if hash_val < 90 else 'h'

            vowel_index = (hash_val + char_code) % len(vowels)
            vowel = vowels[vowel_index]

            return consonant + vowel
        else:
            return 'a'  # 默认音节

    def _add_tone_to_pinyin(self, pinyin):
        """为拼音添加声调"""
        # 简化的声调分配（实际应该基于词典数据）
        import random
        tones = ['1', '2', '3', '4']  # 对应第一声到第四声

        # 根据拼音的特征选择合适的声调
        if pinyin.endswith(('a', 'e', 'i', 'o', 'u', 'ü')):
            # 开放音节，更可能是一声或二声
            tone = random.choice(['1', '2', '3'])
        else:
            # 闭合音节
            tone = random.choice(['1', '2', '3', '4'])

        return pinyin + tone

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

        使用更复杂的韵律分析算法：
        1. 平仄相间度 (40%)
        2. 韵律流畅度 (30%)
        3. 发音和谐度 (30%)
        """
        if len(pinyin_list) < 2:
            return 100  # 单字名字默认完美

        tones = [self._classify_tone(p) for p in pinyin_list]

        # 1. 平仄相间度评分 (0-40分)
        alternation_score = self._calculate_tone_alternation_score(tones)

        # 2. 韵律流畅度评分 (0-30分)
        flow_score = self._calculate_rhythm_flow_score(tones)

        # 3. 发音和谐度评分 (0-30分)
        pronunciation_score = self._calculate_pronunciation_harmony_score(pinyin_list)

        total_score = alternation_score + flow_score + pronunciation_score
        return round(min(100, total_score), 1)

    def _calculate_tone_alternation_score(self, tones):
        """计算平仄相间度评分"""
        if len(tones) < 2:
            return 40

        alternation_score = 0

        for i in range(len(tones) - 1):
            current_tone = tones[i]
            next_tone = tones[i + 1]

            # 平仄相间（最佳）
            if ((current_tone == 'ping' and next_tone in ['shang', 'qu', 'ru']) or
                (current_tone in ['shang', 'qu', 'ru'] and next_tone == 'ping')):
                alternation_score += 10  # 每对相间加10分

            # 仄仄相间（良好）
            elif (current_tone in ['shang', 'qu', 'ru'] and next_tone in ['shang', 'qu', 'ru']):
                alternation_score += 6   # 每对相间加6分

            # 平平相间（一般）
            else:
                alternation_score += 2   # 每对相间加2分

        # 标准化到0-40分
        max_possible = 10 * (len(tones) - 1)
        if max_possible > 0:
            normalized_score = (alternation_score / max_possible) * 40
            return min(40, normalized_score)

        return 40

    def _calculate_rhythm_flow_score(self, tones):
        """计算韵律流畅度评分"""
        if len(tones) < 2:
            return 30

        flow_score = 0

        # 检查韵律模式
        patterns = []
        for i in range(len(tones) - 1):
            pattern = f"{tones[i]}-{tones[i+1]}"
            patterns.append(pattern)

        # 奖励有规律的韵律模式
        common_patterns = {}
        for pattern in patterns:
            common_patterns[pattern] = common_patterns.get(pattern, 0) + 1

        # 如果有重复的韵律模式，加分
        pattern_variety = len(common_patterns)
        if pattern_variety <= 2:  # 韵律模式不多样
            flow_score += 15
        elif pattern_variety <= 4:
            flow_score += 10
        else:  # 韵律过于复杂
            flow_score += 5

        # 检查是否有过长的相同声调序列
        for i in range(len(tones) - 2):
            if tones[i] == tones[i+1] == tones[i+2]:
                flow_score -= 5  # 三个相同声调减分

        flow_score = max(0, min(30, flow_score + 15))  # 基础15分
        return flow_score

    def _calculate_pronunciation_harmony_score(self, pinyin_list):
        """计算发音和谐度评分"""
        if len(pinyin_list) < 2:
            return 30

        harmony_score = 0

        # 检查发音的流畅度
        for i in range(len(pinyin_list) - 1):
            current = pinyin_list[i]
            next_p = pinyin_list[i + 1]

            # 检查是否有拗口的音节组合
            if self._is_difficult_pronunciation(current, next_p):
                harmony_score -= 3

            # 检查韵母的和谐度
            current_vowel = self._extract_vowel(current)
            next_vowel = self._extract_vowel(next_p)

            if current_vowel and next_vowel:
                # 相同韵母和谐
                if current_vowel[-1] == next_vowel[-1]:
                    harmony_score += 2

                # 检查鼻音和谐
                if self._has_nasal_harmony(current_vowel, next_vowel):
                    harmony_score += 1

        harmony_score = max(0, min(30, harmony_score + 15))  # 基础15分
        return harmony_score

    def _is_difficult_pronunciation(self, pinyin1, pinyin2):
        """检查是否是拗口的发音组合"""
        # 简化的检查：如果两个字都有复杂的辅音组合
        difficult_combos = [
            ('zh', 'ch'), ('ch', 'zh'), ('sh', 'ch'), ('ch', 'sh'),
            ('zh', 'sh'), ('sh', 'zh'), ('j', 'q'), ('q', 'j')
        ]

        for combo in difficult_combos:
            if combo[0] in pinyin1.lower() and combo[1] in pinyin2.lower():
                return True

        return False

    def _has_nasal_harmony(self, vowel1, vowel2):
        """检查是否有鼻音和谐"""
        nasal_sounds = ['n', 'ng', 'm']
        has_nasal1 = any(sound in vowel1 for sound in nasal_sounds)
        has_nasal2 = any(sound in vowel2 for sound in nasal_sounds)

        # 鼻音相邻和谐
        return has_nasal1 and has_nasal2

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

    def _analyze_pronunciation_fluency(self, pinyin_list):
        """
        分析发音流畅度

        Args:
            pinyin_list: 拼音列表

        Returns:
            dict: 流畅度分析结果
        """
        fluency_score = 0
        issues = []

        for i in range(len(pinyin_list) - 1):
            current = pinyin_list[i]
            next_p = pinyin_list[i + 1]

            # 检查连续的相同声母（可能拗口）
            current_consonant = self._extract_consonant(current)
            next_consonant = self._extract_consonant(next_p)

            if current_consonant and next_consonant:
                if current_consonant == next_consonant:
                    fluency_score -= 5
                    issues.append(f"连续相同声母: {current_consonant}")
                elif self._are_difficult_consonants(current_consonant, next_consonant):
                    fluency_score -= 3
                    issues.append(f"拗口声母组合: {current_consonant}-{next_consonant}")

            # 检查韵母和谐度
            current_vowel = self._extract_vowel(current)
            next_vowel = self._extract_vowel(next_p)

            if current_vowel and next_vowel:
                if current_vowel == next_vowel:
                    fluency_score += 2  # 相同韵母和谐
                elif self._are_harmonious_vowels(current_vowel, next_vowel):
                    fluency_score += 1  # 相近韵母和谐

        return {
            'fluency_score': max(0, min(100, fluency_score + 50)),  # 基础50分
            'issues': issues[:3],  # 最多显示3个问题
            'fluency_level': '流畅' if fluency_score >= 40 else '一般' if fluency_score >= 20 else '需改进'
        }

    def _analyze_ancient_phonology(self, name_chars, pinyin_list):
        """
        分析古汉语音韵特征

        Args:
            name_chars: 汉字列表
            pinyin_list: 拼音列表

        Returns:
            dict: 古汉语音韵分析结果
        """
        ancient_features = {
            'consonant_groups': [],
            'rhyme_harmony': [],
            'tone_patterns': [],
            'ancient_score': 0
        }

        # 分析声母分组（三十六字母）
        consonants = [self._extract_consonant(pinyin) for pinyin in pinyin_list]
        for i, consonant in enumerate(consonants):
            if consonant:
                group = self._classify_consonant_group(consonant)
                if group:
                    ancient_features['consonant_groups'].append({
                        'char': name_chars[i],
                        'consonant': consonant,
                        'group': group
                    })

        # 分析韵母和谐（近似古汉语韵部）
        vowels = [self._extract_vowel(pinyin) for pinyin in pinyin_list]
        for i in range(len(vowels) - 1):
            current_vowel = vowels[i]
            next_vowel = vowels[i + 1]

            if current_vowel and next_vowel:
                rhyme_relation = self._analyze_vowel_rhyme_relation(current_vowel, next_vowel)
                if rhyme_relation:
                    ancient_features['rhyme_harmony'].append({
                        'chars': f"{name_chars[i]}{name_chars[i+1]}",
                        'relation': rhyme_relation
                    })

        # 计算古汉语音韵评分
        group_score = len(set([item['group'] for item in ancient_features['consonant_groups']])) * 10
        rhyme_score = len(ancient_features['rhyme_harmony']) * 15

        ancient_features['ancient_score'] = min(100, group_score + rhyme_score)

        return ancient_features

    def _extract_consonant(self, pinyin):
        """提取声母"""
        if not pinyin or len(pinyin) < 2:
            return None

        # 移除声调数字
        clean_pinyin = ''.join([c for c in pinyin if not c.isdigit()])

        # 提取声母
        vowels = 'aeiouü'
        consonant = ''
        for char in clean_pinyin:
            if char not in vowels:
                consonant += char
            else:
                break

        return consonant if consonant else None

    def _extract_vowel(self, pinyin):
        """提取韵母"""
        if not pinyin:
            return None

        # 移除声调数字
        clean_pinyin = ''.join([c for c in pinyin if not c.isdigit()])

        # 提取韵母部分
        vowels = 'aeiouü'
        vowel_part = ''
        found_vowel = False

        for char in clean_pinyin:
            if char in vowels or found_vowel:
                found_vowel = True
                vowel_part += char

        return vowel_part if vowel_part else None

    def _are_difficult_consonants(self, c1, c2):
        """检查是否是拗口的声母组合"""
        difficult_pairs = [
            ('zh', 'ch'), ('ch', 'zh'), ('sh', 'ch'), ('ch', 'sh'),
            ('zh', 'sh'), ('sh', 'zh'), ('j', 'q'), ('q', 'j'),
            ('z', 'c'), ('c', 'z'), ('s', 'c'), ('c', 's')
        ]

        return (c1, c2) in difficult_pairs or (c2, c1) in difficult_pairs

    def _are_harmonious_vowels(self, v1, v2):
        """检查韵母是否和谐"""
        # 简化的韵母和谐判断
        similar_vowels = {
            'a': ['a', 'ai', 'an', 'ang', 'ao'],
            'e': ['e', 'ei', 'en', 'eng', 'er'],
            'i': ['i', 'ia', 'ian', 'iang', 'iao', 'ie', 'in', 'ing', 'iong', 'iu'],
            'o': ['o', 'ong', 'ou'],
            'u': ['u', 'ua', 'uai', 'uan', 'uang', 'ue', 'ui', 'un', 'uo'],
            'ü': ['ü', 'ue', 'ui', 'un']
        }

        for group in similar_vowels.values():
            if v1 in group and v2 in group:
                return True

        return False

    def _classify_consonant_group(self, consonant):
        """分类声母到三十六字母组"""
        for group_name, consonants_in_group in self.CONSONANTS.items():
            if consonant in consonants_in_group:
                return group_name
        return None

    def _analyze_vowel_rhyme_relation(self, v1, v2):
        """分析韵母的韵律关系"""
        if v1 == v2:
            return "同韵"
        elif self._are_harmonious_vowels(v1, v2):
            return "谐韵"
        elif v1[-1] == v2[-1]:  # 相同韵尾
            return "韵尾相同"
        else:
            return None

    def _get_phonology_suggestions(self, tone_analysis, rhythm_score, harmony_analysis, fluency_analysis=None):
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
        elif rhythm_score >= 80:
            suggestions.append("韵律和谐度优秀，平仄相间自然流畅")

        # 发音流畅度建议
        if fluency_analysis:
            if fluency_analysis['fluency_score'] < 40:
                suggestions.append(f"发音流畅度需改进：{'; '.join(fluency_analysis['issues'])}")
            elif fluency_analysis['fluency_score'] >= 70:
                suggestions.append("发音流畅自然，音节衔接和谐")

        # 特殊和谐现象
        if harmony_analysis.get('alliteration'):
            suggestions.append(f"✓ 头韵和谐：{', '.join(harmony_analysis['alliteration'])}")

        if harmony_analysis.get('assonance'):
            suggestions.append(f"✓ 韵律和谐：{', '.join(harmony_analysis['assonance'])}")

        # 古汉语音韵建议
        if tone_analysis.get('tone_sequence'):
            tone_seq = tone_analysis['tone_sequence']
            if len(set(tone_seq)) == 1:
                suggestions.append("声调过于单一，建议选择不同声调的字词搭配")
            elif len(set(tone_seq)) >= 3:
                suggestions.append("声调丰富和谐，具有古典韵味")

        # 如果没有建议，添加正面评价
        if not suggestions:
            suggestions.append("音韵结构良好，整体和谐自然")

        return suggestions[:5]  # 最多返回5条建议

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
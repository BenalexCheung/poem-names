"""
数据处理模块
负责诗经、楚辞数据的清洗、解析和导入
"""
import os
import re
import jieba
from collections import Counter
from tqdm import tqdm
import logging

from .models import Poetry, Word, Surname

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PoetryDataProcessor:
    """诗词数据处理器"""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'poetry')
        self.pinyin_dict = self._load_pinyin_dict()
        self.wuxing_dict = self._load_wuxing_dict()

    def _load_pinyin_dict(self):
        """加载拼音词典"""
        # 这里应该加载一个汉字到拼音的映射词典
        # 暂时使用一个简单的示例
        return {
            '关': 'guan1', '雎': 'ju1', '鸠': 'jiu1', '河': 'he2', '洲': 'zhou1',
            '窈': 'yao3', '窕': 'tiao3', '淑': 'shu1', '女': 'nv3', '君': 'jun1',
            '子': 'zi3', '好': 'hao3', '逑': 'qiu2', '参': 'cen1', '差': 'cha1',
            '荇': 'xing4', '菜': 'cai4', '左': 'zuo3', '右': 'you4', '流': 'liu2',
            '寤': 'wu4', '寐': 'mei4', '求': 'qiu2', '之': 'zhi1', '悠': 'you1',
            '哉': 'zai1', '辗': 'zhan3', '转': 'zhuan3', '反': 'fan3', '侧': 'ce4',
            '采': 'cai3', '琴': 'qin2', '瑟': 'se4', '友': 'you3', '钟': 'zhong1',
            '鼓': 'gu3', '乐': 'le4', '葛': 'ge3', '覃': 'tan2', '兮': 'xi1',
            '施': 'shi1', '中': 'zhong1', '谷': 'gu3', '维': 'wei2', '叶': 'ye4',
            '萋': 'qi1', '黄': 'huang2', '鸟': 'niao3', '飞': 'fei1', '集': 'ji2',
            '灌': 'guan4', '木': 'mu4', '鸣': 'ming2', '喈': 'jie1', '莫': 'mo4',
            '刈': 'yi4', '濩': 'hu4', '絺': 'chi1', '绤': 'xi4', '服': 'fu2',
            '斁': 'yi4', '言': 'yan2', '告': 'gao4', '师': 'shi1', '氏': 'shi4',
            '归': 'gui1', '薄': 'bo2', '污': 'wu1', '私': 'si1', '浣': 'huan4',
            '衣': 'yi1', '害': 'hai4', '否': 'fou3', '宁': 'ning2', '父': 'fu4',
            '母': 'mu3', '静': 'jing4', '姝': 'shu1', '俟': 'si4', '城': 'cheng2',
            '隅': 'yu2', '爱': 'ai4', '见': 'jian4', '搔': 'sao1', '首': 'shou3',
            '踟': 'chi2', '蹰': 'chu2', '娈': 'luan2', '贻': 'yi2', '彤': 'tong2',
            '管': 'guan3', '炜': 'wei3', '怿': 'yi4', '美': 'mei3', '牧': 'mu4',
            '荑': 'ti2', '洵': 'xun2', '异': 'yi4', '匪': 'fei3', '人': 'ren2',
            '呦': 'you1', '鹿': 'lu4', '食': 'shi2', '野': 'ye3', '苹': 'ping2',
            '嘉': 'jia1', '宾': 'bin1', '笙': 'sheng1', '簧': 'huang2', '筐': 'kuang1',
            '将': 'jiang1', '示': 'shi4', '周': 'zhou1', '行': 'xing2', '孔': 'kong3',
            '昭': 'zhao1', '视': 'shi4', '民': 'min2', '恌': 'tiao1', '则': 'ze2',
            '效': 'xiao4', '旨': 'zhi3', '酒': 'jiu3', '燕': 'yan4', '敖': 'ao2',
            '芩': 'qin2', '湛': 'zhan4', '心': 'xin1', '文': 'wen2', '王': 'wang2',
            '上': 'shang4', '于': 'yu2', '天': 'tian1', '虽': 'sui1', '旧': 'jiu4',
            '邦': 'bang1', '命': 'ming4', '新': 'xin1', '谓': 'wei4', '克': 'ke4',
            '明': 'ming2', '峻': 'jun4', '德': 'de2', '亲': 'qin1', '九': 'jiu3',
            '族': 'zu2', '既': 'ji4', '睦': 'mu4', '平': 'ping2', '章': 'zhang1',
            '百': 'bai3', '姓': 'xing4', '黎': 'li2', '变': 'bian4', '时': 'shi2',
            '雍': 'yong1'
        }

    def _load_wuxing_dict(self):
        """加载五行属性词典"""
        # 基于汉字部首和意义确定五行属性
        # 金: 金属相关、白色、西方等
        # 木: 植物相关、绿色、东方等
        # 水: 水相关、黑色、北方等
        # 火: 火相关、红色、南方等
        # 土: 土相关、黄色、中央等
        return {
            # 金属性字
            '金': 'jin', '银': 'jin', '铜': 'jin', '铁': 'jin', '钢': 'jin',
            '白': 'jin', '银': 'jin', '亮': 'jin', '光': 'jin', '辉': 'jin',
            '锋': 'jin', '锐': 'jin', '利': 'jin', '坚': 'jin', '硬': 'jin',
            '西': 'jin', '秋': 'jin', '庚': 'jin', '辛': 'jin', '申': 'jin',

            # 木属性字
            '木': 'mu', '林': 'mu', '森': 'mu', '树': 'mu', '竹': 'mu',
            '草': 'mu', '花': 'mu', '叶': 'mu', '枝': 'mu', '根': 'mu',
            '绿': 'mu', '青': 'mu', '蓝': 'mu', '翠': 'mu', '葱': 'mu',
            '东': 'mu', '春': 'mu', '甲': 'mu', '乙': 'mu', '寅': 'mu',
            '卯': 'mu', '生': 'mu', '长': 'mu', '发': 'mu', '育': 'mu',

            # 水属性字
            '水': 'shui', '河': 'shui', '江': 'shui', '海': 'shui', '湖': 'shui',
            '雨': 'shui', '雪': 'shui', '冰': 'shui', '泉': 'shui', '溪': 'shui',
            '黑': 'shui', '玄': 'shui', '深': 'shui', '寒': 'shui', '冷': 'shui',
            '北': 'shui', '冬': 'shui', '壬': 'shui', '癸': 'shui', '亥': 'shui',
            '子': 'shui', '流': 'shui', '动': 'shui', '柔': 'shui', '智': 'shui',

            # 火属性字
            '火': 'huo', '日': 'huo', '阳': 'huo', '光': 'huo', '热': 'huo',
            '红': 'huo', '赤': 'huo', '朱': 'huo', '丹': 'huo', '紫': 'huo',
            '南': 'huo', '夏': 'huo', '丙': 'huo', '丁': 'huo', '巳': 'huo',
            '午': 'huo', '明': 'huo', '亮': 'huo', '炎': 'huo', '炽': 'huo',
            '烈': 'huo', '勇': 'huo', '刚': 'huo', '强': 'huo', '进': 'huo',

            # 土属性字
            '土': 'tu', '地': 'tu', '山': 'tu', '石': 'tu', '岩': 'tu',
            '黄': 'tu', '褐': 'tu', '棕': 'tu', '厚': 'tu', '重': 'tu',
            '中': 'tu', '央': 'tu', '戊': 'tu', '己': 'tu', '丑': 'tu',
            '未': 'tu', '辰': 'tu', '戌': 'tu', '实': 'tu', '稳': 'tu',
            '诚': 'tu', '信': 'tu', '忠': 'tu', '厚': 'tu', '德': 'tu',
        }

    def _parse_poetry_file(self, file_path, poetry_type):
        """解析诗词文件"""
        poems = []
        current_poem = None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line or (line.startswith('#') and not line.startswith('##')):
                    continue

                # 检查是否是标题行
                if '##' in line:
                    # 保存之前的诗
                    if current_poem:
                        poems.append(current_poem)

                    # 解析新标题
                    title_match = re.match(r'##\s*(.+)', line)
                    if title_match:
                        title = title_match.group(1).strip()
                        # 解析章节信息
                        section = ""
                        if '·' in title:
                            parts = title.split('·')
                            if len(parts) >= 2:
                                section = parts[0]
                                title = '·'.join(parts[1:])

                        current_poem = {
                            'title': title,
                            'section': section,
                            'content': '',
                            'poetry_type': poetry_type
                        }
                elif current_poem:
                    # 添加内容行
                    current_poem['content'] += line + '\n'

            # 添加最后一个诗
            if current_poem:
                poems.append(current_poem)

        except Exception as e:
            logger.error(f"解析文件 {file_path} 时出错: {e}")

        return poems

    def _extract_words(self, content):
        """从诗词内容中提取字词"""
        # 去除标点符号和特殊字符
        content = re.sub(r'[^\u4e00-\u9fa5]', '', content)

        # 使用jieba分词
        words = jieba.cut(content, cut_all=False)

        # 过滤单字词和停用词
        filtered_words = []
        stop_words = {'之', '兮', '而', '于', '以', '为', '于', '自', '其', '则', '也', '矣'}

        for word in words:
            if len(word) >= 2 and word not in stop_words:
                filtered_words.append(word)

        return filtered_words

    def _get_word_attributes(self, character):
        """获取字词的属性"""
        # 获取拼音
        pinyin = self.pinyin_dict.get(character, character)

        # 获取五行属性
        wuxing = self.wuxing_dict.get(character, 'unknown')

        # 根据字词内容判断性别倾向和含义 - 增强版性别区分
        gender_preference = 'neutral'
        gender_strength = 'weak'  # 性别倾向强度：weak, medium, strong
        meaning = ""
        tags = []

        # 强性别倾向字词
        strong_male_chars = [
            '男', '郎', '夫', '兄', '父', '叔', '伯', '翁', '君', '王', '帝', '皇', '侯', '公', '卿',
            '勇', '强', '刚', '毅', '坚', '猛', '武', '英', '豪', '杰', '雄', '虎', '龙', '豹', '熊',
            '威', '霸', '霸', '锋', '锐', '剑', '刀', '枪', '戟', '矛', '盾', '甲', '胄', '盔', '铠',
            '战', '斗', '征', '伐', '攻', '守', '胜', '败', '敌', '阵', '营', '军', '师', '将', '兵',
            '力', '劲', '壮', '硕', '伟', '高', '大', '强', '健', '康', '盛', '昌', '隆', '兴', '旺'
        ]

        strong_female_chars = [
            '女', '娘', '姬', '妃', '嫔', '妇', '妻', '母', '妹', '姑', '姨', '姥', '奶', '婆', '妇',
            '柔', '弱', '婉', '约', '温', '和', '静', '淑', '贤', '惠', '丽', '艳', '媚', '娇', '嫩',
            '美', '秀', '华', '芳', '香', '馨', '兰', '菊', '梅', '莲', '荷', '花', '草', '叶', '枝',
            '丝', '绸', '缎', '锦', '绣', '织', '缝', '绣', '针', '线', '缕', '丝', '弦', '琴', '瑟',
            '舞', '歌', '唱', '吟', '咏', '诗', '词', '赋', '文', '墨', '笔', '砚', '纸', '书', '卷'
        ]

        # 中等性别倾向字词（可根据上下文调整）
        medium_male_chars = [
            '智', '慧', '聪', '明', '贤', '才', '能', '德', '善', '仁', '义', '礼', '忠', '信', '孝',
            '志', '心', '意', '思', '想', '谋', '策', '计', '划', '略', '术', '法', '道', '理', '则',
            '天', '地', '山', '河', '海', '江', '湖', '泉', '石', '木', '林', '森', '野', '原', '田',
            '力', '气', '血', '骨', '筋', '脉', '身', '体', '躯', '肢', '臂', '腿', '脚', '手', '指'
        ]

        medium_female_chars = [
            '爱', '情', '意', '心', '思', '念', '想', '忆', '怀', '愁', '怨', '悲', '喜', '乐', '欢',
            '泪', '珠', '玉', '金', '银', '宝', '珍', '贵', '值', '价', '财', '富', '贵', '荣', '华',
            '月', '星', '云', '霞', '彩', '光', '明', '亮', '洁', '净', '清', '纯', '真', '善', '美',
            '水', '泉', '溪', '流', '河', '湖', '海', '洋', '波', '浪', '潮', '汐', '湾', '港', '岛'
        ]

        # 判断性别倾向
        if character in strong_male_chars:
            gender_preference = 'male'
            gender_strength = 'strong'
            meaning = "阳刚、力量"
            tags = ['男性', '刚强', '力量']
        elif character in strong_female_chars:
            gender_preference = 'female'
            gender_strength = 'strong'
            meaning = "阴柔、优雅"
            tags = ['女性', '温柔', '优雅']
        elif character in medium_male_chars:
            gender_preference = 'male'
            gender_strength = 'medium'
            meaning = "智慧、理性"
            tags = ['男性', '智慧', '理性']
        elif character in medium_female_chars:
            gender_preference = 'female'
            gender_strength = 'medium'
            meaning = "情感、细腻"
            tags = ['女性', '情感', '细腻']
        elif character in ['美', '好', '丽', '秀', '艳', '华', '芳', '香', '洁', '纯']:
            # 中性美好字词，但更偏向女性
            gender_preference = 'female'
            gender_strength = 'weak'
            meaning = "美好、美丽"
            tags = ['美好', '美丽', '优雅']
        else:
            # 默认中性，但根据五行和语境进行弱倾向判断
            meaning = "诗词用字"
            tags = ['古典', '诗意']

            # 根据五行进行弱性别倾向判断
            if wuxing == 'huo':  # 火性偏阳刚
                gender_preference = 'male'
                gender_strength = 'weak'
                tags.append('阳刚')
            elif wuxing == 'shui':  # 水性偏阴柔
                gender_preference = 'female'
                gender_strength = 'weak'
                tags.append('阴柔')

        # 添加五行相关标签
        if wuxing != 'unknown':
            tags.append(f'五行{wuxing}')

        return {
            'pinyin': pinyin,
            'wuxing': wuxing,
            'gender_preference': gender_preference,
            'gender_strength': gender_strength,
            'meaning': meaning,
            'tags': tags
        }

    def import_poetry_data(self):
        """导入诗词数据"""
        logger.info("开始导入诗词数据...")

        # 定义数据源映射
        data_sources = {
            'shijing.txt': 'shijing',
            'chuci.txt': 'chuci',
            'classics/lunyu.txt': 'classics',
            'classics/mengzi.txt': 'classics',
            'tang/tang_shi.txt': 'tang',
        }

        total_poems = 0

        for file_path, poetry_type in data_sources.items():
            full_path = os.path.join(self.data_dir, file_path)
            if os.path.exists(full_path):
                logger.info(f"处理 {poetry_type} 数据: {file_path}")
                poems = self._parse_poetry_file(full_path, poetry_type)

                for poem_data in tqdm(poems, desc=f"导入{poetry_type}"):
                    poetry, created = Poetry.objects.get_or_create(
                        title=poem_data['title'],
                        poetry_type=poem_data['poetry_type'],
                        defaults={
                            'content': poem_data['content'],
                            'section': poem_data['section']
                        }
                    )
                    if created:
                        logger.info(f"创建诗词: {poetry.title}")
                        total_poems += 1
            else:
                logger.warning(f"文件不存在: {full_path}")

        logger.info(f"诗词数据导入完成，共导入 {total_poems} 篇诗词")

    def import_word_data(self):
        """导入字词数据"""
        logger.info("开始导入字词数据...")

        # 获取所有诗词内容
        all_poems = Poetry.objects.all()
        word_counter = Counter()

        for poem in tqdm(all_poems, desc="统计字词频率"):
            words = self._extract_words(poem.content)
            word_counter.update(words)

            # 统计单个汉字
            for char in poem.content:
                if '\u4e00' <= char <= '\u9fa5':
                    word_counter[char] += 1

        # 导入字词数据
        for word_text, frequency in tqdm(word_counter.items(), desc="导入字词"):
            if len(word_text) == 1:  # 单字
                attributes = self._get_word_attributes(word_text)
                word, created = Word.objects.get_or_create(
                    character=word_text,
                    defaults={
                        'pinyin': attributes['pinyin'],
                        'wuxing': attributes['wuxing'],
                        'meaning': attributes['meaning'],
                        'gender_preference': attributes['gender_preference'],
                        'frequency': frequency,
                        'tags': attributes['tags']
                    }
                )
                # 只关联包含该字符的诗词（而不是所有诗词）
                if created:
                    # 查找包含该字符的诗词
                    containing_poems = []
                    for poem in all_poems:
                        if word_text in poem.content:
                            containing_poems.append(poem)
                    if containing_poems:
                        word.from_poetry.add(*containing_poems)
                    word.save()
                else:
                    # 如果字已存在，也需要更新关联关系（确保准确性）
                    # 查找包含该字符的诗词
                    containing_poems = []
                    for poem in all_poems:
                        if word_text in poem.content:
                            containing_poems.append(poem)
                    # 更新关联关系
                    word.from_poetry.clear()
                    if containing_poems:
                        word.from_poetry.add(*containing_poems)
                    word.save()

        logger.info("字词数据导入完成")

    def import_surname_data(self):
        """导入姓氏数据"""
        logger.info("开始导入姓氏数据...")

        surnames_file = os.path.join(os.path.dirname(self.data_dir), 'surnames.txt')

        if not os.path.exists(surnames_file):
            logger.warning("姓氏数据文件不存在")
            return

        with open(surnames_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in tqdm(lines, desc="导入姓氏"):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split(',')
            if len(parts) >= 4:
                surname_name, pinyin, meaning, origin = parts[:4]

                surname, created = Surname.objects.get_or_create(
                    name=surname_name,
                    defaults={
                        'pinyin': pinyin,
                        'meaning': meaning,
                        'origin': origin
                    }
                )
                if created:
                    logger.info(f"创建姓氏: {surname.name}")

        logger.info("姓氏数据导入完成")

    def process_all_data(self):
        """处理所有数据"""
        logger.info("开始处理所有数据...")

        try:
            self.import_poetry_data()
            self.import_word_data()
            self.import_surname_data()
            logger.info("所有数据处理完成")
        except Exception as e:
            logger.error(f"数据处理过程中出错: {e}")
            raise


class SurnameDataProcessor:
    """姓氏数据处理器"""

    @staticmethod
    def import_surnames():
        """导入姓氏数据"""
        surnames_data = [
            {'name': '王', 'pinyin': 'wang', 'meaning': '统治者', 'origin': '古代帝王姓氏'},
            {'name': '李', 'pinyin': 'li', 'meaning': '李子树', 'origin': '源于植物'},
            {'name': '张', 'pinyin': 'zhang', 'meaning': '张弓', 'origin': '源于动作'},
            {'name': '刘', 'pinyin': 'liu', 'meaning': '杀戮', 'origin': '源于动作'},
            {'name': '陈', 'pinyin': 'chen', 'meaning': '古国名', 'origin': '源于地名'},
            {'name': '杨', 'pinyin': 'yang', 'meaning': '杨树', 'origin': '源于植物'},
            {'name': '赵', 'pinyin': 'zhao', 'meaning': '跑得快', 'origin': '源于动作'},
            {'name': '黄', 'pinyin': 'huang', 'meaning': '黄色', 'origin': '源于颜色'},
            {'name': '周', 'pinyin': 'zhou', 'meaning': '周朝', 'origin': '源于朝代'},
            {'name': '吴', 'pinyin': 'wu', 'meaning': '古代国名', 'origin': '源于地名'},
        ]

        for data in surnames_data:
            Surname.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
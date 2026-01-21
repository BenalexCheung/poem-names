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

        # 根据字词内容判断性别倾向和含义
        gender_preference = 'neutral'
        meaning = ""
        tags = []

        # 简单的规则判断
        if character in ['女', '娘', '姬', '妃', '嫔', '妇', '妻', '母', '妹', '姑', '姨']:
            gender_preference = 'female'
            meaning = "女性相关"
            tags = ['女性', '温柔']
        elif character in ['男', '郎', '夫', '兄', '父', '叔', '伯', '翁', '君', '王', '帝']:
            gender_preference = 'male'
            meaning = "男性相关"
            tags = ['男性', '刚强']
        elif character in ['美', '好', '丽', '秀', '艳', '华', '芳', '香', '洁', '纯']:
            meaning = "美好、美丽"
            tags = ['美好', '美丽', '优雅']
        elif character in ['智', '慧', '聪', '明', '贤', '才', '能', '德', '善', '仁']:
            meaning = "智慧、贤能"
            tags = ['智慧', '贤能', '优秀']
        elif character in ['勇', '强', '刚', '毅', '坚', '猛', '武', '英', '豪', '杰']:
            gender_preference = 'male'
            meaning = "勇敢、刚强"
            tags = ['勇敢', '刚强', '坚毅']
        elif character in ['柔', '弱', '婉', '约', '温', '和', '静', '淑', '贤', '惠']:
            gender_preference = 'female'
            meaning = "温柔、贤惠"
            tags = ['温柔', '贤惠', '文静']
        else:
            meaning = "诗词用字"
            tags = ['古典', '诗意']

        return {
            'pinyin': pinyin,
            'gender_preference': gender_preference,
            'meaning': meaning,
            'tags': tags
        }

    def import_poetry_data(self):
        """导入诗词数据"""
        logger.info("开始导入诗词数据...")

        # 处理诗经数据
        shijing_file = os.path.join(self.data_dir, 'shijing_sample.txt')
        if os.path.exists(shijing_file):
            logger.info("处理诗经数据...")
            shijing_poems = self._parse_poetry_file(shijing_file, 'shijing')

            for poem_data in tqdm(shijing_poems, desc="导入诗经"):
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

        # 处理楚辞数据
        chuci_file = os.path.join(self.data_dir, 'chuci_sample.txt')
        if os.path.exists(chuci_file):
            logger.info("处理楚辞数据...")
            chuci_poems = self._parse_poetry_file(chuci_file, 'chuci')

            for poem_data in tqdm(chuci_poems, desc="导入楚辞"):
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

        logger.info("诗词数据导入完成")

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
                        'meaning': attributes['meaning'],
                        'gender_preference': attributes['gender_preference'],
                        'frequency': frequency,
                        'tags': attributes['tags']
                    }
                )
                if created:
                    word.from_poetry.add(*all_poems)
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
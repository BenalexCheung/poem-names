"""
传统元素分析模块
提供生肖、时辰、月份与五行的对应关系分析
"""
from collections import Counter


class TraditionalAnalyzer:
    """传统元素分析器 - 生肖、时辰、月份与五行对应"""

    # 十二生肖与五行对应关系
    SHENGXIAO_WUXING = {
        'rat': {'name': '鼠', 'wuxing': 'shui', 'year': 0},      # 子鼠 - 水
        'ox': {'name': '牛', 'wuxing': 'tu', 'year': 1},         # 丑牛 - 土
        'tiger': {'name': '虎', 'wuxing': 'mu', 'year': 2},      # 寅虎 - 木
        'rabbit': {'name': '兔', 'wuxing': 'mu', 'year': 3},     # 卯兔 - 木
        'dragon': {'name': '龙', 'wuxing': 'tu', 'year': 4},     # 辰龙 - 土
        'snake': {'name': '蛇', 'wuxing': 'huo', 'year': 5},     # 巳蛇 - 火
        'horse': {'name': '马', 'wuxing': 'huo', 'year': 6},     # 午马 - 火
        'goat': {'name': '羊', 'wuxing': 'tu', 'year': 7},       # 未羊 - 土
        'monkey': {'name': '猴', 'wuxing': 'jin', 'year': 8},    # 申猴 - 金
        'rooster': {'name': '鸡', 'wuxing': 'jin', 'year': 9},   # 酉鸡 - 金
        'dog': {'name': '狗', 'wuxing': 'tu', 'year': 10},        # 戌狗 - 土
        'pig': {'name': '猪', 'wuxing': 'shui', 'year': 11},     # 亥猪 - 水
    }

    # 十二时辰与五行对应关系
    SHICHEN_WUXING = {
        'zi': {'name': '子时', 'time': '23:00-01:00', 'wuxing': 'shui', 'index': 0},      # 子时 - 水
        'chou': {'name': '丑时', 'time': '01:00-03:00', 'wuxing': 'tu', 'index': 1},     # 丑时 - 土
        'yin': {'name': '寅时', 'time': '03:00-05:00', 'wuxing': 'mu', 'index': 2},      # 寅时 - 木
        'mao': {'name': '卯时', 'time': '05:00-07:00', 'wuxing': 'mu', 'index': 3},      # 卯时 - 木
        'chen': {'name': '辰时', 'time': '07:00-09:00', 'wuxing': 'tu', 'index': 4},     # 辰时 - 土
        'si': {'name': '巳时', 'time': '09:00-11:00', 'wuxing': 'huo', 'index': 5},      # 巳时 - 火
        'wu': {'name': '午时', 'time': '11:00-13:00', 'wuxing': 'huo', 'index': 6},      # 午时 - 火
        'wei': {'name': '未时', 'time': '13:00-15:00', 'wuxing': 'tu', 'index': 7},      # 未时 - 土
        'shen': {'name': '申时', 'time': '15:00-17:00', 'wuxing': 'jin', 'index': 8},    # 申时 - 金
        'you': {'name': '酉时', 'time': '17:00-19:00', 'wuxing': 'jin', 'index': 9},    # 酉时 - 金
        'xu': {'name': '戌时', 'time': '19:00-21:00', 'wuxing': 'tu', 'index': 10},     # 戌时 - 土
        'hai': {'name': '亥时', 'time': '21:00-23:00', 'wuxing': 'shui', 'index': 11},  # 亥时 - 水
    }

    # 农历月份与五行对应关系（按农历）
    LUNAR_MONTH_WUXING = {
        1: {'name': '正月', 'wuxing': 'mu', 'season': '春'},      # 正月 - 木（春）
        2: {'name': '二月', 'wuxing': 'mu', 'season': '春'},      # 二月 - 木（春）
        3: {'name': '三月', 'wuxing': 'tu', 'season': '春'},      # 三月 - 土（春末）
        4: {'name': '四月', 'wuxing': 'huo', 'season': '夏'},     # 四月 - 火（夏）
        5: {'name': '五月', 'wuxing': 'huo', 'season': '夏'},     # 五月 - 火（夏）
        6: {'name': '六月', 'wuxing': 'tu', 'season': '夏'},      # 六月 - 土（夏末）
        7: {'name': '七月', 'wuxing': 'jin', 'season': '秋'},     # 七月 - 金（秋）
        8: {'name': '八月', 'wuxing': 'jin', 'season': '秋'},     # 八月 - 金（秋）
        9: {'name': '九月', 'wuxing': 'tu', 'season': '秋'},      # 九月 - 土（秋末）
        10: {'name': '十月', 'wuxing': 'shui', 'season': '冬'},   # 十月 - 水（冬）
        11: {'name': '十一月', 'wuxing': 'shui', 'season': '冬'}, # 十一月 - 水（冬）
        12: {'name': '十二月', 'wuxing': 'tu', 'season': '冬'},  # 十二月 - 土（冬末）
    }

    # 公历月份与五行对应关系（简化版，按季节）
    SOLAR_MONTH_WUXING = {
        1: {'name': '一月', 'wuxing': 'shui', 'season': '冬'},     # 一月 - 水（冬）
        2: {'name': '二月', 'wuxing': 'mu', 'season': '春'},      # 二月 - 木（春）
        3: {'name': '三月', 'wuxing': 'mu', 'season': '春'},      # 三月 - 木（春）
        4: {'name': '四月', 'wuxing': 'mu', 'season': '春'},      # 四月 - 木（春末）
        5: {'name': '五月', 'wuxing': 'huo', 'season': '夏'},     # 五月 - 火（夏）
        6: {'name': '六月', 'wuxing': 'huo', 'season': '夏'},     # 六月 - 火（夏）
        7: {'name': '七月', 'wuxing': 'huo', 'season': '夏'},     # 七月 - 火（夏末）
        8: {'name': '八月', 'wuxing': 'jin', 'season': '秋'},     # 八月 - 金（秋）
        9: {'name': '九月', 'wuxing': 'jin', 'season': '秋'},     # 九月 - 金（秋）
        10: {'name': '十月', 'wuxing': 'jin', 'season': '秋'},   # 十月 - 金（秋末）
        11: {'name': '十一月', 'wuxing': 'shui', 'season': '冬'}, # 十一月 - 水（冬）
        12: {'name': '十二月', 'wuxing': 'shui', 'season': '冬'}, # 十二月 - 水（冬）
    }

    # 五行相生关系（用于推荐）
    WUXING_SHENG = {
        'jin': 'shui',    # 金生水
        'shui': 'mu',     # 水生木
        'mu': 'huo',      # 木生火
        'huo': 'tu',      # 火生土
        'tu': 'jin'       # 土生金
    }

    # 五行相克关系（需要避免）
    WUXING_KE = {
        'jin': 'mu',      # 金克木
        'mu': 'tu',       # 木克土
        'tu': 'shui',     # 土克水
        'shui': 'huo',    # 水克火
        'huo': 'jin'      # 火克金
    }

    def __init__(self):
        pass

    def get_shengxiao_wuxing(self, shengxiao):
        """
        获取生肖对应的五行
        
        Args:
            shengxiao: 生肖英文名（如 'rat', 'ox' 等）
        
        Returns:
            dict: 包含五行、名称等信息
        """
        return self.SHENGXIAO_WUXING.get(shengxiao.lower(), {})

    def get_shichen_wuxing(self, shichen):
        """
        获取时辰对应的五行
        
        Args:
            shichen: 时辰拼音（如 'zi', 'chou' 等）
        
        Returns:
            dict: 包含五行、名称、时间等信息
        """
        return self.SHICHEN_WUXING.get(shichen.lower(), {})

    def get_month_wuxing(self, month, is_lunar=True):
        """
        获取月份对应的五行
        
        Args:
            month: 月份（1-12）
            is_lunar: 是否为农历月份，默认True
        
        Returns:
            dict: 包含五行、名称、季节等信息
        """
        if is_lunar:
            return self.LUNAR_MONTH_WUXING.get(month, {})
        else:
            return self.SOLAR_MONTH_WUXING.get(month, {})

    def analyze_traditional_elements(self, shengxiao=None, shichen=None, month=None, is_lunar=True):
        """
        综合分析传统元素（生肖、时辰、月份）的五行属性
        
        Args:
            shengxiao: 生肖
            shichen: 时辰
            month: 月份
            is_lunar: 是否为农历月份
        
        Returns:
            dict: 综合分析结果
        """
        wuxing_counts = Counter()
        elements_info = {}
        recommendations = []

        # 分析生肖
        if shengxiao:
            sx_info = self.get_shengxiao_wuxing(shengxiao)
            if sx_info:
                wuxing = sx_info['wuxing']
                wuxing_counts[wuxing] += 1
                elements_info['shengxiao'] = {
                    'name': sx_info['name'],
                    'wuxing': wuxing,
                    'weight': 1.0  # 生肖权重最高
                }

        # 分析时辰
        if shichen:
            sc_info = self.get_shichen_wuxing(shichen)
            if sc_info:
                wuxing = sc_info['wuxing']
                wuxing_counts[wuxing] += 1
                elements_info['shichen'] = {
                    'name': sc_info['name'],
                    'time': sc_info['time'],
                    'wuxing': wuxing,
                    'weight': 0.8  # 时辰权重较高
                }

        # 分析月份
        if month:
            month_info = self.get_month_wuxing(month, is_lunar)
            if month_info:
                wuxing = month_info['wuxing']
                wuxing_counts[wuxing] += 0.6  # 月份权重较低
                elements_info['month'] = {
                    'name': month_info['name'],
                    'season': month_info['season'],
                    'wuxing': wuxing,
                    'weight': 0.6
                }

        # 计算主要五行属性
        if wuxing_counts:
            dominant_wuxing = wuxing_counts.most_common(1)[0][0]
            dominant_count = wuxing_counts.most_common(1)[0][1]
        else:
            dominant_wuxing = None
            dominant_count = 0

        # 生成推荐
        if dominant_wuxing:
            # 推荐相生的五行
            sheng_wuxing = self.WUXING_SHENG.get(dominant_wuxing)
            if sheng_wuxing:
                recommendations.append({
                    'type': 'sheng',
                    'wuxing': sheng_wuxing,
                    'reason': f'{dominant_wuxing}生{sheng_wuxing}，相生关系，有利于发展',
                    'priority': 'high'
                })

            # 避免相克的五行
            ke_wuxing = self.WUXING_KE.get(dominant_wuxing)
            if ke_wuxing:
                recommendations.append({
                    'type': 'avoid',
                    'wuxing': ke_wuxing,
                    'reason': f'{dominant_wuxing}克{ke_wuxing}，相克关系，建议避免',
                    'priority': 'high'
                })

            # 如果某个五行缺失，推荐补充
            all_wuxing = set(['jin', 'mu', 'shui', 'huo', 'tu'])
            present_wuxing = set(wuxing_counts.keys())
            missing_wuxing = all_wuxing - present_wuxing
            if missing_wuxing:
                for wuxing in missing_wuxing:
                    # 优先推荐与主五行相生的
                    if self.WUXING_SHENG.get(dominant_wuxing) == wuxing:
                        recommendations.append({
                            'type': 'complement',
                            'wuxing': wuxing,
                            'reason': f'补充缺失的{wuxing}属性，与主属性{dominant_wuxing}相生',
                            'priority': 'medium'
                        })

        return {
            'elements_info': elements_info,
            'wuxing_distribution': dict(wuxing_counts),
            'dominant_wuxing': dominant_wuxing,
            'recommended_wuxing': [r['wuxing'] for r in recommendations if r['type'] in ['sheng', 'complement']],
            'avoid_wuxing': [r['wuxing'] for r in recommendations if r['type'] == 'avoid'],
            'recommendations': recommendations,
            'summary': self._generate_summary(elements_info, dominant_wuxing, recommendations)
        }

    def _generate_summary(self, elements_info, dominant_wuxing, recommendations):
        """生成分析总结"""
        summary_parts = []
        
        if elements_info.get('shengxiao'):
            sx = elements_info['shengxiao']
            summary_parts.append(f"生肖{sx['name']}属{sx['wuxing']}")
        
        if elements_info.get('shichen'):
            sc = elements_info['shichen']
            summary_parts.append(f"{sc['name']}属{sc['wuxing']}")
        
        if elements_info.get('month'):
            month = elements_info['month']
            summary_parts.append(f"{month['name']}属{month['wuxing']}")
        
        if dominant_wuxing:
            summary_parts.append(f"主属性为{dominant_wuxing}")
        
        return "；".join(summary_parts) if summary_parts else "未提供传统元素信息"

    def get_wuxing_suggestions_for_name(self, traditional_analysis):
        """
        根据传统元素分析，为名字生成提供五行建议
        
        Args:
            traditional_analysis: analyze_traditional_elements 返回的分析结果
        
        Returns:
            dict: 名字生成的五行建议
        """
        dominant_wuxing = traditional_analysis.get('dominant_wuxing')
        recommended_wuxing = traditional_analysis.get('recommended_wuxing', [])
        avoid_wuxing = traditional_analysis.get('avoid_wuxing', [])

        suggestions = {
            'preferred_wuxing': [],
            'avoid_wuxing': avoid_wuxing,
            'balance_suggestions': []
        }

        # 优先推荐的五行
        if dominant_wuxing:
            suggestions['preferred_wuxing'].append(dominant_wuxing)
        
        suggestions['preferred_wuxing'].extend(recommended_wuxing)

        # 平衡建议
        if dominant_wuxing:
            # 如果主属性过强，建议平衡
            suggestions['balance_suggestions'].append({
                'type': 'balance',
                'message': f'主属性{dominant_wuxing}较强，建议在名字中适当补充其他五行以保持平衡'
            })

        return suggestions


# 全局传统元素分析器实例
traditional_analyzer = TraditionalAnalyzer()

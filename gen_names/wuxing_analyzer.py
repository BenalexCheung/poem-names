"""
五行八卦分析模块
提供五行平衡度计算和八卦方位建议
"""
import math
from collections import Counter
from .models import Word


class WuxingAnalyzer:
    """五行八卦分析器"""

    # 五行相生关系：金生水，水生木，木生火，火生土，土生金
    WUXING_SHENG = {
        'jin': 'shui',    # 金生水
        'shui': 'mu',     # 水生木
        'mu': 'huo',      # 木生火
        'huo': 'tu',      # 火生土
        'tu': 'jin'       # 土生金
    }

    # 五行相克关系：金克木，木克土，土克水，水克火，火克金
    WUXING_KE = {
        'jin': 'mu',      # 金克木
        'mu': 'tu',       # 木克土
        'tu': 'shui',     # 土克水
        'shui': 'huo',    # 水克火
        'huo': 'jin'      # 火克金
    }

    # 八卦方位对应
    BAGUA_FANGWEI = {
        'qian': {'name': '乾', 'direction': '西北', 'wuxing': 'jin', 'meaning': '天、父、首领'},
        'kun': {'name': '坤', 'direction': '西南', 'wuxing': 'tu', 'meaning': '地、母、包容'},
        'zhen': {'name': '震', 'direction': '东', 'wuxing': 'mu', 'meaning': '雷、长男、行动'},
        'xun': {'name': '巽', 'direction': '东南', 'wuxing': 'mu', 'meaning': '风、长女、渗透'},
        'li': {'name': '离', 'direction': '南', 'wuxing': 'huo', 'meaning': '火、中女、光明'},
        'kan': {'name': '坎', 'direction': '北', 'wuxing': 'shui', 'meaning': '水、中男、险恶'},
        'gen': {'name': '艮', 'direction': '东北', 'wuxing': 'tu', 'meaning': '山、少男、停止'},
        'dui': {'name': '兑', 'direction': '西', 'wuxing': 'jin', 'meaning': '泽、少女、喜悦'}
    }

    def __init__(self):
        self.word_cache = {}
        self._load_word_cache()

    def _load_word_cache(self):
        """加载字词缓存"""
        try:
            words = Word.objects.all()
            for word in words:
                self.word_cache[word.character] = {
                    'wuxing': word.wuxing,
                    'pinyin': word.pinyin,
                    'meaning': word.meaning
                }
        except Exception as e:
            print(f"加载字词缓存失败: {e}")
            self.word_cache = {}

    def analyze_name_wuxing(self, name_chars):
        """
        分析名字的五行属性

        Args:
            name_chars: 名字字符列表

        Returns:
            dict: 五行分析结果
        """
        wuxing_counts = Counter()
        wuxing_chars = {}

        # 统计每个字的五行属性
        for char in name_chars:
            wuxing = self.word_cache.get(char, {}).get('wuxing', 'unknown')
            if wuxing != 'unknown':
                wuxing_counts[wuxing] += 1
                if wuxing not in wuxing_chars:
                    wuxing_chars[wuxing] = []
                wuxing_chars[wuxing].append(char)

        total_chars = len(name_chars)
        wuxing_percentages = {}

        # 计算五行占比
        for wuxing in ['jin', 'mu', 'shui', 'huo', 'tu']:
            count = wuxing_counts.get(wuxing, 0)
            percentage = (count / total_chars) * 100 if total_chars > 0 else 0
            wuxing_percentages[wuxing] = round(percentage, 1)

        # 计算五行平衡度
        balance_score = self._calculate_balance_score(wuxing_counts, total_chars)

        # 分析五行相生相克关系
        wuxing_relationships = self._analyze_relationships(wuxing_counts)

        return {
            'wuxing_counts': dict(wuxing_counts),
            'wuxing_percentages': wuxing_percentages,
            'wuxing_chars': wuxing_chars,
            'balance_score': balance_score,
            'balance_level': self._get_balance_level(balance_score),
            'relationships': wuxing_relationships,
            'recommendations': self._get_recommendations(wuxing_counts, total_chars)
        }

    def _calculate_balance_score(self, wuxing_counts, total_chars):
        """
        计算五行平衡度分数 (0-100)

        使用更智能的平衡度算法：
        1. 完整性评分：拥有五行属性的数量
        2. 均衡性评分：各五行分布的标准差
        3. 和谐性评分：五行相生关系的完善度
        """
        if total_chars == 0:
            return 0

        # 1. 完整性评分 (0-40分)
        present_wuxing = sum(1 for count in wuxing_counts.values() if count > 0)
        completeness_score = (present_wuxing / 5) * 40

        # 2. 均衡性评分 (0-40分)
        percentages = []
        for wuxing in ['jin', 'mu', 'shui', 'huo', 'tu']:
            count = wuxing_counts.get(wuxing, 0)
            percentage = count / total_chars if total_chars > 0 else 0
            percentages.append(percentage)

        if len(percentages) > 1:
            mean = sum(percentages) / len(percentages)
            variance = sum((p - mean) ** 2 for p in percentages) / len(percentages)
            std_dev = math.sqrt(variance)
            # 标准差越小，均衡性越好
            balance_score = max(0, 40 - (std_dev * 100))
        else:
            balance_score = 20  # 只有一个五行时的中等评分

        # 3. 和谐性评分 (0-20分)
        harmony_score = self._calculate_wuxing_harmony_score(wuxing_counts)

        total_score = completeness_score + balance_score + harmony_score
        return round(min(100, total_score), 1)

    def _calculate_wuxing_harmony_score(self, wuxing_counts):
        """计算五行和谐度评分"""
        harmony_score = 0

        # 检查五行相生关系的存在
        wuxing_present = {w for w, c in wuxing_counts.items() if c > 0}

        # 奖励相生关系的完整性
        sheng_chains = 0
        for wuxing in wuxing_present:
            target = self.WUXING_SHENG.get(wuxing)
            if target and target in wuxing_present:
                sheng_chains += 1

        # 每个相生链条加2分
        harmony_score += sheng_chains * 2

        # 奖励五行多样性
        diversity_bonus = len(wuxing_present) - 1  # 从0开始，每多一个五行加1分
        harmony_score += diversity_bonus

        # 检查是否有明显的五行冲突（相克关系过多）
        ke_conflicts = 0
        for wuxing in wuxing_present:
            target = self.WUXING_KE.get(wuxing)
            if target and target in wuxing_present:
                ke_conflicts += 1

        # 相克关系过多会扣分
        conflict_penalty = max(0, ke_conflicts - 2) * 1  # 超过2对相克关系开始扣分
        harmony_score -= conflict_penalty

        return max(0, min(20, harmony_score))

    def _get_balance_level(self, balance_score):
        """根据平衡度分数获取等级"""
        if balance_score >= 80:
            return {'level': '优秀', 'color': 'green', 'description': '五行非常均衡，有利于各方面发展'}
        elif balance_score >= 60:
            return {'level': '良好', 'color': 'blue', 'description': '五行较为均衡，整体发展较好'}
        elif balance_score >= 40:
            return {'level': '一般', 'color': 'orange', 'description': '五行分布不够均衡，某些方面可能需要加强'}
        else:
            return {'level': '不佳', 'color': 'red', 'description': '五行严重失衡，可能影响各方面发展'}

    def _analyze_relationships(self, wuxing_counts):
        """分析五行相生相克关系"""
        relationships = {
            'sheng': [],  # 相生关系
            'ke': [],     # 相克关系
            'conflicts': []  # 冲突关系
        }

        # 检查相生关系
        for wuxing, target in self.WUXING_SHENG.items():
            if wuxing_counts.get(wuxing, 0) > 0 and wuxing_counts.get(target, 0) > 0:
                relationships['sheng'].append(f'{wuxing}生{target}')

        # 检查相克关系
        for wuxing, target in self.WUXING_KE.items():
            if wuxing_counts.get(wuxing, 0) > 0 and wuxing_counts.get(target, 0) > 0:
                relationships['ke'].append(f'{wuxing}克{target}')

        return relationships

    def _get_recommendations(self, wuxing_counts, total_chars):
        """根据五行分布提供建议"""
        recommendations = []

        # 找出缺失的五行
        missing_wuxing = []
        for wuxing in ['jin', 'mu', 'shui', 'huo', 'tu']:
            if wuxing_counts.get(wuxing, 0) == 0:
                missing_wuxing.append(wuxing)

        if missing_wuxing:
            recommendations.append(f"建议补充以下五行属性: {', '.join(missing_wuxing)}")

        # 检查过度集中的五行
        max_count = max(wuxing_counts.values()) if wuxing_counts else 0
        if max_count > total_chars * 0.4:  # 超过40%
            dominant_wuxing = [w for w, c in wuxing_counts.items() if c == max_count][0]
            recommendations.append(f"当前{dominant_wuxing}属性过于集中，建议平衡其他五行")

        return recommendations

    def get_bagua_suggestions(self, name_wuxing_analysis):
        """
        根据五行分析提供智能八卦方位建议

        Args:
            name_wuxing_analysis: 五行分析结果

        Returns:
            dict: 八卦方位建议
        """
        suggestions = []
        wuxing_counts = name_wuxing_analysis['wuxing_counts']

        # 1. 优先推荐缺失五行的八卦方位
        missing_wuxing = []
        for wuxing in ['jin', 'mu', 'shui', 'huo', 'tu']:
            if wuxing_counts.get(wuxing, 0) == 0:
                missing_wuxing.append(wuxing)

        # 为缺失的五行提供建议
        for wuxing in missing_wuxing[:2]:  # 最多处理前2个缺失的五行
            best_bagua = self._find_best_bagua_for_wuxing(wuxing, wuxing_counts)
            if best_bagua:
                suggestions.append({
                    'bagua': best_bagua['name'],
                    'direction': best_bagua['direction'],
                    'wuxing': wuxing,
                    'meaning': best_bagua['meaning'],
                    'reason': f'补充缺失的{wuxing}属性，增强整体平衡',
                    'priority': 'high'
                })

        # 2. 如果没有缺失的五行，推荐强化优势五行的方位
        if not missing_wuxing:
            strong_wuxing = self._get_strongest_wuxing(wuxing_counts)
            if strong_wuxing:
                best_bagua = self._find_best_bagua_for_wuxing(strong_wuxing, wuxing_counts)
                if best_bagua:
                    suggestions.append({
                        'bagua': best_bagua['name'],
                        'direction': best_bagua['direction'],
                        'wuxing': strong_wuxing,
                        'meaning': best_bagua['meaning'],
                        'reason': f'强化优势{strong_wuxing}属性，提升整体运势',
                        'priority': 'medium'
                    })

        # 3. 提供通用吉利方位
        lucky_directions = self._get_lucky_directions(wuxing_counts)
        avoid_directions = self._get_avoid_directions(wuxing_counts)

        return {
            'suggestions': suggestions[:3],  # 最多推荐3个
            'lucky_directions': lucky_directions,
            'avoid_directions': avoid_directions,
            'analysis': self._get_bagua_analysis(wuxing_counts)
        }

    def _find_best_bagua_for_wuxing(self, target_wuxing, wuxing_counts):
        """为指定五行找到最佳的八卦方位"""
        candidates = []

        for bagua_key, bagua_info in self.BAGUA_FANGWEI.items():
            if bagua_info['wuxing'] == target_wuxing:
                # 计算这个方位的推荐度
                score = self._calculate_bagua_score(bagua_info, wuxing_counts)
                candidates.append((bagua_info, score))

        if candidates:
            # 选择得分最高的八卦
            best_bagua, _ = max(candidates, key=lambda x: x[1])
            return best_bagua

        return None

    def _calculate_bagua_score(self, bagua_info, wuxing_counts):
        """计算八卦方位的推荐分数"""
        score = 10  # 基础分数

        bagua_wuxing = bagua_info['wuxing']

        # 如果这个五行在名字中缺失，加分
        if wuxing_counts.get(bagua_wuxing, 0) == 0:
            score += 20

        # 如果这个五行在名字中较少，加分
        total_chars = sum(wuxing_counts.values())
        if total_chars > 0:
            percentage = wuxing_counts.get(bagua_wuxing, 0) / total_chars
            if percentage < 0.2:  # 少于20%
                score += 15

        return score

    def _get_strongest_wuxing(self, wuxing_counts):
        """获取最强的五行属性"""
        if not wuxing_counts:
            return None

        max_count = max(wuxing_counts.values())
        strong_wuxing = [w for w, c in wuxing_counts.items() if c == max_count]

        return strong_wuxing[0] if strong_wuxing else None

    def _get_bagua_analysis(self, wuxing_counts):
        """提供八卦分析总结"""
        present_wuxing = {w for w, c in wuxing_counts.items() if c > 0}
        missing_wuxing = {'jin', 'mu', 'shui', 'huo', 'tu'} - present_wuxing

        analysis = {
            'present_wuxing_count': len(present_wuxing),
            'missing_wuxing_count': len(missing_wuxing),
            'strongest_wuxing': self._get_strongest_wuxing(wuxing_counts),
            'balance_status': 'excellent' if len(present_wuxing) >= 4 else 'good' if len(present_wuxing) >= 3 else 'needs_improvement'
        }

        return analysis

    def _get_lucky_directions(self, wuxing_counts):
        """获取吉利方位"""
        lucky_directions = []
        strong_wuxing = [w for w, c in wuxing_counts.items() if c > 0]

        for wuxing in strong_wuxing:
            for bagua_key, bagua_info in self.BAGUA_FANGWEI.items():
                if bagua_info['wuxing'] == wuxing:
                    lucky_directions.append({
                        'direction': bagua_info['direction'],
                        'bagua': bagua_info['name'],
                        'reason': f'强化{wuxing}属性'
                    })

        return lucky_directions[:2]  # 最多返回2个

    def _get_avoid_directions(self, wuxing_counts):
        """获取需要回避的方位"""
        avoid_directions = []
        weak_wuxing = [w for w in ['jin', 'mu', 'shui', 'huo', 'tu']
                       if wuxing_counts.get(w, 0) == 0]

        for wuxing in weak_wuxing:
            for bagua_key, bagua_info in self.BAGUA_FANGWEI.items():
                if bagua_info['wuxing'] == wuxing:
                    avoid_directions.append({
                        'direction': bagua_info['direction'],
                        'bagua': bagua_info['name'],
                        'reason': f'避免强化缺失的{wuxing}属性'
                    })

        return avoid_directions[:2]  # 最多返回2个

    def get_name_score(self, name_wuxing_analysis):
        """
        根据五行分析计算名字总评分

        Args:
            name_wuxing_analysis: 五行分析结果

        Returns:
            dict: 评分结果
        """
        balance_score = name_wuxing_analysis['balance_score']

        # 五行平衡度占60%
        # 五行完整度占40%
        wuxing_counts = name_wuxing_analysis['wuxing_counts']
        complete_wuxing = sum(1 for c in wuxing_counts.values() if c > 0)
        completeness_score = (complete_wuxing / 5) * 100

        total_score = (balance_score * 0.6) + (completeness_score * 0.4)
        total_score = round(total_score, 1)

        # 获取评分等级
        if total_score >= 80:
            level = {'grade': 'A', 'description': '优秀', 'color': 'green'}
        elif total_score >= 70:
            level = {'grade': 'B', 'description': '良好', 'color': 'blue'}
        elif total_score >= 60:
            level = {'grade': 'C', 'description': '一般', 'color': 'orange'}
        else:
            level = {'grade': 'D', 'description': '不佳', 'color': 'red'}

        return {
            'total_score': total_score,
            'balance_score': balance_score,
            'completeness_score': completeness_score,
            'level': level
        }


# 全局五行分析器实例
wuxing_analyzer = WuxingAnalyzer()
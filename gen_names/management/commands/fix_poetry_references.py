"""
修复名字的参考诗词关联
确保男性名字只关联诗经，女性名字只关联楚辞
"""
from django.core.management.base import BaseCommand
from gen_names.models import Name, Poetry


class Command(BaseCommand):
    help = '修复名字的参考诗词关联，确保男性名字只关联诗经，女性名字只关联楚辞'

    def handle(self, *args, **options):
        self.stdout.write('开始修复名字的参考诗词关联...')
        
        fixed_count = 0
        error_count = 0
        
        # 获取所有名字
        names = Name.objects.all()
        total = names.count()
        
        for name in names:
            try:
                # 根据性别确定应该关联的诗词类型
                poetry_type = 'shijing' if name.gender == 'M' else 'chuci'
                
                # 清空所有关联
                name.reference_poetry.clear()
                
                # 获取名字中的字符
                name_chars = list(name.given_name)
                related_poem_ids = set()
                
                # 查找每个字符对应的诗词
                for char in name_chars:
                    try:
                        from gen_names.models import Word
                        word_obj = Word.objects.filter(character=char).first()
                        if word_obj:
                            # 只获取指定类型的诗词ID
                            char_poem_ids = word_obj.from_poetry.filter(
                                poetry_type=poetry_type
                            ).values_list('id', flat=True)
                            related_poem_ids.update(char_poem_ids)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f'处理字符 {char} 时出错: {e}'
                        ))
                        continue
                
                # 设置正确的关联
                if related_poem_ids:
                    valid_poems = Poetry.objects.filter(
                        id__in=related_poem_ids,
                        poetry_type=poetry_type
                    )
                    if valid_poems.exists():
                        name.reference_poetry.set(valid_poems)
                        fixed_count += 1
                    else:
                        # 如果没有找到，使用该类型的一些诗词作为参考
                        fallback_poems = Poetry.objects.filter(poetry_type=poetry_type)[:3]
                        if fallback_poems.exists():
                            name.reference_poetry.set(fallback_poems)
                            fixed_count += 1
                else:
                    # 如果没有找到，使用该类型的一些诗词作为参考
                    fallback_poems = Poetry.objects.filter(poetry_type=poetry_type)[:3]
                    if fallback_poems.exists():
                        name.reference_poetry.set(fallback_poems)
                        fixed_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(
                    f'修复名字 {name.full_name} 时出错: {e}'
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f'修复完成！共处理 {total} 个名字，成功修复 {fixed_count} 个，错误 {error_count} 个'
        ))

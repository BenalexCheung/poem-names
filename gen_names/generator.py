import random
from nltk.corpus import names

def generate_name(gender='unknown', origin='unknown', length=6):
    # 如果未指定性别，则从男女名字中随机选择一个
    if gender == 'unknown':
        gender = random.choice(['male', 'female'])

    # 如果未指定名字来源，则从所有名字中随机选择一个
    if origin == 'unknown':
        origin = 'all'

    # 获取名字列表
    name_list = get_name_list(gender=gender, origin=origin)

    # 随机生成一个名字
    name = ''.join(random.choices(name_list, k=length))

    return name

def get_name_list(gender, origin):
    # 如果指定了名字来源，则只使用对应来源的名字
    if origin != 'all':
        name_list = names.words(f'names/{gender}.{origin}')
    else:
        # 否则从所有名字中选择
        if gender == 'male':
            name_list = names.words('male.txt')
        elif gender == 'female':
            name_list = names.words('female.txt')
        else:
            # 如果未指定性别，则使用所有名字
            name_list = names.words()

    return name_list

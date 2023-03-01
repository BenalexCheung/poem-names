from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .generator import generate_name  # 名字生成算法

@csrf_exempt
def generate_name_view(request):
    if request.method == 'POST':
        # # 解析请求参数
        # dynasty = request.POST.get('dynasty')
        # gender = request.POST.get('gender')
        # name_type = request.POST.get('type')

        # # 参数校验
        # if not dynasty or dynasty not in ['tang', 'song', 'yuan', 'ming', 'qing']:
        #     return JsonResponse({'status': 400, 'message': 'Invalid dynasty parameter'})
        # if not gender or gender not in ['male', 'female']:
        #     return JsonResponse({'status': 400, 'message': 'Invalid gender parameter'})
        # if not name_type or name_type not in ['given', 'surname']:
        #     return JsonResponse({'status': 400, 'message': 'Invalid type parameter'})

        # 调用名字生成算法
        name = generate_name()

        return JsonResponse({'status': 200, 'message': 'OK', 'data': {'name': name}})
    else:
        return JsonResponse({'status': 400, 'message': 'Invalid request method'})

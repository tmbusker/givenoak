from django.http import JsonResponse, HttpResponse
import json

from mst.models.ido import IdoSyumoku


def select_ido_type(request):
    """異動タイプの選択"""
    if request.method == 'GET':
        ido_type = request.GET['ido_type']
    elif request.method == 'POST':
        data = json.load(request)['data']
        ido_type = data.get('ido_type')
    else:
        return HttpResponse("Request method is invalid.", status=405)
    
    if not ido_type:
        return HttpResponse("Invalid parameter.", status=405)
    
    ido_syumoku_list = IdoSyumoku.objects.filter(ido_type__code=ido_type).values_list('code', 'name')
    return JsonResponse({'data': list(ido_syumoku_list)})
    
    

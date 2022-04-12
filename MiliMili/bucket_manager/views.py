from bucket_manager.Bucket import Bucket
from django.http import JsonResponse


def callback(request, bucket_name, key_name):
    bucket = Bucket()
    if request.method == 'GET':
        url = 'http://101.42.224.73:8000/api/bucket_manager/callback/' + bucket_name + '/' + key_name + '/'
        try:
            bucket.video_audit_submit(bucket_name, key_name, url)
        except Exception:
            result = {'result': -1}
        else:
            result = {'result': 1}
        return JsonResponse(result)
    elif request.method == 'POST':
        result = bucket.video_audit_query(request.POST)
        return JsonResponse(result)


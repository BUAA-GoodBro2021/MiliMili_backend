import json
from bucket_manager.Bucket import Bucket
from django.http import JsonResponse


def callback(request, bucket_name, key_name):
    bucket = Bucket()
    if request.method == 'GET':
        host = 'http://101.42.224.73:8000/'
        url = host + 'api/bucket_manager/callback/' + bucket_name + '/' + key_name + '/'
        try:
            job_id = bucket.video_audit_submit(bucket_name, key_name, url)
        except Exception:
            result = {'result': -1, 'job_id': None}
        else:
            result = {'result': 1, 'job_id': job_id}
        return JsonResponse(result)
    elif request.method == 'POST':
        body = json.loads(request.body)
        result = bucket.video_audit_query(request.body)
        return JsonResponse(result)


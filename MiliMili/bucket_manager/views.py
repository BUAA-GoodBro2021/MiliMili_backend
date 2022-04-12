import json
from bucket_manager.Bucket import Bucket
from django.http import JsonResponse


def callback(request):
    bucket = Bucket()
    if request.method == 'POST':
        body = json.loads(request.body)
        result = bucket.video_audit_query(body)
    else:
        result = {'result': -1, 'label': None, 'job_id': None}
    return JsonResponse(result)

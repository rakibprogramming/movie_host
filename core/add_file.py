import os
from django.shortcuts import render
import requests
import time
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

STATUS_FILE = os.path.join(settings.MEDIA_ROOT, 'status.txt')


def add(request):
    return render(request, "add_video.html")

@csrf_exempt
def start_download(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    data = json.loads(request.body)
    url = data.get('url')
    if not url:
        return JsonResponse({'success': False, 'error': 'No URL provided'})

    try:
        # Determine filename from URL
        filename = os.path.basename(url.split('?')[0])
        save_path = os.path.join(settings.MEDIA_ROOT, filename)

        # Stream download with status
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_length = r.headers.get('content-length')
            if total_length is None:
                total_length = 0
            else:
                total_length = int(total_length)

            downloaded = 0
            start_time = time.time()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        elapsed = max(time.time() - start_time, 0.001)
                        percent = round((downloaded / total_length) * 100, 2) if total_length else 0
                        speed = round((downloaded / 1024) / elapsed, 2)  # KB/s

                        # Write status
                        with open(STATUS_FILE, 'w') as s:
                            s.write(json.dumps({'percent': percent, 'speed': speed}))
        # Ensure 100% at end
        with open(STATUS_FILE, 'w') as s:
            s.write(json.dumps({'percent': 100, 'speed': 0}))

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



def download_status(request):
    if not os.path.exists(STATUS_FILE):
        return JsonResponse({'percent': 0, 'speed': 0})
    try:
        with open(STATUS_FILE, 'r') as f:
            import json
            data = json.load(f)
            return JsonResponse(data)
    except:
        return JsonResponse({'percent': 0, 'speed': 0})

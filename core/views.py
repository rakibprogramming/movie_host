from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.http import Http404
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from urllib.parse import urlparse
import requests


def home(request):
    media_folder = settings.MEDIA_ROOT
    videos = []

    # List all .mp4 files in media folder with their mtime
    for f in os.listdir(media_folder):
        if f.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.mpg', '.mpeg')):
            full_path = os.path.join(media_folder, f)
            mtime = os.path.getmtime(full_path)
            videos.append((f, mtime))

    # Sort by modification time, newest first
    videos.sort(key=lambda x: x[1], reverse=True)

    # Only keep filenames for template
    videos = [v[0] for v in videos]

    context = {
        'videos': videos
    }

    return render(request, 'home.html', context)


def view(request):
    filename = request.GET.get('filename')
    if not filename:
        raise Http404("No video specified")

    video_path = os.path.join(settings.MEDIA_ROOT, filename)
    if not os.path.exists(video_path):
        raise Http404("Video not found")

    # Look for any subtitle files matching the video name in media/sub
    name_without_ext = os.path.splitext(filename)[0]
    sub_folder = os.path.join(settings.MEDIA_ROOT, 'sub')
    subtitles = []

    if os.path.exists(sub_folder):
        for f in os.listdir(sub_folder):
            if f.startswith(name_without_ext) and f.lower().endswith(('.srt', '.vtt')):
                subtitles.append(f)

    context = {
        'video_file': filename,
        'subtitles': subtitles  # list of subtitle filenames
    }

    return render(request, 'view.html', context)




@csrf_exempt  # use only for local/personal server
def add_subtitle(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    import json
    data = json.loads(request.body)
    video_name = data.get('video')
    url = data.get('url')

    if not video_name or not url:
        return JsonResponse({'success': False, 'error': 'Missing video or URL'})

    # Get extension from URL
    parsed = urlparse(url)
    ext = os.path.splitext(parsed.path)[1]
    if ext.lower() not in ('.srt', '.vtt'):
        return JsonResponse({'success': False, 'error': 'Unsupported subtitle format'})

    # Save file to media/sub/
    sub_folder = os.path.join(settings.MEDIA_ROOT, 'sub')
    os.makedirs(sub_folder, exist_ok=True)

    # Keep video base name, change extension
    base_name = os.path.splitext(video_name)[0]
    save_path = os.path.join(sub_folder, f"{base_name}{ext}")

    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(r.content)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': True})



@csrf_exempt  # only for personal server
def delete_video(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'})

    import json
    data = json.loads(request.body)
    video_name = data.get('video')
    if not video_name:
        return JsonResponse({'success': False, 'error': 'No video specified'})

    video_path = os.path.join(settings.MEDIA_ROOT, video_name)
    if not os.path.exists(video_path):
        return JsonResponse({'success': False, 'error': 'Video not found'})

    try:
        os.remove(video_path)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': True})
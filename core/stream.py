# movie/views.py
import os
from django.conf import settings
from django.http import StreamingHttpResponse, Http404, HttpResponse
import pysrt

def stream_video(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename) 
    if not os.path.exists(file_path):
        raise Http404("File not found")

    def file_iterator(path, chunk_size=8192):
        with open(path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                yield data

    response = StreamingHttpResponse(file_iterator(file_path), content_type='video/mp4')
    response['Content-Length'] = os.path.getsize(file_path)
    response['Accept-Ranges'] = 'bytes'
    return response

 
def stream_subtitle(request, filename):
    """
    Streams subtitle file.
    Converts .srt to .vtt automatically if needed.
    """
    # Full path to file
    file_path = os.path.join(settings.MEDIA_ROOT, 'sub', filename)
    if not os.path.exists(file_path):
        raise Http404("Subtitle file not found")

    # If .vtt, just stream
    if filename.endswith('.vtt'):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type='text/vtt')
 
    # If .srt, convert to .vtt on the fly
    elif filename.endswith('.srt'):
        subs = pysrt.open(file_path)
        vtt_content = "WEBVTT\n\n"
        for i, sub in enumerate(subs):
            start = sub.start.to_time()
            end = sub.end.to_time()
            # Format as HH:MM:SS.mmm
            start_str = start.strftime("%H:%M:%S.%f")[:-3]
            end_str = end.strftime("%H:%M:%S.%f")[:-3]
            vtt_content += f"{i+1}\n{start_str} --> {end_str}\n{sub.text}\n\n"

        return HttpResponse(vtt_content, content_type='text/vtt')

    else:
        raise Http404("Unsupported subtitle format")
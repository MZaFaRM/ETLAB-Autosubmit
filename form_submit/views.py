# Create your views here.
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .etlab_script import ETLab
import threading
from django.core.cache import cache


def get_cache_key(request):
    return f"etlab_status_{request.session.session_key}"


def complete_surveys_thread(username, password, cache_key):
    etlab = ETLab(username, password, cache_key)
    etlab.complete_surveys()
    cache.set(cache_key + '_done', True)


def survey_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        cache_key = get_cache_key(request)
        cache.set(cache_key + '_started', True)
        cache.set(cache_key + '_done', False)
        cache.set(cache_key, "")

        thread = threading.Thread(
            target=complete_surveys_thread,
            args=(username, password, cache_key),
        )
        thread.start()

        return redirect("progress")

    return render(request, "login_survey.html")


def etlab_status(request):
    cache_key = get_cache_key(request)

    output = cache.get(cache_key, "")
    done = cache.get(cache_key + '_done', False)
    return JsonResponse({'output': output, 'done': done})


def progress(request):
    cache_key = get_cache_key(request)
    if not cache.get(cache_key + '_started', False):
        return redirect('login')
    return render(request, "progress.html")

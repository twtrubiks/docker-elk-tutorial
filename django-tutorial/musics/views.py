from django.shortcuts import render

from musics.models import Music
from django.http import Http404


# Create your views here.
def hello_view(request):
    musics = Music.objects.all()
    # raise Exception('error !!!!')
    # raise Http404("sorry 404")
    return render(request, 'hello_django.html', {
        'data': "Hello Django ",
        'musics': musics,
    })

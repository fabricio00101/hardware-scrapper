from django.shortcuts import render
from .scraper import rastreador_dinamico

def inicio(request):
    query = request.GET.get('q', '')
    resultados = []

    if query:
        resultados = rastreador_dinamico(query)

    return render(request, 'index.html',{
        'ofertas': resultados,
        'query': query
    })

# Create your views here.

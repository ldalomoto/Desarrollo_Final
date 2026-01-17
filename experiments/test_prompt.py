from core.enrich import enrich_text

def noticia(new):
    result = enrich_text(new)
    print(result)

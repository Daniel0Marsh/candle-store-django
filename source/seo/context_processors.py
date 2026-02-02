from .models import PageSEO

def seo_meta(request):
    """
    Returns the SEO object for the current path (static page).
    Can be used in templates as 'meta'.
    """
    path = request.path
    try:
        seo_obj = PageSEO.objects.get(url_path=path)
        meta = seo_obj.meta
    except PageSEO.DoesNotExist:
        meta = None
    return {"meta": meta}
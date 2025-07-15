from .models import ZakahNisab

def zakah_nisab(request):
    try:
        current_nisab = ZakahNisab.objects.filter(is_active=True).first()
    except:
        current_nisab = None
    return {'current_nisab': current_nisab} 
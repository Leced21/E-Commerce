# ton_app/context_processors.py
from .models import Cart

def cart_count(request):
    count = 0
    # On s'assure qu'une session existe pour les visiteurs anonymes
    if not request.session.session_key:
        request.session.create()
        
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            cart = Cart.objects.filter(session_key=request.session.session_key).first()
        
        if cart:
            # On utilise .count() ou sum() sur les items
            count = sum(item.quantity for item in cart.items.all())
    except Exception:
        count = 0
        
    return {'cart_item_count': count}
from django.shortcuts import render
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, Order, OrderItem, Category, Product
from .stripe_service import create_payment_intent
import logging
from django.core.cache import cache


# Initialisez Stripe pour les Webhooks
stripe.api_key = settings.STRIPE_SECRET_KEY
WEBHOOK_SECRET = settings.STRIPE_WEBHOOK_SECRET
logger = logging.getLogger(__name__)


class CreatePaymentIntentView(APIView):
    """
    Crée une intention de paiement Stripe à partir du panier de l'utilisateur.
    """

    def post(self, request, *args, **kwargs):
        # 1. Récupérer le panier de l'utilisateur (simplifié ici)
        user = request.user
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {"error": "Panier non trouvé."}, status=status.HTTP_404_NOT_FOUND
            )

        # 2. Calculer le total du panier (en centimes, Stripe exige des entiers)
        # ASSUMPTION: Votre CartItem.variant a un champ 'price_default'
        total_price_decimal = sum(
            item.quantity * item.variant.price_default for item in cart.items.all()
        )
        amount_in_cents = int(total_price_decimal * 100)  # Montant en centimes

        if amount_in_cents <= 50:  # Minimum Stripe (0.50 EUR/USD)
            return Response(
                {"error": "Le montant est trop faible pour le paiement."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Créer la Commande (Order) en statut 'pending'
        order = Order.objects.create(
            user=user,
            shipping_address="Adresse de démo",  # Ceci doit venir de la requête client
            billing_address="Adresse de démo",
            total_paid=total_price_decimal,
            status="pending",
        )
        # Transférer les articles du panier à la commande
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product_variant=item.variant,
                quantity=item.quantity,
                price_at_time_of_purchase=item.variant.price_default,  # Enregistrer le prix
            )

        # 4. Créer l'intention de paiement Stripe
        intent = create_payment_intent(
            amount_in_cents=amount_in_cents,
            metadata={"order_id": order.id, "user_id": user.id},
        )

        if intent:
            # 5. Mettre à jour la commande avec l'ID du Payment Intent
            order.stripe_payment_intent_id = intent.id
            order.save()

            # 6. Renvoyer le 'client_secret' au frontend
            return Response(
                {
                    "client_secret": intent.client_secret,
                    "public_key": settings.STRIPE_PUBLIC_KEY,
                    "order_id": order.id,
                }
            )

        # Gérer l'échec de création de l'intention
        order.status = "failed_creation"
        order.save()
        return Response(
            {"error": "Erreur lors de la création du Payment Intent."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@csrf_exempt
def stripe_webhook(request):
    """
    Gère les notifications d'événements (webhooks) envoyées par Stripe.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        # 1. Vérifie la signature pour s'assurer que l'appel vient bien de Stripe
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError as e:
        # Charge utile invalide
        print(f"Erreur de payload Stripe : {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Signature invalide
        logger.error(f"Erreur de vérification de signature Stripe : {e}")
        return HttpResponse(status=400)

    # 2. Gère l'événement
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]

        # Récupère l'ID de la commande que nous avons stocké dans les metadata
        order_id = intent["metadata"].get("order_id")

        if order_id:
            try:
                order = Order.objects.get(id=order_id)

                if order.status == "pending":
                    # 3. Met à jour le statut de la commande
                    order.status = "processing"
                    order.save()

                    # 4. Vide le panier de l'utilisateur (logique à implémenter)
                    # if order.user:
                    #     Cart.objects.filter(user=order.user).delete()

                    print(
                        f"Paiement réussi pour la commande {order_id}. Statut mis à jour."
                    )

            except Order.DoesNotExist:
                print(f"ERREUR: Commande {order_id} non trouvée.")

    elif event["type"] == "payment_intent.payment_failed":
        # Gérer l'échec de paiement (ex: envoyer une alerte, mettre le statut à 'failed')
        pass

    return HttpResponse(status=200)  # Stripe attend toujours un code 200


class CategoryListView(APIView):
    def get(self, request, *args, **kwargs):
        CACHE_KEY = "all_categories"
        data = cache.get(CACHE_KEY)  # Essaie de lire les données du cache

        if data is None:
            # Si le cache est vide, interroge la base de données (lourd)
            categories = Category.objects.all().values("id", "name", "slug")
            data = list(categories)  # Conversion en liste pour le cache

            # Stocke les données dans le cache pour 3600 secondes (1 heure)
            cache.set(CACHE_KEY, data, 3600)

            print("CACHE MISS: Données lues depuis la base de données.")
        else:
            print("CACHE HIT: Données lues depuis Redis.")

        return Response(data)


def home(request):
    return render(request, "core/home.html")

def product_list(request):
    # On récupère les produits actifs et on pré-charge les variantes pour avoir l'image et le prix
    products = Product.objects.filter(is_active=True).prefetch_related('variants')
    return render(request, 'pages/index.html', {'products': products})

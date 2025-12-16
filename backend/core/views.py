from django.shortcuts import render

# backend/core/views.py (exemple simplifié)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, Order, OrderItem
from .stripe_service import create_payment_intent


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


def home(request):
    return render(request, "core/home.html")

import stripe
import os
from django.conf import settings

# Initialise le client Stripe avec la clé secrète
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(amount_in_cents: int, currency: str = 'eur', metadata: dict = None):
    """Crée une intention de paiement auprès de l'API Stripe."""
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency=currency,
            # Le Payment Intent stocke des infos que vous pouvez récupérer plus tard
            metadata=metadata if metadata else {},
            # Ajoutez une méthode de paiement supportée
            automatic_payment_methods={"enabled": True}, 
        )
        return intent
    except stripe.error.StripeError as e:
        # Gérer les erreurs Stripe (clé invalide, montant invalide, etc.)
        print(f"Erreur Stripe lors de la création de l'intention: {e}")
        return None
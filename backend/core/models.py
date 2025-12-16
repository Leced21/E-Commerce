from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

User = get_user_model() # Récupère le modèle utilisateur actif


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    price_default = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    sku = models.CharField(
        max_length=50, unique=True
    )  # Clé unique de gestion des stocks
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)
    additional_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Supplément de prix pour cette variante.",
    )
    stock = models.IntegerField(default=0)
    # L'ImageField utilisera GCS grâce à vos paramètres de production
    image = models.ImageField(upload_to="product_variants/", blank=True, null=True)

    class Meta:
        unique_together = ("product", "color", "size")

    def __str__(self):
        return f"{self.product.name} - {self.color}/{self.size}"
    
# Modèle pour le Panier
class Cart(models.Model):
    # Relie le panier à un utilisateur (peut être nul pour les utilisateurs anonymes)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='cart')
    # Clé unique pour lier les paniers des utilisateurs anonymes aux sessions
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Panier de {self.user.username}"
        return f"Panier anonyme ({self.session_key[:8]})"
    
    # Propriété pour calculer le total du panier (vous développerez la logique dans les vues)
    # @property
    # def total_price(self):
    #     return sum(item.sub_total for item in self.items.all())

# Modèle pour les Articles du Panier
class CartItem(models.Model):
    # Lien vers le panier parent
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    # Lien vers la variante de produit spécifique (SKU)
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE) 
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # Assure qu'un produit donné ne peut être ajouté qu'une seule fois par panier
        unique_together = ('cart', 'variant') 

    def __str__(self):
        return f"{self.quantity} x {self.variant.product.name} ({self.variant.size})"

    # Propriété pour calculer le sous-total de l'article (vous développerez la logique)
    # @property
    # def sub_total(self):
    #     # Doit retourner le prix de la variante * la quantité
    #     return self.quantity * self.variant.price_default # Correction: utiliser le prix effectif de la variante

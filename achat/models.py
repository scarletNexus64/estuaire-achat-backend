from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
import uuid


class CustomUserManager(UserManager):
    def create_user(self, identifier, nom=None, prenom=None, password=None, **extra_fields):
        if not identifier:
            raise ValueError('The Identifier field must be set')
        
        # Créer un username par défaut basé sur l'identifier si non fourni
        if 'username' not in extra_fields:
            extra_fields['username'] = identifier
            
        user = self.model(
            identifier=identifier,
            nom=nom or '',
            prenom=prenom or '',
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, identifier, nom, prenom, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(identifier, nom, prenom, password, **extra_fields)


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('customer', 'Client'),
        ('vendor', 'Fournisseur'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identifier = models.CharField(max_length=255, unique=True)  # email ou telephone
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    photo_profile = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('O', 'Autre')
    ])
    birthday = models.DateField(blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    
    USERNAME_FIELD = 'identifier'
    REQUIRED_FIELDS = ['nom', 'prenom']
    
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.identifier})"


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)  # city name
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='locations')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'is_default']  # Un seul default par user

    def __str__(self):
        return f"{self.name} - {self.user.prenom} {self.user.nom}"

    def save(self, *args, **kwargs):
        # Si c'est la localisation par défaut, supprimer le défaut des autres
        if self.is_default:
            Location.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class UserToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='auth_token')
    token = models.UUIDField(unique=True, default=uuid.uuid4)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Token for {self.user.identifier} ({'Active' if self.is_active else 'Inactive'})"


class SubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    name_trl = models.CharField(max_length=255, verbose_name="Name (English)", help_text="English translation")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sous-catégorie"
        verbose_name_plural = "Sous-catégories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    name_trl = models.CharField(max_length=255, verbose_name="Name (English)", help_text="English translation")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    subcategories = models.ManyToManyField(SubCategory, related_name='categories', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"


class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('pending', 'En attente'),
        ('sold', 'Vendu'),
    ]

    PAYMENT_CONDITIONS_CHOICES = [
        ('cash', 'Espèces'),
        ('transfer', 'Virement'),
        ('mobile', 'Mobile Money'),
        ('negotiable', 'Négociable'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='products')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField(default=1)
    is_stock = models.BooleanField(default=True)
    images = models.ManyToManyField(ProductImage, blank=True, related_name='products')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(blank=True, null=True)
    conditions_paiement = models.CharField(max_length=20, choices=PAYMENT_CONDITIONS_CHOICES, default='negotiable')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.user.prenom} {self.user.nom}"


class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Liste de souhaits"
        verbose_name_plural = "Listes de souhaits"
        unique_together = ['user', 'product']  # Un utilisateur ne peut ajouter un produit qu'une seule fois
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.prenom} {self.user.nom} - {self.product.name}"


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=255)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} - {self.user.prenom} {self.user.nom} ({'Lu' if self.is_read else 'Non lu'})"


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def __str__(self):
        return f"Panier de {self.user.prenom} {self.user.nom}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product.name} x{self.quantity} - {self.cart.user.prenom}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='orders')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande {self.order_number} - {self.user.prenom} {self.user.nom}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            from django.utils import timezone
            import random
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_digits = str(random.randint(1000, 9999))
            self.order_number = f"EST{timestamp}{random_digits}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"

    def __str__(self):
        return f"{self.product.name} x{self.quantity} - Commande {self.order.order_number}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews_given')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    vendor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews_received')
    order_item = models.OneToOneField(OrderItem, on_delete=models.CASCADE, related_name='review', null=True, blank=True)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        unique_together = ['user', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis de {self.user.prenom} sur {self.product.name} - {self.rating}⭐"

    def save(self, *args, **kwargs):
        self.vendor = self.product.user
        if self.order_item and self.order_item.order.user == self.user:
            self.is_verified = True
        super().save(*args, **kwargs)


class VendorRating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='vendor_rating')
    total_reviews = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_1_count = models.PositiveIntegerField(default=0)
    rating_2_count = models.PositiveIntegerField(default=0)
    rating_3_count = models.PositiveIntegerField(default=0)
    rating_4_count = models.PositiveIntegerField(default=0)
    rating_5_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Note Vendeur"
        verbose_name_plural = "Notes Vendeurs"

    def __str__(self):
        return f"Note de {self.vendor.prenom} {self.vendor.nom} - {self.average_rating}⭐ ({self.total_reviews} avis)"

    def update_rating(self):
        from django.db.models import Avg, Count
        
        reviews = Review.objects.filter(vendor=self.vendor)
        
        self.total_reviews = reviews.count()
        
        if self.total_reviews > 0:
            self.average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
            
            rating_counts = reviews.values('rating').annotate(count=Count('rating'))
            
            self.rating_1_count = 0
            self.rating_2_count = 0
            self.rating_3_count = 0
            self.rating_4_count = 0
            self.rating_5_count = 0
            
            for item in rating_counts:
                setattr(self, f"rating_{item['rating']}_count", item['count'])
        else:
            self.average_rating = 0.00
            
        self.save()


class DeliveryOption(models.Model):
    DELIVERY_TYPE_CHOICES = [
        ('pickup', 'Retrait en point'),
        ('home', 'Livraison à domicile'),
        ('express', 'Livraison express'),
        ('standard', 'Livraison standard'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estimated_days_min = models.PositiveIntegerField(default=1)
    estimated_days_max = models.PositiveIntegerField(default=3)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Option de livraison"
        verbose_name_plural = "Options de livraison"
        ordering = ['price']

    def __str__(self):
        return f"{self.name} - {self.price} FCFA ({self.estimated_days_min}-{self.estimated_days_max} jours)"


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('preparing', 'Préparation'),
        ('picked_up', 'Récupéré'),
        ('in_transit', 'En transit'),
        ('out_for_delivery', 'En cours de livraison'),
        ('delivered', 'Livré'),
        ('failed', 'Échec de livraison'),
        ('returned', 'Retourné'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    tracking_number = models.CharField(max_length=50, unique=True)
    delivery_option = models.ForeignKey(DeliveryOption, on_delete=models.CASCADE, related_name='shipments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparing')
    estimated_delivery_date = models.DateTimeField(null=True, blank=True)
    actual_delivery_date = models.DateTimeField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Expédition"
        verbose_name_plural = "Expéditions"
        ordering = ['-created_at']

    def __str__(self):
        return f"Expédition {self.tracking_number} - Commande {self.order.order_number}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            from django.utils import timezone
            import random
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            random_digits = str(random.randint(100, 999))
            self.tracking_number = f"SHIP{timestamp}{random_digits}"
        
        if self.status == 'delivered' and not self.actual_delivery_date:
            from django.utils import timezone
            self.actual_delivery_date = timezone.now()
            
        super().save(*args, **kwargs)

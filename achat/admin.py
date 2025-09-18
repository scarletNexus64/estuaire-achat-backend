from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import CustomUser, Location, UserToken, Category, SubCategory, Product, ProductImage, Wishlist, Notification, Cart, CartItem, Order, OrderItem, Review, VendorRating, DeliveryOption, Shipment
from .admin_dashboard import achat_dashboard_view


class LocationInline(admin.TabularInline):
    model = Location
    extra = 0
    fields = ['name', 'longitude', 'latitude', 'is_default']
    readonly_fields = ['created_at', 'updated_at']


class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        'get_avatar', 'identifier', 'get_full_name', 'get_user_type', 'gender', 
        'get_location_count', 'get_product_count', 'is_active', 'date_joined'
    ]
    list_filter = ['user_type', 'gender', 'is_active', 'date_joined']
    search_fields = ['identifier', 'nom', 'prenom', 'username']
    inlines = [LocationInline]
    readonly_fields = ['id', 'date_joined', 'last_login']
    
    fieldsets = (
        ('👤 Informations Personnelles', {
            'fields': ('identifier', 'nom', 'prenom', 'photo_profile', 'gender', 'birthday', 'user_type')
        }),
        ('🔐 Informations de Connexion', {
            'fields': ('username', 'password', 'last_login')
        }),
        ('⚙️ Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    def get_avatar(self, obj):
        if obj.photo_profile:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />',
                obj.photo_profile.url
            )
        return "👤"
    get_avatar.short_description = "Avatar"
    
    def get_full_name(self, obj):
        return f"{obj.prenom} {obj.nom}"
    get_full_name.short_description = "Nom Complet"
    
    def get_user_type(self, obj):
        type_colors = {
            'customer': '#28a745',
            'vendor': '#6366F1'
        }
        type_icons = {
            'customer': '👤',
            'vendor': '🏪'
        }
        color = type_colors.get(obj.user_type, '#6c757d')
        icon = type_icons.get(obj.user_type, '❓')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_user_type_display()
        )
    get_user_type.short_description = "Type"
    
    def get_location_count(self, obj):
        count = obj.locations.count()
        if count > 0:
            return format_html(
                '<span style="background: #f35453; color: white; padding: 2px 6px; border-radius: 10px;">📍 {}</span>',
                count
            )
        return "📍 0"
    get_location_count.short_description = "Localisations"
    
    def get_product_count(self, obj):
        count = obj.products.count()
        if count > 0:
            return format_html(
                '<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 10px;">🛍️ {}</span>',
                count
            )
        return "🛍️ 0"
    get_product_count.short_description = "Produits"


class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_user_info', 'is_default', 'get_coordinates', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'user__nom', 'user__prenom', 'user__identifier']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('📍 Informations de Localisation', {
            'fields': ('name', 'user', 'is_default')
        }),
        ('🗺️ Coordonnées', {
            'fields': ('latitude', 'longitude')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        return format_html(
            '👤 {} {} ({})',
            obj.user.prenom,
            obj.user.nom,
            obj.user.identifier
        )
    get_user_info.short_description = "Utilisateur"
    
    def get_coordinates(self, obj):
        return f"🌍 {obj.latitude}, {obj.longitude}"
    get_coordinates.short_description = "Coordonnées"


class UserTokenAdmin(admin.ModelAdmin):
    list_display = ['get_user_info', 'get_token_preview', 'get_status', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['user__nom', 'user__prenom', 'user__identifier', 'token']
    readonly_fields = ['id', 'token', 'created_at', 'updated_at']
    
    fieldsets = (
        ('🔑 Token Information', {
            'fields': ('user', 'token', 'is_active')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        return format_html(
            '👤 {} {} ({})',
            obj.user.prenom,
            obj.user.nom,
            obj.user.identifier
        )
    get_user_info.short_description = "Utilisateur"
    
    def get_token_preview(self, obj):
        token_str = str(obj.token)
        return format_html(
            '<code style="background: #f35453; color: white; padding: 2px 6px; border-radius: 3px;">🔑 {}...{}</code>',
            token_str[:8],
            token_str[-8:]
        )
    get_token_preview.short_description = "Token (Aperçu)"
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px;">✅ Actif</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 10px;">❌ Inactif</span>'
            )
    get_status.short_description = "Statut"


class SubCategoryInline(admin.TabularInline):
    model = Category.subcategories.through
    extra = 0
    verbose_name = "Sous-catégorie associée"
    verbose_name_plural = "Sous-catégories associées"


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_trl', 'get_status', 'get_categories_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'name_trl', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('📂 Informations Générales', {
            'fields': ('name', 'name_trl', 'description', 'is_active')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px;">✅ Actif</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 10px;">❌ Inactif</span>'
            )
    get_status.short_description = "Statut"
    
    def get_categories_count(self, obj):
        count = obj.categories.count()
        if count > 0:
            return format_html(
                '<span style="background: #007bff; color: white; padding: 2px 6px; border-radius: 10px;">📁 {}</span>',
                count
            )
        return "📁 0"
    get_categories_count.short_description = "Catégories"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_trl', 'get_status', 'get_subcategories_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'name_trl', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['subcategories']
    
    fieldsets = (
        ('📁 Informations Générales', {
            'fields': ('name', 'name_trl', 'description', 'is_active')
        }),
        ('📂 Sous-catégories', {
            'fields': ('subcategories',)
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px;">✅ Actif</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 10px;">❌ Inactif</span>'
            )
    get_status.short_description = "Statut"
    
    def get_subcategories_count(self, obj):
        count = obj.subcategories.count()
        if count > 0:
            return format_html(
                '<span style="background: #6f42c1; color: white; padding: 2px 6px; border-radius: 10px;">📂 {}</span>',
                count
            )
        return "📂 0"
    get_subcategories_count.short_description = "Sous-catégories"


class ProductImageInline(admin.TabularInline):
    model = Product.images.through
    extra = 0
    verbose_name = "Image du produit"
    verbose_name_plural = "Images du produit"


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['get_image_preview', 'get_products_count', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('🖼️ Image', {
            'fields': ('image',)
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "🖼️"
    get_image_preview.short_description = "Aperçu"
    
    def get_products_count(self, obj):
        count = obj.products.count()
        if count > 0:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 10px;">🛍️ {}</span>',
                count
            )
        return "🛍️ 0"
    get_products_count.short_description = "Produits"


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'get_user_info', 'get_price', 'get_category_info', 
        'get_status', 'get_stock_status', 'get_images_count', 'created_at'
    ]
    list_filter = ['status', 'is_stock', 'category', 'subcategory', 'conditions_paiement', 'created_at']
    search_fields = ['name', 'description', 'user__nom', 'user__prenom', 'user__identifier']
    readonly_fields = ['id', 'created_at', 'updated_at']
    filter_horizontal = ['images']
    
    fieldsets = (
        ('🛍️ Informations Produit', {
            'fields': ('name', 'description', 'price', 'quantity', 'is_stock', 'status')
        }),
        ('👤 Vendeur et Localisation', {
            'fields': ('user', 'location')
        }),
        ('📁 Catégorisation', {
            'fields': ('category', 'subcategory')
        }),
        ('🖼️ Images', {
            'fields': ('images',)
        }),
        ('💰 Conditions de Paiement', {
            'fields': ('conditions_paiement',)
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        return format_html(
            '👤 {} {} ({})',
            obj.user.prenom,
            obj.user.nom,
            obj.user.identifier
        )
    get_user_info.short_description = "Vendeur"
    
    def get_price(self, obj):
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold;">💰 {} FCFA</span>',
            obj.price
        )
    get_price.short_description = "Prix"
    
    def get_category_info(self, obj):
        if obj.category and obj.subcategory:
            return format_html(
                '📁 {} → 📂 {}',
                obj.category.name,
                obj.subcategory.name
            )
        elif obj.category:
            return format_html('📁 {}', obj.category.name)
        return "❌ Non catégorisé"
    get_category_info.short_description = "Catégorie"
    
    def get_status(self, obj):
        status_colors = {
            'active': '#28a745',
            'inactive': '#6c757d',
            'pending': '#ffc107',
            'sold': '#dc3545'
        }
        status_icons = {
            'active': '✅',
            'inactive': '⏸️',
            'pending': '⏳',
            'sold': '💰'
        }
        color = status_colors.get(obj.status, '#6c757d')
        icon = status_icons.get(obj.status, '❓')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 10px;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    get_status.short_description = "Statut"
    
    def get_stock_status(self, obj):
        if obj.is_stock:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px;">📦 En stock ({})</span>',
                obj.quantity
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 10px;">📭 Rupture</span>'
            )
    get_stock_status.short_description = "Stock"
    
    def get_images_count(self, obj):
        count = obj.images.count()
        if count > 0:
            return format_html(
                '<span style="background: #6f42c1; color: white; padding: 2px 6px; border-radius: 10px;">🖼️ {}</span>',
                count
            )
        return "🖼️ 0"
    get_images_count.short_description = "Images"


class WishlistAdmin(admin.ModelAdmin):
    list_display = [
        'get_user_info', 'get_product_info', 'get_product_price',
        'get_product_status', 'created_at'
    ]
    list_filter = ['created_at', 'product__status', 'product__category']
    search_fields = [
        'user__nom', 'user__prenom', 'user__identifier',
        'product__name', 'product__description'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('📋 Informations Wishlist', {
            'fields': ('user', 'product')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        return format_html(
            '👤 {} {} ({})',
            obj.user.prenom,
            obj.user.nom,
            obj.user.identifier
        )
    get_user_info.short_description = "Utilisateur"
    
    def get_product_info(self, obj):
        return format_html(
            '🛍️ {}',
            obj.product.name
        )
    get_product_info.short_description = "Produit"
    
    def get_product_price(self, obj):
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold;">💰 {} FCFA</span>',
            obj.product.price
        )
    get_product_price.short_description = "Prix"
    
    def get_product_status(self, obj):
        status_colors = {
            'active': '#28a745',
            'inactive': '#6c757d',
            'pending': '#ffc107',
            'sold': '#dc3545'
        }
        status_icons = {
            'active': '✅',
            'inactive': '⏸️',
            'pending': '⏳',
            'sold': '💰'
        }
        color = status_colors.get(obj.product.status, '#6c757d')
        icon = status_icons.get(obj.product.status, '❓')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 10px;">{} {}</span>',
            color,
            icon,
            obj.product.get_status_display()
        )
    get_product_status.short_description = "Statut Produit"


class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'get_user_info', 'get_read_status', 
        'get_content_preview', 'created_at'
    ]
    list_filter = ['is_read', 'created_at', 'updated_at']
    search_fields = [
        'titre', 'content', 'user__nom', 'user__prenom', 'user__identifier'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('📢 Contenu Notification', {
            'fields': ('user', 'titre', 'content', 'is_read')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        return format_html(
            '👤 {} {} ({})',
            obj.user.prenom,
            obj.user.nom,
            obj.user.identifier
        )
    get_user_info.short_description = "Utilisateur"
    
    def get_read_status(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px;">📖 Lue</span>'
            )
        else:
            return format_html(
                '<span style="background: #ffc107; color: black; padding: 2px 8px; border-radius: 10px;">📬 Non lue</span>'
            )
    get_read_status.short_description = "Statut"
    
    def get_content_preview(self, obj):
        content = obj.content
        if len(content) > 100:
            content = content[:100] + '...'
        return format_html(
            '<span style="font-style: italic; color: #6c757d;">{}</span>',
            content
        )
    get_content_preview.short_description = "Aperçu"


class VendorAdmin(admin.ModelAdmin):
    """Admin spécialisé pour la gestion des fournisseurs (vendors)"""
    
    def get_queryset(self, request):
        # Afficher seulement les vendors
        return CustomUser.objects.filter(user_type='vendor')
    
    list_display = [
        'get_avatar', 'identifier', 'get_full_name', 'get_vendor_status',
        'get_product_count', 'get_location_count', 'is_active', 'date_joined'
    ]
    list_filter = ['is_active', 'gender', 'date_joined']
    search_fields = ['identifier', 'nom', 'prenom', 'username']
    readonly_fields = ['id', 'date_joined', 'last_login', 'user_type']
    
    fieldsets = (
        ('🏪 Informations Fournisseur', {
            'fields': ('identifier', 'nom', 'prenom', 'photo_profile', 'gender', 'birthday', 'user_type')
        }),
        ('🔐 Accès Plateforme', {
            'fields': ('username', 'password', 'last_login', 'is_active')
        }),
        ('📊 Statistiques', {
            'fields': ('id', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    def get_avatar(self, obj):
        if obj.photo_profile:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />',
                obj.photo_profile.url
            )
        return "🏪"
    get_avatar.short_description = "Avatar"
    
    def get_full_name(self, obj):
        return f"{obj.prenom} {obj.nom}"
    get_full_name.short_description = "Nom Complet"
    
    def get_vendor_status(self, obj):
        product_count = obj.products.count()
        if product_count > 0:
            if product_count >= 10:
                return format_html(
                    '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px;">🌟 Actif</span>'
                )
            else:
                return format_html(
                    '<span style="background: #ffc107; color: black; padding: 2px 8px; border-radius: 10px;">⭐ Débutant</span>'
                )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 10px;">💤 Inactif</span>'
            )
    get_vendor_status.short_description = "Statut Vendeur"
    
    def get_product_count(self, obj):
        count = obj.products.count()
        active_count = obj.products.filter(status='active').count()
        if count > 0:
            return format_html(
                '<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 10px;">🛍️ {} ({})</span>',
                count, active_count
            )
        return "🛍️ 0"
    get_product_count.short_description = "Produits (Actifs)"
    
    def get_location_count(self, obj):
        count = obj.locations.count()
        if count > 0:
            return format_html(
                '<span style="background: #f35453; color: white; padding: 2px 6px; border-radius: 10px;">📍 {}</span>',
                count
            )
        return "📍 0"
    get_location_count.short_description = "Localisations"


class CustomerAdmin(admin.ModelAdmin):
    """Admin spécialisé pour la gestion des clients"""
    
    def get_queryset(self, request):
        # Afficher seulement les customers
        return CustomUser.objects.filter(user_type='customer')
    
    list_display = [
        'get_avatar', 'identifier', 'get_full_name', 'get_customer_activity',
        'get_wishlist_count', 'get_location_count', 'is_active', 'date_joined'
    ]
    list_filter = ['is_active', 'gender', 'date_joined']
    search_fields = ['identifier', 'nom', 'prenom', 'username']
    readonly_fields = ['id', 'date_joined', 'last_login', 'user_type']
    
    fieldsets = (
        ('👤 Informations Client', {
            'fields': ('identifier', 'nom', 'prenom', 'photo_profile', 'gender', 'birthday', 'user_type')
        }),
        ('🔐 Accès Compte', {
            'fields': ('username', 'password', 'last_login', 'is_active')
        }),
        ('📊 Activité', {
            'fields': ('id', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    def get_avatar(self, obj):
        if obj.photo_profile:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />',
                obj.photo_profile.url
            )
        return "👤"
    get_avatar.short_description = "Avatar"
    
    def get_full_name(self, obj):
        return f"{obj.prenom} {obj.nom}"
    get_full_name.short_description = "Nom Complet"
    
    def get_customer_activity(self, obj):
        wishlist_count = obj.wishlists.count()
        if wishlist_count > 0:
            return format_html(
                '<span style="background: #e83e8c; color: white; padding: 2px 8px; border-radius: 10px;">💝 Actif</span>'
            )
        else:
            return format_html(
                '<span style="background: #6c757d; color: white; padding: 2px 8px; border-radius: 10px;">😴 Passif</span>'
            )
    get_customer_activity.short_description = "Activité"
    
    def get_wishlist_count(self, obj):
        count = obj.wishlists.count()
        if count > 0:
            return format_html(
                '<span style="background: #e83e8c; color: white; padding: 2px 6px; border-radius: 10px;">💝 {}</span>',
                count
            )
        return "💝 0"
    get_wishlist_count.short_description = "Wishlist"
    
    def get_location_count(self, obj):
        count = obj.locations.count()
        if count > 0:
            return format_html(
                '<span style="background: #f35453; color: white; padding: 2px 6px; border-radius: 10px;">📍 {}</span>',
                count
            )
        return "📍 0"
    get_location_count.short_description = "Localisations"


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ['product', 'quantity', 'total_price']
    readonly_fields = ['total_price']


class CartAdmin(admin.ModelAdmin):
    list_display = ['get_user_info', 'get_total_items', 'get_total_amount', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__nom', 'user__prenom', 'user__identifier']
    readonly_fields = ['id', 'total_items', 'total_amount', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    
    fieldsets = (
        ('🛒 Informations Panier', {
            'fields': ('user', 'total_items', 'total_amount')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        return format_html(
            '👤 {} {} ({})',
            obj.user.prenom,
            obj.user.nom,
            obj.user.identifier
        )
    get_user_info.short_description = "Utilisateur"
    
    def get_total_items(self, obj):
        count = obj.total_items
        if count > 0:
            return format_html(
                '<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 10px;">🛍️ {}</span>',
                count
            )
        return "🛍️ 0"
    get_total_items.short_description = "Articles"
    
    def get_total_amount(self, obj):
        amount = obj.total_amount
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold;">💰 {} FCFA</span>',
            amount
        )
    get_total_amount.short_description = "Montant Total"


class CartItemAdmin(admin.ModelAdmin):
    list_display = ['get_cart_user', 'get_product_info', 'quantity', 'get_total_price', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['cart__user__nom', 'cart__user__prenom', 'product__name']
    readonly_fields = ['id', 'total_price', 'created_at', 'updated_at']
    
    fieldsets = (
        ('🛒 Article du Panier', {
            'fields': ('cart', 'product', 'quantity', 'total_price')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_cart_user(self, obj):
        return format_html(
            '👤 {} {} ({})',
            obj.cart.user.prenom,
            obj.cart.user.nom,
            obj.cart.user.identifier
        )
    get_cart_user.short_description = "Utilisateur"
    
    def get_product_info(self, obj):
        return format_html(
            '🛍️ {} - {} FCFA',
            obj.product.name,
            obj.product.price
        )
    get_product_info.short_description = "Produit"
    
    def get_total_price(self, obj):
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold;">💰 {} FCFA</span>',
            obj.total_price
        )
    get_total_price.short_description = "Prix Total"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'vendor', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'get_user_info', 'get_status', 'get_total_amount', 'get_items_count', 'created_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['order_number', 'user__nom', 'user__prenom', 'user__identifier']
    readonly_fields = ['id', 'order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('📋 Informations Commande', {
            'fields': ('order_number', 'user', 'status', 'total_amount')
        }),
        ('📍 Livraison', {
            'fields': ('delivery_location', 'notes')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        return format_html(
            '👤 {} {} ({})',
            obj.user.prenom,
            obj.user.nom,
            obj.user.identifier
        )
    get_user_info.short_description = "Client"
    
    def get_status(self, obj):
        status_colors = {
            'pending': '#ffc107',
            'confirmed': '#17a2b8',
            'processing': '#6f42c1',
            'shipped': '#fd7e14',
            'delivered': '#28a745',
            'cancelled': '#dc3545'
        }
        status_icons = {
            'pending': '⏳',
            'confirmed': '✅',
            'processing': '🔄',
            'shipped': '📦',
            'delivered': '✅',
            'cancelled': '❌'
        }
        color = status_colors.get(obj.status, '#6c757d')
        icon = status_icons.get(obj.status, '❓')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 10px;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    get_status.short_description = "Statut"
    
    def get_total_amount(self, obj):
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold;">💰 {} FCFA</span>',
            obj.total_amount
        )
    get_total_amount.short_description = "Montant Total"
    
    def get_items_count(self, obj):
        count = obj.items.count()
        if count > 0:
            return format_html(
                '<span style="background: #17a2b8; color: white; padding: 2px 6px; border-radius: 10px;">📦 {}</span>',
                count
            )
        return "📦 0"
    get_items_count.short_description = "Articles"


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['get_order_info', 'get_product_info', 'get_vendor_info', 'quantity', 'get_total_price', 'created_at']
    list_filter = ['created_at', 'order__status']
    search_fields = ['order__order_number', 'product__name', 'vendor__nom', 'vendor__prenom']
    readonly_fields = ['id', 'total_price', 'created_at']
    
    fieldsets = (
        ('📦 Article de Commande', {
            'fields': ('order', 'product', 'vendor', 'quantity', 'unit_price', 'total_price')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_order_info(self, obj):
        return format_html(
            '📋 {} ({})',
            obj.order.order_number,
            obj.order.get_status_display()
        )
    get_order_info.short_description = "Commande"
    
    def get_product_info(self, obj):
        return format_html(
            '🛍️ {}',
            obj.product.name
        )
    get_product_info.short_description = "Produit"
    
    def get_vendor_info(self, obj):
        return format_html(
            '🏪 {} {} ({})',
            obj.vendor.prenom,
            obj.vendor.nom,
            obj.vendor.identifier
        )
    get_vendor_info.short_description = "Vendeur"
    
    def get_total_price(self, obj):
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold;">💰 {} FCFA</span>',
            obj.total_price
        )
    get_total_price.short_description = "Prix Total"


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['get_user_info', 'get_product_info', 'get_vendor_info', 'rating', 'get_verified_status', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['user__nom', 'user__prenom', 'product__name', 'vendor__nom', 'vendor__prenom', 'comment']
    readonly_fields = ['id', 'vendor', 'is_verified', 'created_at', 'updated_at']
    
    fieldsets = (
        ('⭐ Informations Avis', {
            'fields': ('user', 'product', 'vendor', 'order_item', 'rating', 'comment', 'is_verified')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_info(self, obj):
        return format_html(
            '👤 {} {} ({})',
            obj.user.prenom,
            obj.user.nom,
            obj.user.identifier
        )
    get_user_info.short_description = "Client"
    
    def get_product_info(self, obj):
        return format_html(
            '🛍️ {}',
            obj.product.name
        )
    get_product_info.short_description = "Produit"
    
    def get_vendor_info(self, obj):
        return format_html(
            '🏪 {} {} ({})',
            obj.vendor.prenom,
            obj.vendor.nom,
            obj.vendor.identifier
        )
    get_vendor_info.short_description = "Vendeur"
    
    def get_verified_status(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px;">✅ Vérifié</span>'
            )
        else:
            return format_html(
                '<span style="background: #ffc107; color: black; padding: 2px 8px; border-radius: 10px;">⚠️ Non vérifié</span>'
            )
    get_verified_status.short_description = "Statut"


class VendorRatingAdmin(admin.ModelAdmin):
    list_display = ['get_vendor_info', 'get_average_rating', 'total_reviews', 'get_rating_breakdown', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['vendor__nom', 'vendor__prenom', 'vendor__identifier']
    readonly_fields = ['id', 'total_reviews', 'average_rating', 'rating_1_count', 'rating_2_count', 'rating_3_count', 'rating_4_count', 'rating_5_count', 'updated_at']
    
    fieldsets = (
        ('🏪 Vendeur', {
            'fields': ('vendor',)
        }),
        ('⭐ Statistiques de Notes', {
            'fields': ('total_reviews', 'average_rating', 'rating_5_count', 'rating_4_count', 'rating_3_count', 'rating_2_count', 'rating_1_count')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_vendor_info(self, obj):
        return format_html(
            '🏪 {} {} ({})',
            obj.vendor.prenom,
            obj.vendor.nom,
            obj.vendor.identifier
        )
    get_vendor_info.short_description = "Vendeur"
    
    def get_average_rating(self, obj):
        return format_html(
            '<span style="background: #ffc107; color: black; padding: 2px 8px; border-radius: 10px; font-weight: bold;">⭐ {}</span>',
            obj.average_rating
        )
    get_average_rating.short_description = "Note Moyenne"
    
    def get_rating_breakdown(self, obj):
        return format_html(
            '5⭐:{} | 4⭐:{} | 3⭐:{} | 2⭐:{} | 1⭐:{}',
            obj.rating_5_count,
            obj.rating_4_count,
            obj.rating_3_count,
            obj.rating_2_count,
            obj.rating_1_count
        )
    get_rating_breakdown.short_description = "Répartition"


class DeliveryOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'delivery_type', 'get_price', 'get_delivery_time', 'get_status', 'created_at']
    list_filter = ['delivery_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('🚚 Informations Livraison', {
            'fields': ('name', 'delivery_type', 'price', 'estimated_days_min', 'estimated_days_max', 'description', 'is_active')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_price(self, obj):
        return format_html(
            '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold;">💰 {} FCFA</span>',
            obj.price
        )
    get_price.short_description = "Prix"
    
    def get_delivery_time(self, obj):
        return format_html(
            '<span style="background: #17a2b8; color: white; padding: 2px 8px; border-radius: 10px;">🕒 {}-{} jours</span>',
            obj.estimated_days_min,
            obj.estimated_days_max
        )
    get_delivery_time.short_description = "Délai"
    
    def get_status(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px;">✅ Actif</span>'
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 10px;">❌ Inactif</span>'
            )
    get_status.short_description = "Statut"


class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'get_order_info', 'get_delivery_option', 'get_status', 'get_delivery_dates', 'created_at']
    list_filter = ['status', 'delivery_option', 'created_at']
    search_fields = ['tracking_number', 'order__order_number']
    readonly_fields = ['id', 'tracking_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('📦 Informations Expédition', {
            'fields': ('order', 'tracking_number', 'delivery_option', 'status')
        }),
        ('🕒 Dates de Livraison', {
            'fields': ('estimated_delivery_date', 'actual_delivery_date', 'delivery_notes')
        }),
        ('📊 Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_order_info(self, obj):
        return format_html(
            '📋 {} ({})',
            obj.order.order_number,
            obj.order.get_status_display()
        )
    get_order_info.short_description = "Commande"
    
    def get_delivery_option(self, obj):
        return format_html(
            '🚚 {} - {} FCFA',
            obj.delivery_option.name,
            obj.delivery_option.price
        )
    get_delivery_option.short_description = "Option Livraison"
    
    def get_status(self, obj):
        status_colors = {
            'preparing': '#ffc107',
            'picked_up': '#17a2b8',
            'in_transit': '#6f42c1',
            'out_for_delivery': '#fd7e14',
            'delivered': '#28a745',
            'failed': '#dc3545',
            'returned': '#6c757d'
        }
        status_icons = {
            'preparing': '📦',
            'picked_up': '🚚',
            'in_transit': '🛣️',
            'out_for_delivery': '🚛',
            'delivered': '✅',
            'failed': '❌',
            'returned': '↩️'
        }
        color = status_colors.get(obj.status, '#6c757d')
        icon = status_icons.get(obj.status, '❓')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 10px;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    get_status.short_description = "Statut"
    
    def get_delivery_dates(self, obj):
        if obj.actual_delivery_date:
            return format_html(
                '✅ Livré le {}',
                obj.actual_delivery_date.strftime('%d/%m/%Y')
            )
        elif obj.estimated_delivery_date:
            return format_html(
                '📅 Prévu le {}',
                obj.estimated_delivery_date.strftime('%d/%m/%Y')
            )
        return "🕒 Date non définie"
    get_delivery_dates.short_description = "Livraison"


# Custom Admin Site Configuration
class EstuaireAdminSite(admin.AdminSite):
    site_header = "🏢 ESTUAIRE Administration"
    site_title = "ESTUAIRE Admin"
    index_title = "🚀 Bienvenue sur ESTUAIRE Administration"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('achat-dashboard/', achat_dashboard_view, name='achat_dashboard'),
        ]
        return custom_urls + urls
    
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Add dashboard stats to admin index
        extra_context.update({
            'dashboard_stats': {
                'total_users': CustomUser.objects.count(),
                'total_vendors': CustomUser.objects.filter(user_type='vendor').count(),
                'total_customers': CustomUser.objects.filter(user_type='customer').count(),
                'active_vendors': CustomUser.objects.filter(user_type='vendor', products__isnull=False).distinct().count(),
                'total_locations': Location.objects.count(),
                'active_tokens': UserToken.objects.filter(is_active=True).count(),
                'total_products': Product.objects.count(),
                'active_products': Product.objects.filter(status='active').count(),
                'total_wishlists': Wishlist.objects.count(),
                'total_notifications': Notification.objects.count(),
                'unread_notifications': Notification.objects.filter(is_read=False).count(),
            },
            'quick_links': [
                {
                    'title': '📊 Dashboard Achat',
                    'url': reverse('admin:achat_dashboard'),
                    'description': 'Voir les statistiques détaillées',
                    'icon': '📊'
                },
                {
                    'title': '👥 Gérer Utilisateurs',
                    'url': reverse('admin:achat_customuser_changelist'),
                    'description': 'Gérer tous les utilisateurs',
                    'icon': '👥'
                },
                {
                    'title': '🏪 Gérer Fournisseurs',
                    'url': reverse('admin:achat_vendorproxy_changelist'),
                    'description': 'Gérer les fournisseurs',
                    'icon': '🏪'
                },
                {
                    'title': '👤 Gérer Clients',
                    'url': reverse('admin:achat_customerproxy_changelist'),
                    'description': 'Gérer les clients',
                    'icon': '👤'
                },
                {
                    'title': '📍 Gérer Localisations',
                    'url': reverse('admin:achat_location_changelist'),
                    'description': 'Gérer les localisations',
                    'icon': '📍'
                },
                {
                    'title': '📁 Gérer Catégories',
                    'url': reverse('admin:achat_category_changelist'),
                    'description': 'Gérer les catégories',
                    'icon': '📁'
                },
                {
                    'title': '📂 Gérer Sous-catégories',
                    'url': reverse('admin:achat_subcategory_changelist'),
                    'description': 'Gérer les sous-catégories',
                    'icon': '📂'
                },
                {
                    'title': '🛍️ Gérer Produits',
                    'url': reverse('admin:achat_product_changelist'),
                    'description': 'Gérer les produits',
                    'icon': '🛍️'
                },
                {
                    'title': '🖼️ Gérer Images',
                    'url': reverse('admin:achat_productimage_changelist'),
                    'description': 'Gérer les images de produits',
                    'icon': '🖼️'
                },
                {
                    'title': '💝 Gérer Wishlists',
                    'url': reverse('admin:achat_wishlist_changelist'),
                    'description': 'Gérer les listes de souhaits',
                    'icon': '💝'
                },
                {
                    'title': '🔔 Gérer Notifications',
                    'url': reverse('admin:achat_notification_changelist'),
                    'description': 'Gérer les notifications',
                    'icon': '🔔'
                },
            ]
        })
        
        return super().index(request, extra_context)


# Create custom admin site instance
estuaire_admin_site = EstuaireAdminSite(name='estuaire_admin')

# Register models with custom admin site
# Create proxy models for admin separation
class VendorProxy(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"

class CustomerProxy(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Client"
        verbose_name_plural = "Clients"

estuaire_admin_site.register(CustomUser, CustomUserAdmin)
estuaire_admin_site.register(VendorProxy, VendorAdmin)
estuaire_admin_site.register(CustomerProxy, CustomerAdmin)
estuaire_admin_site.register(Location, LocationAdmin)
estuaire_admin_site.register(UserToken, UserTokenAdmin)
estuaire_admin_site.register(Category, CategoryAdmin)
estuaire_admin_site.register(SubCategory, SubCategoryAdmin)
estuaire_admin_site.register(Product, ProductAdmin)
estuaire_admin_site.register(ProductImage, ProductImageAdmin)
estuaire_admin_site.register(Wishlist, WishlistAdmin)
estuaire_admin_site.register(Notification, NotificationAdmin)
estuaire_admin_site.register(Cart, CartAdmin)
estuaire_admin_site.register(CartItem, CartItemAdmin)
estuaire_admin_site.register(Order, OrderAdmin)
estuaire_admin_site.register(OrderItem, OrderItemAdmin)
estuaire_admin_site.register(Review, ReviewAdmin)
estuaire_admin_site.register(VendorRating, VendorRatingAdmin)
estuaire_admin_site.register(DeliveryOption, DeliveryOptionAdmin)
estuaire_admin_site.register(Shipment, ShipmentAdmin)

# Re-register Django's built-in models with our custom admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin

estuaire_admin_site.register(Group, GroupAdmin)

# Override default admin site
admin.site = estuaire_admin_site

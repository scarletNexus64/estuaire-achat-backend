
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-pdka^!qhz943qkq45r(348+%r!ndbfyus+v-o=b6g5je$+7y%_'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    # Admin Theme (must be before django.contrib.admin)
    'jazzmin',
    
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'rest_framework',
    'drf_spectacular',

    # Apps
    'achat',
]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "achat.authentication.UUIDTokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ESTUAIRE API",
    "DESCRIPTION": "Documentation de l'API ESTUAIRE avec DRF & Spectacular",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "TAGS": [
        {
            "name": "Authentication",
            "description": "Gestion de l'authentification des utilisateurs",
        },
        {
            "name": "Products",
            "description": "Gestion des produits e-commerce",
        },
        {
            "name": "Categories",
            "description": "Gestion des catégories et sous-catégories",
        },
        {
            "name": "SubCategories", 
            "description": "Gestion des sous-catégories",
        },
        {
            "name": "Wishlists",
            "description": "Gestion des listes de souhaits des utilisateurs",
        },
        {
            "name": "Notifications",
            "description": "Gestion des notifications utilisateurs",
        },
        {
            "name": "Achat",
            "description": "Gestion générale des achats et des commandes",
        },
        # Ajoutez vos futures applications ici :
        # {
        #     "name": "Emploi", 
        #     "description": "Gestion des emplois et recrutement",
        # },
    ],
    "PREPROCESSING_HOOKS": [
        "estuaire.spectacular_hooks.custom_preprocessing_hook",
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'estuaire.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'estuaire.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'achat.CustomUser'

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'achat.authentication.CustomAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Jazzmin Configuration - Modern E-commerce Dashboard
JAZZMIN_SETTINGS = {
    # ============================================
    # 🎨 BRANDING & IDENTITY
    # ============================================
    "site_title": "💎 ESTUAIRE E-Commerce Dashboard",
    "site_header": "💎 ESTUAIRE",
    "site_brand": "💎 ESTUAIRE",
    "site_logo": None,
    "login_logo": None,
    "login_logo_dark": None,
    "site_logo_classes": "img-circle elevation-3",
    "site_icon": None,
    
    # ============================================
    # 🚀 WELCOME & BRANDING
    # ============================================
    "welcome_sign": "🚀 Bienvenue dans votre Dashboard E-Commerce",
    "copyright": "💎 ESTUAIRE E-Commerce Platform © 2024",
    
    # ============================================
    # 🔍 SEARCH & USER SETTINGS
    # ============================================
    "search_model": [
        "achat.CustomUser", 
        "achat.Product", 
        "achat.Location", 
        "achat.Category",
        "achat.SubCategory"
    ],
    "user_avatar": "photo_profile",
    
    # ============================================
    # 📋 TOP NAVIGATION MENU - COMPACT
    # ============================================
    "topmenu_links": [
        {
            "name": "Dashboard", 
            "url": "admin:index", 
            "permissions": ["auth.view_user"]
        },
        {
            "name": "Analytics", 
            "url": "admin:achat_dashboard", 
            "permissions": ["achat.view_customuser"]
        },
        {
            "name": "API", 
            "url": "/api/schema/swagger-ui/", 
            "new_window": True
        },
        {
            "app": "achat"
        },
    ],
    
    # ============================================
    # 👤 USER MENU (Top Right) - CLEAN
    # ============================================
    "usermenu_links": [
        {
            "name": "Voir le Site", 
            "url": "/", 
            "new_window": True
        },
        {
            "name": "Mon Profil", 
            "model": "achat.CustomUser"
        }
    ],
    
    # ============================================
    # 📱 SIDEBAR NAVIGATION
    # ============================================
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "achat.Product",
        "achat.Category", 
        "achat.SubCategory",
        "achat.CustomUser",
        "achat.Location",
        "achat.UserToken",
        "auth"
    ],
    
    # ============================================
    # 🔗 CUSTOM NAVIGATION LINKS
    # ============================================
    "custom_links": {
        "achat": [
            {
                "name": "📊 Dashboard Analytics", 
                "url": "admin:achat_dashboard", 
                "icon": "fas fa-chart-bar",
                "permissions": ["achat.view_customuser"]
            },
            {
                "name": "💰 Rapport Ventes", 
                "url": "admin:achat_dashboard", 
                "icon": "fas fa-money-bill-wave",
                "permissions": ["achat.view_product"]
            },
            {
                "name": "📈 Analytics Produits", 
                "url": "admin:achat_dashboard", 
                "icon": "fas fa-chart-line",
                "permissions": ["achat.view_product"]
            }
        ]
    },
    
    # ============================================
    # 🎯 MODERN ICONS (FontAwesome 6)
    # ============================================
    "icons": {
        # Core Apps
        "auth": "fas fa-shield-halved",
        "auth.user": "fas fa-user-gear", 
        "auth.User": "fas fa-user-tie",
        "auth.Group": "fas fa-users-gear",
        
        # E-commerce App Icons
        "achat": "fas fa-store",
        "achat.CustomUser": "fas fa-user-crown",
        "achat.customuser": "fas fa-user-crown",
        "achat.Customuser": "fas fa-user-crown",
        "achat.Product": "fas fa-box-open",
        "achat.product": "fas fa-box-open",
        "achat.ProductImage": "fas fa-images",
        "achat.productimage": "fas fa-images",
        "achat.Category": "fas fa-layer-group",
        "achat.category": "fas fa-layer-group",
        "achat.SubCategory": "fas fa-folder-tree",
        "achat.subcategory": "fas fa-folder-tree",
        "achat.Location": "fas fa-map-location-dot",
        "achat.location": "fas fa-map-location-dot",
        "achat.UserToken": "fas fa-key",
        "achat.usertoken": "fas fa-key",
        "achat.Wishlist": "fas fa-heart",
        "achat.wishlist": "fas fa-heart",
        "achat.Notification": "fas fa-bell",
        "achat.notification": "fas fa-bell",
        
        # Additional Django Auth Models
        "django.contrib.auth": "fas fa-shield-halved",
        "django.contrib.auth.models.User": "fas fa-user-tie",
        "django.contrib.auth.models.Group": "fas fa-users-gear",
    },
    
    # Default icon styling
    "default_icon_parents": "fas fa-angle-right",
    "default_icon_children": "fas fa-dot-circle",
    
    # ============================================
    # 🎨 UI ENHANCEMENTS
    # ============================================
    "related_modal_active": True,
    "custom_css": "admin/css/estuaire_modern.css",
    "custom_js": "admin/js/estuaire_dashboard.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,
    
    # ============================================
    # 📋 FORM LAYOUTS
    # ============================================
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "achat.CustomUser": "carousel",
        "achat.Product": "horizontal_tabs",
        "achat.Category": "collapsible",
        "achat.SubCategory": "collapsible",
        "auth.Group": "vertical_tabs"
    },
    
    # ============================================
    # 🌍 LOCALIZATION
    # ============================================
    "language_chooser": False,
}

# Modern E-commerce Dark Mode UI Design
JAZZMIN_UI_TWEAKS = {
    # ============================================
    # 📱 LAYOUT & STRUCTURE
    # ============================================
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "layout_boxed": False,
    "navbar_fixed": True,
    "footer_fixed": False,
    "sidebar_fixed": True,
    
    # ============================================
    # 🌙 DARK MODE CONFIGURATION
    # ============================================
    "theme": "slate",  # Dark theme by default
    "dark_mode_theme": None,  # No switch, always dark
    
    # Navbar & Brand Colors
    "brand_colour": "navbar-primary",
    "navbar": "navbar-primary navbar-dark",
    "no_navbar_border": True,
    
    # Sidebar Design
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    
    # Accent Colors
    "accent": "accent-primary",
    
    # ============================================
    # 🌈 PREMIUM BUTTON COLOR PALETTE
    # ============================================
    "button_colours": {
        # Primary E-commerce Colors
        "primary": "#6366F1",      # Modern Indigo
        "secondary": "#8B5CF6",    # Elegant Purple  
        "info": "#06B6D4",         # Cyan Blue
        "warning": "#F59E0B",      # Amber
        "danger": "#EF4444",       # Red
        "success": "#10B981",      # Emerald Green
        
        # Custom E-commerce Actions
        "dark": "#374151",         # Dark Gray
        "light": "#F3F4F6",       # Light Gray
    },
    
    # ============================================
    # 🎯 ADVANCED STYLING
    # ============================================
    "sidebar_nav_accordion": True,
    "sidebar_nav_animation_speed": 300,
}

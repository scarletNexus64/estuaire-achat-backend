from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

def create_spectacular_patterns(app_name, app_urls):
    """Créer les patterns Spectacular pour une application"""
    return [
        # Schéma OpenAPI spécifique à l'app
        path(f"{app_name}/schema/", SpectacularAPIView.as_view(urlconf=f"{app_name}.urls"), name=f"schema-{app_name}"),
        
        # Interfaces docs spécifiques à l'app
        path(f"{app_name}/docs/", SpectacularSwaggerView.as_view(url_name=f"schema-{app_name}"), name=f"swagger-ui-{app_name}"),
        path(f"{app_name}/redoc/", SpectacularRedocView.as_view(url_name=f"schema-{app_name}"), name=f"redoc-{app_name}"),
        
        # URLs de l'application
        path(f"{app_name}/", include(app_urls)),
    ]

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Documentation globale (toutes les apps)
    path("schema/", SpectacularAPIView.as_view(), name="global-schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="global-schema"), name="global-swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="global-schema"), name="global-redoc"),
    
    # Routes d'authentification au niveau principal
    path("", include("achat.urls")),
]

# Applications actuelles
urlpatterns.extend(create_spectacular_patterns("achat", "achat.urls"))

# Exemple pour futures applications - décommentez quand vous les ajouterez :
# urlpatterns.extend(create_spectacular_patterns("emploi", "emploi.urls"))
# urlpatterns.extend(create_spectacular_patterns("autre_app", "autre_app.urls"))

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import Location, UserToken
import json

User = get_user_model()


class AuthenticationTestCase(APITestCase):
    """Tests pour l'authentification des utilisateurs (customers et vendors)"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        
        # Données de test pour un customer
        self.customer_data = {
            'identifier': 'customer@test.com',
            'nom': 'Dupont',
            'prenom': 'Jean',
            'gender': 'M',
            'username': 'customer_test',
            'user_type': 'customer',
            'password': 'testpassword123',
            'location_name': 'Paris',
            'longitude': 2.3522,
            'latitude': 48.8566
        }
        
        # Données de test pour un vendor
        self.vendor_data = {
            'identifier': 'vendor@test.com',
            'nom': 'Martin',
            'prenom': 'Sophie',
            'gender': 'F',
            'username': 'vendor_test',
            'user_type': 'vendor',
            'password': 'testpassword123',
            'location_name': 'Lyon',
            'longitude': 4.8357,
            'latitude': 45.7640
        }

    def test_register_customer_success(self):
        """Test d'inscription réussie d'un client"""
        response = self.client.post(self.register_url, self.customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        
        # Vérifier que l'utilisateur est créé avec le bon type
        user = User.objects.get(identifier='customer@test.com')
        self.assertEqual(user.user_type, 'customer')
        self.assertEqual(user.nom, 'Dupont')
        self.assertEqual(user.prenom, 'Jean')
        
        # Vérifier que la localisation est créée
        self.assertTrue(user.locations.exists())
        location = user.locations.first()
        self.assertEqual(location.name, 'Paris')
        self.assertTrue(location.is_default)
        
        # Vérifier que le token est créé
        self.assertTrue(hasattr(user, 'auth_token'))
        self.assertTrue(user.auth_token.is_active)

    def test_register_vendor_success(self):
        """Test d'inscription réussie d'un fournisseur"""
        response = self.client.post(self.register_url, self.vendor_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        
        # Vérifier que l'utilisateur est créé avec le bon type
        user = User.objects.get(identifier='vendor@test.com')
        self.assertEqual(user.user_type, 'vendor')
        self.assertEqual(user.nom, 'Martin')
        self.assertEqual(user.prenom, 'Sophie')
        
        # Vérifier que la localisation est créée
        self.assertTrue(user.locations.exists())
        location = user.locations.first()
        self.assertEqual(location.name, 'Lyon')

    def test_register_duplicate_identifier(self):
        """Test d'inscription avec un identifier déjà existant"""
        # Créer d'abord un utilisateur
        self.client.post(self.register_url, self.customer_data, format='json')
        
        # Essayer de créer un autre utilisateur avec le même identifier
        response = self.client.post(self.register_url, self.customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('identifier', response.data)

    def test_register_missing_fields(self):
        """Test d'inscription avec des champs manquants"""
        incomplete_data = {
            'identifier': 'incomplete@test.com',
            'nom': 'Test'
            # Champs manquants: prenom, password, etc.
        }
        
        response = self.client.post(self.register_url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_customer_success(self):
        """Test de connexion réussie d'un client"""
        # D'abord créer un utilisateur
        self.client.post(self.register_url, self.customer_data, format='json')
        
        # Puis essayer de se connecter
        login_data = {
            'identifier': self.customer_data['identifier'],
            'password': self.customer_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user_type'], 'customer')

    def test_login_vendor_success(self):
        """Test de connexion réussie d'un fournisseur"""
        # D'abord créer un utilisateur vendor
        self.client.post(self.register_url, self.vendor_data, format='json')
        
        # Puis essayer de se connecter
        login_data = {
            'identifier': self.vendor_data['identifier'],
            'password': self.vendor_data['password']
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user_type'], 'vendor')

    def test_login_wrong_password(self):
        """Test de connexion avec mauvais mot de passe"""
        # Créer un utilisateur
        self.client.post(self.register_url, self.customer_data, format='json')
        
        # Essayer de se connecter avec un mauvais mot de passe
        login_data = {
            'identifier': self.customer_data['identifier'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test de connexion avec un utilisateur inexistant"""
        login_data = {
            'identifier': 'nonexistent@test.com',
            'password': 'somepassword'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_type_default_to_customer(self):
        """Test que le type d'utilisateur par défaut est 'customer'"""
        data_without_user_type = self.customer_data.copy()
        del data_without_user_type['user_type']
        
        response = self.client.post(self.register_url, data_without_user_type, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(identifier=data_without_user_type['identifier'])
        self.assertEqual(user.user_type, 'customer')

    def test_location_creation_during_registration(self):
        """Test que la localisation est correctement créée lors de l'inscription"""
        response = self.client.post(self.register_url, self.customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(identifier=self.customer_data['identifier'])
        
        # Vérifier qu'une localisation est créée
        self.assertEqual(user.locations.count(), 1)
        
        location = user.locations.first()
        self.assertEqual(location.name, self.customer_data['location_name'])
        self.assertEqual(float(location.longitude), self.customer_data['longitude'])
        self.assertEqual(float(location.latitude), self.customer_data['latitude'])
        self.assertTrue(location.is_default)

    def test_token_creation_during_registration(self):
        """Test que le token est correctement créé lors de l'inscription"""
        response = self.client.post(self.register_url, self.customer_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        user = User.objects.get(identifier=self.customer_data['identifier'])
        
        # Vérifier qu'un token est créé
        self.assertTrue(hasattr(user, 'auth_token'))
        self.assertTrue(user.auth_token.is_active)
        
        # Vérifier que le token est retourné dans la réponse
        self.assertIn('token', response.data)
        self.assertEqual(response.data['token'], str(user.auth_token.token))


class VendorProductManagementTestCase(APITestCase):
    """Tests pour la gestion des produits par les vendors"""
    
    def setUp(self):
        """Configuration initiale pour les tests de produits vendors"""
        # URLs
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.products_url = reverse('product-list')
        
        # Créer des catégories et sous-catégories pour les tests
        from ..models import Category, SubCategory
        self.category = Category.objects.create(
            name='Électronique',
            name_trl='Electronics',
            description='Produits électroniques'
        )
        self.subcategory = SubCategory.objects.create(
            name='Smartphones',
            name_trl='Smartphones',
            description='Téléphones intelligents'
        )
        self.category.subcategories.add(self.subcategory)
        
        # Créer un vendor
        self.vendor_data = {
            'identifier': 'vendor@test.com',
            'nom': 'Martin',
            'prenom': 'Sophie',
            'gender': 'F',
            'username': 'vendor_test',
            'user_type': 'vendor',
            'password': 'testpassword123',
            'location_name': 'Lyon',
            'longitude': 4.8357,
            'latitude': 45.7640
        }
        
        # Enregistrer et connecter le vendor
        response = self.client.post(self.register_url, self.vendor_data, format='json')
        self.vendor_user = User.objects.get(identifier='vendor@test.com')
        self.vendor_token = response.data['token']
        self.vendor_location = self.vendor_user.locations.first()
        
        # Créer un customer pour tester l'isolation
        self.customer_data = {
            'identifier': 'customer@test.com',
            'nom': 'Dupont',
            'prenom': 'Jean',
            'gender': 'M',
            'username': 'customer_test',
            'user_type': 'customer',
            'password': 'testpassword123',
            'location_name': 'Paris',
            'longitude': 2.3522,
            'latitude': 48.8566
        }
        
        response = self.client.post(self.register_url, self.customer_data, format='json')
        self.customer_user = User.objects.get(identifier='customer@test.com')
        self.customer_token = response.data['token']
        self.customer_location = self.customer_user.locations.first()

    def test_vendor_can_publish_product(self):
        """Test qu'un vendor peut publier un produit"""
        # S'authentifier en tant que vendor
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        
        product_data = {
            'name': 'iPhone 14 Pro',
            'price': 1299.99,
            'location': str(self.vendor_location.id),
            'quantity': 5,
            'is_stock': True,
            'status': 'active',
            'description': 'Nouveau iPhone 14 Pro en excellent état',
            'conditions_paiement': 'mobile',
            'category': str(self.category.id),
            'subcategory': str(self.subcategory.id)
        }
        
        response = self.client.post(self.products_url, product_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        
        # Vérifier que le produit est créé avec le bon vendor
        from ..models import Product
        product = Product.objects.get(id=response.data['id'])
        self.assertEqual(product.user, self.vendor_user)
        self.assertEqual(product.name, 'iPhone 14 Pro')
        self.assertEqual(float(product.price), 1299.99)

    def test_vendor_can_update_own_product(self):
        """Test qu'un vendor peut modifier ses propres produits"""
        # Créer un produit en tant que vendor
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        
        product_data = {
            'name': 'MacBook Pro',
            'price': 2499.99,
            'location': str(self.vendor_location.id),
            'quantity': 3,
            'is_stock': True,
            'status': 'active',
            'description': 'MacBook Pro M2 neuf',
            'conditions_paiement': 'transfer'
        }
        
        response = self.client.post(self.products_url, product_data, format='json')
        product_id = response.data['id']
        
        # Modifier le produit
        update_data = {
            'name': 'MacBook Pro M2 - PROMOTION',
            'price': 2199.99,
            'quantity': 2,
            'description': 'MacBook Pro M2 neuf - Prix réduit!',
            'status': 'active'
        }
        
        response = self.client.patch(f'{self.products_url}{product_id}/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'MacBook Pro M2 - PROMOTION')
        self.assertEqual(float(response.data['price']), 2199.99)

    def test_vendor_can_delete_own_product(self):
        """Test qu'un vendor peut supprimer ses propres produits"""
        # Créer un produit en tant que vendor
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        
        product_data = {
            'name': 'iPad Air',
            'price': 799.99,
            'location': str(self.vendor_location.id),
            'quantity': 2,
            'is_stock': True,
            'status': 'active',
            'description': 'iPad Air dernière génération'
        }
        
        response = self.client.post(self.products_url, product_data, format='json')
        product_id = response.data['id']
        
        # Supprimer le produit
        response = self.client.delete(f'{self.products_url}{product_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Vérifier que le produit est supprimé
        from ..models import Product
        self.assertFalse(Product.objects.filter(id=product_id).exists())

    def test_vendor_cannot_modify_other_vendor_product(self):
        """Test qu'un vendor ne peut pas modifier les produits d'un autre vendor"""
        # Créer un autre vendor
        other_vendor_data = {
            'identifier': 'vendor2@test.com',
            'nom': 'Bernard',
            'prenom': 'Claire',
            'gender': 'F',
            'username': 'vendor2_test',
            'user_type': 'vendor',
            'password': 'testpassword123',
            'location_name': 'Marseille',
            'longitude': 5.3698,
            'latitude': 43.2965
        }
        
        response = self.client.post(self.register_url, other_vendor_data, format='json')
        other_vendor_token = response.data['token']
        other_vendor_user = User.objects.get(identifier='vendor2@test.com')
        other_vendor_location = other_vendor_user.locations.first()
        
        # Créer un produit avec l'autre vendor
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_vendor_token}')
        
        product_data = {
            'name': 'Samsung Galaxy S23',
            'price': 999.99,
            'location': str(other_vendor_location.id),
            'quantity': 4,
            'is_stock': True,
            'status': 'active'
        }
        
        response = self.client.post(self.products_url, product_data, format='json')
        product_id = response.data['id']
        
        # Essayer de modifier avec le premier vendor
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        
        update_data = {
            'name': 'Samsung Galaxy S23 - HACK ATTEMPT',
            'price': 1.00
        }
        
        response = self.client.patch(f'{self.products_url}{product_id}/', update_data, format='json')
        
        # Doit être refusé (403 ou 404 selon l'implémentation)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])

    def test_customer_can_publish_product(self):
        """Test qu'un customer peut publier un produit"""
        # S'authentifier en tant que customer
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.customer_token}')
        
        product_data = {
            'name': 'Produit customer',
            'price': 100.00,
            'location': str(self.customer_location.id),
            'quantity': 1,
            'is_stock': True,
            'status': 'active'
        }
        
        response = self.client.post(self.products_url, product_data, format='json')
        
        # Tous les utilisateurs authentifiés peuvent créer des produits
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        
        # Vérifier que le produit est créé avec le bon customer
        from ..models import Product
        product = Product.objects.get(id=response.data['id'])
        self.assertEqual(product.user, self.customer_user)

    def test_vendor_can_manage_product_stock(self):
        """Test qu'un vendor peut gérer le stock de ses produits"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        
        product_data = {
            'name': 'Nintendo Switch',
            'price': 349.99,
            'location': str(self.vendor_location.id),
            'quantity': 10,
            'is_stock': True,
            'status': 'active'
        }
        
        response = self.client.post(self.products_url, product_data, format='json')
        product_id = response.data['id']
        
        # Mettre à jour le stock
        stock_update = {
            'quantity': 5,
            'is_stock': True
        }
        
        response = self.client.patch(f'{self.products_url}{product_id}/', stock_update, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 5)
        self.assertTrue(response.data['is_stock'])
        
        # Marquer comme en rupture de stock
        stock_out = {
            'quantity': 0,
            'is_stock': False,
            'status': 'inactive'
        }
        
        response = self.client.patch(f'{self.products_url}{product_id}/', stock_out, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], 0)
        self.assertFalse(response.data['is_stock'])
        self.assertEqual(response.data['status'], 'inactive')

    def test_vendor_can_get_own_products(self):
        """Test qu'un vendor peut récupérer ses propres produits"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.vendor_token}')
        
        # Créer plusieurs produits
        products_data = [
            {
                'name': 'Produit 1',
                'price': 100.00,
                'location': str(self.vendor_location.id),
                'quantity': 1
            },
            {
                'name': 'Produit 2',
                'price': 200.00,
                'location': str(self.vendor_location.id),
                'quantity': 2
            }
        ]
        
        for product_data in products_data:
            self.client.post(self.products_url, product_data, format='json')
        
        # Récupérer les produits du vendor
        response = self.client.get(f'{self.products_url}by-user/{str(self.vendor_user.id)}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Vérifier que tous les produits appartiennent au vendor
        for product in response.data:
            self.assertEqual(product['user_details']['id'], str(self.vendor_user.id))

    def test_vendor_product_requires_authentication(self):
        """Test que la gestion des produits nécessite une authentification"""
        # Essayer de créer un produit sans authentification
        product_data = {
            'name': 'Produit non autorisé',
            'price': 100.00,
            'location': str(self.vendor_location.id),
            'quantity': 1
        }
        
        response = self.client.post(self.products_url, product_data, format='json')
        
        # Doit être refusé
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

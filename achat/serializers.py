from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from .models import Location, UserToken, Category, SubCategory, Product, ProductImage, Wishlist, Notification

User = get_user_model()


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'longitude', 'latitude', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'identifier', 'nom', 'prenom', 'photo_profile', 
            'gender', 'username', 'birthday', 'user_type', 'locations', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegisterSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=255)
    nom = serializers.CharField(max_length=100)
    prenom = serializers.CharField(max_length=100)
    photo_profile = serializers.ImageField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=[('M', 'Masculin'), ('F', 'Féminin'), ('O', 'Autre')])
    username = serializers.CharField(max_length=150)
    birthday = serializers.DateField(required=False)
    user_type = serializers.ChoiceField(choices=[('customer', 'Client'), ('vendor', 'Fournisseur')], default='customer')
    password = serializers.CharField(write_only=True)
    
    # Location fields
    location_name = serializers.CharField(max_length=255)
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()

    def validate_identifier(self, value):
        if User.objects.filter(identifier=value).exists():
            raise serializers.ValidationError("Cet identifier existe déjà.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur existe déjà.")
        return value

    def create(self, validated_data):
        # Extraire les données de localisation
        location_data = {
            'name': validated_data.pop('location_name'),
            'longitude': validated_data.pop('longitude'),
            'latitude': validated_data.pop('latitude'),
            'is_default': True
        }
        
        # Créer l'utilisateur
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Créer la localisation
        Location.objects.create(user=user, **location_data)
        
        # Créer le token
        UserToken.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserResponseSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)
    token = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'identifier', 'nom', 'prenom', 'photo_profile', 
            'gender', 'username', 'birthday', 'user_type', 'locations', 'token'
        ]
    
    @extend_schema_field(serializers.CharField)
    def get_token(self, obj):
        try:
            return str(obj.auth_token.token)
        except:
            return None


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = [
            'id', 'name', 'name_trl', 'description', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        if SubCategory.objects.filter(name__iexact=value).exists():
            if self.instance is None or self.instance.name.lower() != value.lower():
                raise serializers.ValidationError("Une sous-catégorie avec ce nom existe déjà.")
        return value


class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    subcategory_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs des sous-catégories à associer"
    )
    subcategories_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'name_trl', 'description', 'is_active',
            'subcategories', 'subcategory_ids', 'subcategories_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'subcategories_count']

    def validate_name(self, value):
        if Category.objects.filter(name__iexact=value).exists():
            if self.instance is None or self.instance.name.lower() != value.lower():
                raise serializers.ValidationError("Une catégorie avec ce nom existe déjà.")
        return value

    @extend_schema_field(serializers.IntegerField)
    def get_subcategories_count(self, obj):
        return obj.subcategories.count()

    def create(self, validated_data):
        subcategory_ids = validated_data.pop('subcategory_ids', [])
        category = Category.objects.create(**validated_data)
        
        if subcategory_ids:
            subcategories = SubCategory.objects.filter(id__in=subcategory_ids)
            category.subcategories.set(subcategories)
        
        return category

    def update(self, instance, validated_data):
        subcategory_ids = validated_data.pop('subcategory_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if subcategory_ids is not None:
            subcategories = SubCategory.objects.filter(id__in=subcategory_ids)
            instance.subcategories.set(subcategories)
        
        return instance


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Liste des fichiers d'images à télécharger"
    )
    user_details = UserSerializer(source='user', read_only=True)
    location_details = LocationSerializer(source='location', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    subcategory_details = SubCategorySerializer(source='subcategory', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'location', 'user', 'quantity', 'is_stock',
            'images', 'image_files', 'status', 'description', 'conditions_paiement',
            'category', 'subcategory', 'created_at', 'updated_at',
            'user_details', 'location_details', 'category_details', 'subcategory_details'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        user = self.context['request'].user
        validated_data['user'] = user
        
        product = Product.objects.create(**validated_data)
        
        for image_file in image_files:
            product_image = ProductImage.objects.create(image=image_file)
            product.images.add(product_image)
        
        return product

    def update(self, instance, validated_data):
        image_files = validated_data.pop('image_files', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if image_files is not None:
            for image_file in image_files:
                product_image = ProductImage.objects.create(image=image_file)
                instance.images.add(product_image)
        
        return instance


class WishlistSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = Wishlist
        fields = [
            'id', 'user', 'product', 'created_at', 'updated_at',
            'user_details', 'product_details'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return Wishlist.objects.create(**validated_data)

    def validate(self, data):
        user = self.context['request'].user
        product = data.get('product')
        
        # Vérifier si le produit est déjà dans la wishlist de l'utilisateur
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError(
                "Ce produit est déjà dans votre liste de souhaits."
            )
        
        return data


class NotificationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'titre', 'content', 'is_read', 
            'created_at', 'updated_at', 'user_details'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

    def create(self, validated_data):
        user = self.context.get('user') or self.context['request'].user
        validated_data['user'] = user
        return Notification.objects.create(**validated_data)
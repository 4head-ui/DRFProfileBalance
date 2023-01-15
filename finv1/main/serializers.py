from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from .models import Amounttake,Category,FinUser


class AtSerializer(serializers.ModelSerializer):

    class Meta:
        model = Amounttake
        fields = (
                  'amount',
                  'amount_date',
                  'company',
                  'description',)
        read_only_fields = ['amount_date',]


class NBSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amounttake
        fields = (
                  'amount',
                  'amount_date',
                  'company',
                  'description',
                  'user',)
        read_only_fields = ['amount_date',]


class CASerializer(serializers.ModelSerializer):
    company = serializers.CharField(max_length=20,default='Мой перевод')

    class Meta:
        model = Amounttake
        fields = (
                  'amount',
                  'amount_date',
                  'description',
                  'company',
                  'name_of_category',)
        read_only_fields = ['amount_date','company']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category_name','category_amount','user')



        read_only_fields = ['category_amount','user']


class FUSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinUser
        fields = ('id','username','account_balance','first_name','last_name')

        read_only_fields = ['account_balance', ]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        label="Username",
        write_only=True,
    )

    password = serializers.CharField(
        label="Password",
        # This will be used when the DRF browsable API is enabled
        style={'input_type': 'password'},
        write_only=True,
    )
    """
    This serializer defines two fields for authentication:
      * username
      * password.
    It will try to authenticate the user with when validated.
    """
    class Meta:
        model = FinUser
        fields = ('username','password')

    def validate(self, attrs):
        # Take username and password from request
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            # Try to authenticate the user using Django auth framework.
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                # If we don't have a regular user, raise a ValidationError
                msg = 'Access denied: wrong username or password.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Both "username" and "password" are required.'
            raise serializers.ValidationError(msg, code='authorization')
        # We have a valid user, put it in the serializer's validated_data.
        # It will be used in the view.
        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=FinUser.objects.all())]
        )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = FinUser
        fields = ('username', 'password', 'password2',
                    'email', 'first_name', 'last_name')
        extra_kwargs = {
                        'first_name': {'required': True},
                        'last_name': {'required': True}
    }
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                            {"password": "Password fields didn't match."})
        return attrs
    def create(self, validated_data):
        user = FinUser.objects.create(
                                    username=validated_data['username'],
                                    email=validated_data['email'],
                                    first_name=validated_data['first_name'],
                                    last_name=validated_data['last_name']
            )
        user.set_password(validated_data['password'])
        user.save()
        return user
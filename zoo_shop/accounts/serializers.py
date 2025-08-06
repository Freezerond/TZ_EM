from rest_framework import serializers
from .models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_repeat = serializers.CharField(write_only=True)

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Пользователь с таким email уже зарегистрирован."
            )
        ]
    )

    class Meta:
        model = User
        fields = ['email', 'name', 'patronymic', 'surname', 'password', 'password_repeat']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_repeat']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_repeat')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                raise serializers.ValidationError('Неверный email или пароль.')

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Email и пароль обязательны.')


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'name', 'patronymic', 'surname']
        extra_kwargs = {
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'Это поле обязательно к заполнению.'
                }
            },
            'name': {
                'required': True,
                'error_messages': {
                    'required': 'Это поле обязательно к заполнению.'
                }
            },
            'surname': {
                'required': True,
                'error_messages': {
                    'required': 'Это поле обязательно к заполнению.'
                }
            },
            'patronymic': {
                'required': True,
                'error_messages': {
                    'required': 'Это поле обязательно к заполнению.'
                }
            },
        }

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже используется другим пользователем.")
        return value


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'patronymic', 'surname', 'role', 'is_active']
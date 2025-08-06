from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .serializers import *
from .utils import jwt_pair_for_user
from .permissions import *


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = jwt_pair_for_user(user)

            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "patronymic": user.patronymic,
                    "surname": user.surname,
                    "role": user.role
                },
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"]
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = jwt_pair_for_user(user)

            return Response({
                'access_token': tokens['access'],
                'refresh_token': tokens['refresh'],
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"detail": "Вы успешно вышли из аккаунта."}, status=status.HTTP_200_OK)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserUpdateSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=False,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"detail": "Аккаунт успешно деактивирован."}, status=status.HTTP_204_NO_CONTENT)


class UserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PromoteToManagerView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({'error': 'user_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        if user.role == 'manager':
            return Response({'message': 'Пользователь уже является менеджером'}, status=status.HTTP_400_BAD_REQUEST)

        user.role = 'manager'
        user.save()

        return Response({'message': f'Пользователь {user.email} назначен менеджером'}, status=status.HTTP_200_OK)


class ProductListView(APIView):
    """Просмотр товаров доступен всем"""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'products': ['Корм', 'Игрушка', 'Когтеточка']})


class OrderCreateView(APIView):
    """Только клиенты могут делать заказы"""
    permission_classes = [IsAuthenticated, IsClient]

    def post(self, request):
        return Response({'message': 'Заказ создан!'}, status=status.HTTP_201_CREATED)


class ProductManageView(APIView):
    """Менеджер и админ могут добавлять и редактировать товар"""
    permission_classes = [IsManager or IsAdmin]

    def post(self, request):
        return Response({'message': 'Товар добавлен'}, status=status.HTTP_201_CREATED)

    def put(self, request):
        return Response({'message': 'Товар обновлен'}, status=status.HTTP_200_OK)


class AdminManageUsersView(APIView):
    """Админ может деактивировать пользователей"""
    permission_classes = [IsAdmin]

    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        if not user.is_active:
            return Response(
                {"detail": "Пользователь уже деактивирован."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.role == 'admin':
            return Response(
                {"detail": "Нельзя деактивировать другого администратора."},
                status=status.HTTP_403_FORBIDDEN
            )

        user.is_active = False
        user.save()

        return Response(
            {"detail": f"Пользователь {user.email} успешно деактивирован."},
            status=status.HTTP_200_OK
        )
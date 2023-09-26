from .models import Category, MenuItem
from .serializers import *
from rest_framework import generics
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
import datetime
# Create your views here.


class IsManager(BasePermission):
    def has_permission(self, request, view):
        is_manager = request.user.groups.filter(name='Manager').exists()
        permission_classes = [IsAuthenticated]
        return is_manager, permission_classes


class category_detail(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuItemsView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price', 'category']
    filterset_fields = ['price', 'category']
    search_fields = ['title', 'category__title']

    def post(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'New Item Created!'})
        else:
            raise PermissionDenied()


class SingleItemView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def put(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Item has been updated!'})
        else:
            raise PermissionDenied()

    def delete(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists()
            instance = self.get_object()
            instance.delete()
            return Response({'message': 'Item has been deleted'})
        else:
            raise PermissionDenied()


class ManagersView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(groups__name='Manager')

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            manager_group = Group.objects.get(name="Manager")
            manager_group.user_set.add(user)
            return Response({"message": "User has been added to the Manager Group"}, status=status.HTTP_201_CREATED)

        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


class ManagerRemoveView(generics.RetrieveDestroyAPIView):
    throttle_classes = [UserRateThrottle,AnonRateThrottle]
    permission_classes = [IsManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(groups__name='Manager')

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('pk')
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            manager_group = Group.objects.get(name="Manager")
            manager_group.user_set.remove(user)
            return Response({"message": "User has been removed from the Managers group"})

        return Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)


class DeliveryCrewView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(groups__name='Delivery Crew')

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_group = Group.objects.get(name='Delivery Crew')
            delivery_group.user_set.add(user)
            return Response(
                {"message": "User has been added to the Delivery Crew group!"},
                status=status.HTTP_201_CREATED
            )

        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)


class DeliveryCrewRemoveView(generics.RetrieveDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsManager]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(groups__name='Delivery Crew')

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('pk')
        if user_id:
            user = get_object_or_404(User, pk=user_id)
            delivery_group = Group.objects.get(name="Delivery Crew")
            delivery_group.user_set.remove(user)
            return Response(
                {"message": "User has been removed from the Delivery Crew group!"},
                status=status.HTTP_204_NO_CONTENT,
            )

        return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)



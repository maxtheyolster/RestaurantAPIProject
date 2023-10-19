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
from django.shortcuts import render
from rest_framework.views import APIView
# Create your views here.


class IsManager(BasePermission):
    def has_permission(self, request, view):
        is_manager = request.user.groups.filter(name='Manager').exists()
        return is_manager and IsAuthenticated


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
        if request.user.groups.filter(name="Manager").exists():
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


class CartView(generics.ListCreateAPIView, generics.DestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.all().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        menu_item_id = serializer.validated_data['menuitem'].id
        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
        except MenuItem.DoesNotExist:
            return Response("Invalid menu item ID.", status=status.HTTP_400_BAD_REQUEST)

        unit_price = serializer.validated_data['unit_price']
        quantity = serializer.validated_data['quantity']
        price = unit_price * quantity

        cart = Cart(
            user=request.user,
            menuitem=menu_item,
            unit_price=unit_price,
            quantity=quantity,
            price=price,
        )
        cart.save()

        return Response({'cart_id': cart.id, 'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user_cart = Cart.objects.filter(user=request.user)
        if not user_cart.exists():
            return Response("Cart does not exist.", status=status.HTTP_404_NOT_FOUND)

        user_cart.delete()
        return Response("All items in the cart have been deleted.", status=status.HTTP_204_NO_CONTENT)


class OrdersView(generics.ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.groups.filter(name='Manager').exists():
            queryset = self.queryset.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            queryset = self.queryset.filter(delivery_crew=user)
        else:
            queryset = self.queryset.filter(user=user)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = Cart.objects.filter(user=user)

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                total=0,
                date=datetime.date.today()
            )

            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.price,
                )

            order.total = sum(item.price for item in order.orderitem_set.all())
            order.save()
            cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderIdView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated, (IsAdminUser | IsManager)]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    ordering_fields = ['id', 'delivery_crew', 'date', 'order_status']
    filterset_fields = ['id', 'delivery_crew', 'date', 'order_status']
    search_fields = ['id', 'delivery_crew', 'date', 'order_status']

    def retrieve(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response("Order not found.", status=status.HTTP_404_NOT_FOUND)

        if order.user != request.user:
            return Response("You do not have authorization to access this order")

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        try:
            order = Order.ojects.get(id=order_id)
        except Order.DoesNotExist:
            return Response("Order not found", status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.groups.filter(name="Manager").exists():
            serializer = self.get_serializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif user.groups.filter(name="Delivery Crew").exists():
            order_status = request.data.get('order_status')
            if status in [0, 1]:
                order.status = status
                order.save()
                serializer = self.get_serializer(order)
                return Response(serializer.data)
            return Response(
                "Invalid status value. It should be 0 for not delivered and 1 for delivered.",
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response("You do not have authorization to update this order!", status=status.HTTP_403_FORBIDDEN)


class OrderItemsView(generics.ListAPIView, generics.UpdateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        order_id = self.kwargs.get('pk')
        try:
            queryset = OrderItem.objects.filter(order=order_id)
        except Order.DoesNotExist:
            return Response("Order not found.", status=status.HTTP_404_NOT_FOUND)
        return queryset


class HomePageView(APIView):
    def get(self, request):
        return render(request, 'home.html')


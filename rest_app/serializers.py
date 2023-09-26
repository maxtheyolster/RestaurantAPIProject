from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        field = ['id', 'title', 'price', 'featured']
        depth = 1


class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    unit_price = serializers.DecimalField(decimal_places=2, max_digits=6, default=0.0)
    price = serializers.DecimalField(decimal_places=2, max_digits=6, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True,
    )
    delivery_crew = serializers.PrimaryKeyRelatedField(queryset=User.objects.none())
    order_items = OrderItemSerializer(many=True, read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        delivery_crew_group = Group.objects.get(name='Delivery Crew')
        delivery_crew_users = delivery_crew_group.user_set.all()
        self.fields['delivery_crew'].queryset = delivery_crew_users

    class Meta:
        model = Order
        fields = ['id', ' user', 'delivery_crew', 'status', 'total', 'date', 'order_items']


class UserSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField()
    password = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']

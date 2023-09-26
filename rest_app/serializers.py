from rest_framework import serializers
from .models import MenuItem, Category
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

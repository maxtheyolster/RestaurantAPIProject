from .models import Category, MenuItem
from .serializers import MenuItemSerializer, CategorySerializer
from rest_framework import generics


# Create your views here.


class MenuItemsView(generics.ListCreateAPIView):
    pass


class SingleItemView(generics.RetrieveUpdateDestroyAPIView):
    pass
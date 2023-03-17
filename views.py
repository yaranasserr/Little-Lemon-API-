# from django.shortcuts import render
from posixpath import isabs
from .models import MenuItem, Category, Cart, Order, OrderItem
from rest_framework import generics, status
from .serializers import MenuItemSerializer, CategorySerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User, Group
from datetime import date
from django.db.models import Sum

# Create your views here.
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price']
    filterset_fields = ['price']
    search_fields = ['title']
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

# class SecretView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, format=None):
#         return Response({"message": "Some secret message"})

class ManagerView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        if request.user.groups.filter(name='Manager').exists():
            return Response({"message": "Only Manager Should see this."})
        else:
            return Response({"Message:" "You are not authorized."}, 403)

class ManagersView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request, format=None):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)
            return Response({"message": "ok, the Manager has been added"})
        return Response({"message": "error"}, status.HTTP_404_BAD_REQUEST)

class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            cart_item = serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        id = kwargs.get('id')

        try:
            cart_item = Cart.objects.get(id=id, user=request.user)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cart.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

#new OrderView:
class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = Order.objects.create(
            user=self.request.user,
            status=False,
            total=0,
            date=date.today()
        )
        serializer.save(order=order)

#new orderItemView
class OrderItemView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)

    def perform_create(self, serializer):
        order = Order.objects.filter(user=self.request.user, status=False).first()
        if not order:
            order = Order.objects.create(user=self.request.user, status=False, total=0, date=date.today())

        menuitem = serializer.validated_data['menuitem']
        quantity = serializer.validated_data['quantity']
        unit_price = menuitem.price
        price = unit_price * quantity
        serializer.save(order=order, unit_price=unit_price, price=price)

        # Update order total
        order.total = OrderItem.objects.filter(order=order).aggregate(Sum('price'))['price__sum']
        order.save()



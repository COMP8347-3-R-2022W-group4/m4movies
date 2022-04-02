from django.contrib import admin
from django.db import models
from .models import Type, Item, Client, OrderItem

# Register your models here.
admin.site.register(Type)
admin.site.register(Item)
admin.site.register(Client)
admin.site.register(OrderItem)


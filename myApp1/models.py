from django.db import models
import datetime
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.

class Type(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        details = "{} (type)"
        return details.format(self.name)


class Item(models.Model):
    type = models.ForeignKey(Type, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=100)
    available = models.BooleanField(default=True)
    product_description = models.TextField(blank=True)

    def __str__(self):
        details = "{} (item)"
        return details.format(self.name)


class Client(User):
    CITY_CHOICES = [('WD', 'Windsor'), ('TO', 'Toronto'), ('CH', 'Chatham'), ('WL', 'Waterloo')]
    # fullname = models.CharField(max_length=50)
    shipping_address = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=2, choices=CITY_CHOICES, default='CH')
    interested_in = models.ManyToManyField(Type)
    phone_no = models.CharField(null=True, max_length=30)  # ^(\+\d{1,3})?,?\s?\d{8,13} regex for phone number

    def __str__(self):
        details = "Client: {}"
        return details.format(self.first_name)


class OrderItem(models.Model):
    item = models.ForeignKey(Item, related_name='order_items', on_delete=models.CASCADE)
    client = models.ForeignKey(Client, related_name='order_clients', on_delete=models.CASCADE)
    no_of_items = models.PositiveIntegerField(default=0)
    STATUS_CHOICES = [('0', 'cancelled'), ('1', 'placed'), ('2', 'shipped'), ('3', 'delivered')]
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='0')
    last_updated = models.DateField()

    def __str__(self):
        order_details = "Order for client from city {} having {} count of item {} with status {}"
        return order_details.format(self.client.city, self.item.name, self.no_of_items, self.status)

    def total_price(self):
        return self.item.price * self.no_of_items


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    profile_pic = models.ImageField(default="profile1.png", null=True, blank=True)

    # date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

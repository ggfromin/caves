from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    has_server_access = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, related_name='residents')
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="cave_user_set",
        related_query_name="cave_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="cave_user_set",
        related_query_name="cave_user",
    )
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']
    
    def __str__(self):
        return self.username

class City(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='cities/', null=True, blank=True)
    population = models.IntegerField(default=0)
    mayor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cities_managed')
    founded_date = models.DateField(default=timezone.now)
    coordinates = models.CharField(max_length=100, help_text="X, Z координаты в Minecraft")
    is_capital = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class MarketplaceItem(models.Model):
    ITEM_TYPES = [
        ('block', 'Блок'),
        ('tool', 'Инструмент'),
        ('armor', 'Броня'),
        ('food', 'Еда'),
        ('potion', 'Зелье'),
        ('other', 'Другое'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items_for_sale')
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='marketplace/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.price}"

class Purchase(models.Model):
    item = models.ForeignKey(MarketplaceItem, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.buyer.username} купил {self.item.title}"

class Comment(models.Model):
    item = models.ForeignKey(MarketplaceItem, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Комментарий от {self.author.username} к {self.item.title}"
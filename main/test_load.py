import pytest
import requests
from django.urls import reverse
from django.contrib.auth import get_user_model
from main.models import MarketplaceItem
import pytest
from main.models import MarketplaceItem
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_create_item():
    user = User.objects.create_user(username='seller', password='12345', email='s@test.com', phone='123')
    item = MarketplaceItem.objects.create(
        title="Блок",
        description="Описание",
        price=100,
        item_type="block",
        seller=user
    )
    assert item.title == "Блок"

User = get_user_model()

BASE_URL = "http://127.0.0.1:8000" 

@pytest.mark.django_db
def test_marketplace_load(benchmark):
    user = User.objects.create_user(username='seller', password='12345', email='s@test.com', phone='123')
    MarketplaceItem.objects.create(
        title="Тестовый блок",
        description="Описание",
        price=100,
        item_type="block",
        seller=user
    )

    def load_marketplace():
        response = requests.get(f"{BASE_URL}/marketplace/")
        assert response.status_code == 200

    benchmark(load_marketplace)
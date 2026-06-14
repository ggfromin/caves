from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import User, City, MarketplaceItem, Purchase, Comment
from .forms import RegistrationForm, LoginForm, MarketplaceItemForm, CommentForm, ProfileForm

def index(request):
    cities = City.objects.all()[:6]  
    return render(request, 'main/index.html', {'cities': cities})

@login_required
def buy_server_access(request):
    """Покупка доступа на сервер"""
    ACCESS_PRICE = 500
    
    if request.user.has_server_access:
        messages.warning(request, 'У вас уже есть доступ на сервер!')
        return redirect('index')

    if request.user.balance >= ACCESS_PRICE:
        request.user.balance -= ACCESS_PRICE
        request.user.has_server_access = True
        request.user.save()
        
        messages.success(request, f'Вы купили доступ на сервер. Теперь вы можете заходить на наш сервер!')
        
        
    else:
        messages.error(request, f'Недостаточно средств! Вам не хватает {ACCESS_PRICE - request.user.balance}. Пополните баланс на торговой площадке.')
    
    return redirect('index')

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('index')
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            
            user = None
            if '@' in identifier:
                try:
                    user = User.objects.get(email=identifier)
                except User.DoesNotExist:
                    pass
            elif identifier.isdigit():
                try:
                    user = User.objects.get(phone=identifier)
                except User.DoesNotExist:
                    pass
            else:
                try:
                    user = User.objects.get(username=identifier)
                except User.DoesNotExist:
                    pass
            
            if user and user.check_password(password):
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('index')
            else:
                messages.error(request, 'Неверные учетные данные')
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта')
    return redirect('index')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлен!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    purchases = Purchase.objects.filter(buyer=request.user).select_related('item', 'item__seller')
    return render(request, 'main/profile.html', {'form': form, 'purchases': purchases})

def marketplace(request):
    items = MarketplaceItem.objects.filter(is_available=True).order_by('-created_at')
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = MarketplaceItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.seller = request.user
            item.save()
            messages.success(request, 'Товар успешно добавлен!')
            return redirect('marketplace')
    else:
        form = MarketplaceItemForm()
    
    return render(request, 'main/marketplace.html', {'items': items, 'form': form})

@login_required
def buy_item(request, item_id):
    item = get_object_or_404(MarketplaceItem, id=item_id, is_available=True)
    
    if item.seller == request.user:
        messages.error(request, 'Нельзя купить свой собственный товар')
        return redirect('marketplace')
    
    if request.user.balance >= item.price:
        request.user.balance -= item.price
        request.user.save()
        
        item.seller.balance += item.price
        item.seller.save()
        
        Purchase.objects.create(
            item=item,
            buyer=request.user,
            price_paid=item.price
        )
        
        item.is_available = False
        item.save()
        
        messages.success(request, f'Вы купили {item.title} за {item.price}!')
    else:
        messages.error(request, 'Недостаточно средств!')
    
    return redirect('marketplace')

@login_required
def add_comment(request, item_id):
    item = get_object_or_404(MarketplaceItem, id=item_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.item = item
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
    
    return redirect('marketplace')

def cities(request):
    all_cities = City.objects.all()
    return render(request, 'main/cities.html', {'cities': all_cities})

def city_detail(request, city_id):
    city = get_object_or_404(City, id=city_id)
    residents = User.objects.filter(city=city)
    city.population = residents.count()
    city.save()
    
    return render(request, 'main/city_detail.html', {'city': city, 'residents': residents})

@login_required
def join_city(request, city_id):
    city = get_object_or_404(City, id=city_id)
    if request.user.city:
        messages.warning(request, f'Вы уже живёте в городе {request.user.city.name}. Сначала покиньте его.')
        return redirect('city_detail', city_id=city_id)
    
    request.user.city = city
    request.user.save()
    
    city.population = User.objects.filter(city=city).count()
    city.save()
    
    messages.success(request, f'Добро пожаловать в город {city.name}!')
    return redirect('city_detail', city_id=city_id)

@login_required
def leave_city(request, city_id):
    city = get_object_or_404(City, id=city_id)
    
    if request.user.city != city:
        messages.error(request, 'Вы не живёте в этом городе')
        return redirect('city_detail', city_id=city_id)
    
    request.user.city = None
    request.user.save()
    
    city.population = User.objects.filter(city=city).count()
    city.save()
    
    messages.success(request, f'Вы покинули город {city.name}')
    return redirect('city_detail', city_id=city_id)


def item_detail(request, item_id):
    item = get_object_or_404(MarketplaceItem, id=item_id)
    comment_form = CommentForm()
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.item = item
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('item_detail', item_id=item.id)
    
    return render(request, 'main/item_detail.html', {'item': item, 'comment_form': comment_form})
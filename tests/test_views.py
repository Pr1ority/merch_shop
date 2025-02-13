import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model

from shop.models import Purchase, CoinTransaction
from shop.constants import MERCH_ITEMS
from shop.views import buy_merch, send_coin

User = get_user_model()


@pytest.mark.django_db
def test_buy_merch_unit_success():
    user = User.objects.create_user(username='buyer', password='pass')
    user.balance = 1000
    user.save()

    factory = APIRequestFactory()
    item = 't-shirt'
    price = MERCH_ITEMS[item]
    initial_balance = user.balance

    request = factory.get(f'/api/buy/{item}/')
    force_authenticate(request, user=user)

    response = buy_merch(request, item=item)

    assert response.status_code == 200, 'Покупка мерча не удалась'
    user.refresh_from_db()
    assert user.balance == initial_balance - price, 'Некорректный баланс'

    purchase = Purchase.objects.filter(user=user, item=item).first()
    assert purchase is not None, 'Запись о покупке не создана'
    assert purchase.price == price, 'Цена покупки неверна'


@pytest.mark.django_db
def test_send_coin_unit_success():
    sender = User.objects.create_user(username='sender', password='pass')
    sender.balance = 1000
    sender.save()

    recipient = User.objects.create_user(username='recipient', password='pass')
    recipient.balance = 1000
    recipient.save()
    factory = APIRequestFactory()
    data = {'toUser': recipient.id, 'amount': 100}
    request = factory.post('/api/sendCoin/', data, format='json')
    force_authenticate(request, user=sender)
    
    response = send_coin(request)
    assert response.status_code == 200, 'Перевод монет не удался'

    sender.refresh_from_db()
    recipient.refresh_from_db()
    assert sender.balance == 900, 'Баланс отправителя неверен'
    assert recipient.balance == 1100, 'Баланс получателя неверен'

    transaction = CoinTransaction.objects.filter(
        from_user=sender, to_user=recipient, amount=100
    ).first()
    assert transaction is not None, 'Запись транзакции не создана'

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from shop.constants import MERCH_ITEMS
from shop.models import CoinTransaction, Purchase, User


@pytest.mark.django_db
def test_buy_merch_success():
    client = APIClient()

    user = User.objects.create(username='testuser123', password='testpass')
    user.save()

    auth_url = reverse('auth')
    auth_response = client.post(
        auth_url, {
         'username': 'testuser123', 'password': 'testpass'
        }, format='json'
    )
    assert auth_response.status_code == 200, 'Не удалось получить токен'
    token = auth_response.data.get('access')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    item = 't-shirt'
    price = MERCH_ITEMS[item]
    initial_balance = user.balance
    buy_url = reverse('buy_merch', kwargs={'item': item})
    response = client.get(buy_url)

    assert response.status_code == 200, 'Покупка мерча не удалась'

    user.refresh_from_db()
    assert user.balance == initial_balance - price, 'Неверный баланс'

    purchase = Purchase.objects.filter(user=user, item=item).first()
    assert purchase is not None, 'Запись о покупке не создана'
    assert purchase.price == price, 'Цена покупки неверна'


@pytest.mark.django_db
def test_send_coin_success():
    client = APIClient()

    sender = User.objects.create_user(username='sender', password='pass123')
    sender.save()

    recipient = User.objects.create_user(
        username='recepient', password='pass123'
    )
    recipient.save

    auth_url = reverse('auth')
    auth_response = client.post(
        auth_url, {'username': 'sender', 'password': 'pass123'}, format='json'
    )
    assert auth_response.status_code == 200, 'Нет токена отправителя'
    token = auth_response.data.get('access')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    send_coin_url = reverse('send_coin')
    data = {
        'toUser': recipient.id,
        'amount': 100
    }
    response = client.post(send_coin_url, data, format='json')

    assert response.status_code == 200, 'Перевод монет не удался'

    sender.refresh_from_db()
    recipient.refresh_from_db()

    assert sender.balance == 900, 'Баланс отправителя неверен'
    assert recipient.balance == 1100, 'Баланс получателя неверен'

    transaction = CoinTransaction.objects.filter(
        from_user=sender, to_user=recipient, amount=100
    ).first
    assert transaction is not None, 'Запись транзакции не создана'

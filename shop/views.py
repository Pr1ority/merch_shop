from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import MERCH_ITEMS
from .models import CoinTransaction, Purchase


User = get_user_model()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def buy_merch(request, item):
    user = request.user
    if item not in MERCH_ITEMS:
        return Response(
            {'error': 'Некорректный предмет'},
            status=status.HTTP_400_BAD_REQUEST
        )
    price = MERCH_ITEMS[item]
    if user.balance < price:
        return Response(
            {'error': 'Недостаточно средств'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user.balance -= price
    user.save()
    Purchase.objects.create(user=user, item=item, price=price)
    return Response({'message': 'Покупка успешна'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_info(request):
    user = request.user
    purchases = Purchase.objects.filter(user=user)
    sent_transactions = CoinTransaction.objects.filter(from_user=user)
    received_transactions = CoinTransaction.objects.filter(to_user=user)

    data = {
        'coins': user.balance,
        'inventory': [
            {
                'item': p.item, 'price': p.price, 'timestamp': p.timestamp
            } for p in purchases
        ],
        'coinHistory': {
            'sent': [
                {
                    'toUser': t.to_user.username,
                    'amount': t.amount,
                    'timestamp': t.timestamp
                } for t in sent_transactions
            ],
            'received': [
                {
                    'fromUser': t.from_user.username,
                    'amount': t.amount,
                    'timestamp': t.timestamp
                } for t in received_transactions
            ],
        }
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_coin(request):
    to_user_id = request.data.get('toUser')
    amount = request.data.get('amount')
    if not to_user_id or not amount:
        return Response(
            {'error': 'Нужны toUser и amount'},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        amount = int(amount)
    except ValueError:
        return Response(
            {'error': 'Некорректное значение amount'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = request.user
    if user.balance < amount:
        return Response(
            {'error': 'Недостаточно средств'},
            status=status.HTTP_400_BAD_REQUEST
        )

    to_user = get_object_or_404(User, id=to_user_id)

    user.balance -= amount
    user.save()
    to_user.balance += amount
    to_user.save()

    CoinTransaction.objects.create(
        from_user=user, to_user=to_user, amount=amount
    )
    return Response(
        {'message': 'Средства переведены'}, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth(request):
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return Response(
            {'error': 'Необходимо указать имя пользователя и пароль.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password(password)
        user.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh)
      }, status=status.HTTP_200_OK)

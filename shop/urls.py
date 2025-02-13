from django.urls import path

from .views import auth, buy_merch,  get_info, send_coin


urlpatterns = [
    path('buy/<str:item>/', buy_merch, name='buy_merch'),
    path('auth/', auth, name='auth'),
    path('info/', get_info, name='get_info'),
    path('sendCoin/', send_coin, name='send_coin')
]

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    balance = models.IntegerField(default=1000)

    def __str__(self):
        return f'У пользователя {self.username} на счету {self.balance} монет.'


class CoinTransaction(models.Model):
    from_user = models.ForeignKey(
        User, related_name='sent_transactions', on_delete=models.CASCADE,
        null=True, blank=True
    )
    to_user = models.ForeignKey(
        User, related_name='received_transactions', on_delete=models.CASCADE,
        null=True, blank=True
    )
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f'{self.from_user.username} перевел пользователю '
            f'{self.to_user.username} {self.amount} монет.'
        )


class Purchase(models.Model):
    user = models.ForeignKey(
        User, related_name='purchases', on_delete=models.CASCADE
    )
    item = models.CharField(max_length=50)
    price = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} приобрел {self.item}.'

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Book(models.Model):
    title  = models.CharField(max_length=50,unique=True)
    author = models.CharField(max_length=50)
    sdesc  = models.CharField(max_length=100,unique=True)
    price  = models.IntegerField(default=0)
    borrow = models.IntegerField(default=0)
    purchase = models.IntegerField(default=0)
    cart = models.IntegerField(default=0)
    uid = models.IntegerField(default=0)
    
class UserImage(models.Model):
    image  = models.ImageField()
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)

class UserPaymentDetails(models.Model):
    name = models.CharField(max_length=50,verbose_name='Name On Debit Card')
    debit_card_num = models.CharField(max_length=16,unique=True,verbose_name='Debit Card Number')
    cvv = models.CharField(max_length=3,unique=True,verbose_name='CVV')
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    price = models.IntegerField(default=0,null=True,verbose_name="Amount")
 
class NetBankingDetails(models.Model):
    first_name = models.CharField(max_length=50,default=0)
    last_name= models.CharField(max_length=50,default=0)
    account_num = models.CharField(max_length=15,default=0,unique=True)
    mobile_num = models.CharField(max_length=10,default=0,unique=True)
    username = models.CharField(max_length=50,unique=True)
    password = models.CharField(max_length=30)
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
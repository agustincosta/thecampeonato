from django.db import models

from django.db import models

class Groups(models.Model):
    group = models.IntegerField(primary_key=True)
    group_name = models.CharField(max_length=80)

    def __str__(self):
        return self.group_name

class Users(models.Model):
    user = models.IntegerField(primary_key=True)
    user_name = models.CharField(max_length=80)
    email = models.CharField(max_length=80)
    profile_options = models.IntegerField()
    user_age = models.IntegerField()
    date_created = models.DateField()
    group_id = models.ForeignKey(Groups, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.user_name

class Purchases(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    store_id = models.IntegerField()
    purchase_date = models.DateField()
    purchase_total = models.FloatField()
    purchase = models.IntegerField(primary_key=True, default=0)

    def __str__(self):
        return str(self.purchase)

class Products(models.Model):
    product_id = models.IntegerField(primary_key=True)
    product_description = models.CharField(max_length=80)
    product_quantity = models.FloatField()
    product_unit_price = models.FloatField()
    product_total_price = models.FloatField()
    purchase_id = models.ForeignKey(Purchases, on_delete=models.CASCADE)

class Categories(models.Model):
    purchase_id = models.ForeignKey(Purchases, on_delete=models.CASCADE)
    category_text = models.CharField(max_length=80)
    amount = models.FloatField()

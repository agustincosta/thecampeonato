from django import forms
from .models import Users, Groups, Products, Purchases, Categories

YEAR_CHOICES = [('2019','2019'),('2020','2020'),('2021','2021'),('2022','2022')]
MONTH_CHOICES = [('1','January'),('2','February'),('3','March'),('4','April'),('5','May'),\
                ('6','June'),('7','July'),('8','August'),('9','September'),('10','October'),('11','November'),('12','December')]

class UserForm(forms.ModelForm):
    group_id = forms.ModelChoiceField(queryset=Groups.objects.all(), \
                                        to_field_name='group', \
                                        empty_label="Select group")
    class Meta:
        model = Users
        exclude = ['group_id']
        labels = {'user':"ID", 'user_name':"Name", 'email':"Email", 'profile_options':"Options",\
             'user_age':"Age",'date_created':"User creation date", 'group_id':"Member of group"}
        widgets = {'date_created':forms.SelectDateWidget(years=YEAR_CHOICES)}

class GroupForm(forms.ModelForm):
    class Meta:
        model = Groups
        fields = '__all__'
        labels = {'group':"ID", 'group_name':"name"}

class PurchasesForm(forms.ModelForm):
    class Meta:
        model = Purchases
        fields = '__all__'
        labels = {'user_id':"User ID", 'store_id':"Store ID", 'purchase_date':"Purchase Date", \
            'purchase_total':"Purchase total", 'purchase':"Purchase ID"}
        widgets = {'purchase_date':forms.SelectDateWidget(years=YEAR_CHOICES)}

class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = '__all__'
        labels = {'product_id':"Product ID", 'product_description':"Description",\
             'product_quantity':"Quantity", 'product_unit_price':"Unit price",\
             'product_total_price':"Total price", 'purchase_id':"Purchase ID"}

class CategoriesForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = '__all__'
        labels = {'purchase_id':"Purchase ID", 'category_text':"Category",'amount':"Amount"}

class SelectUserForm(forms.Form):
    user_id = forms.ModelChoiceField(queryset=Users.objects.all(), \
                                        to_field_name='user', \
                                        empty_label="Select user")

class SelectGroupForm(forms.Form):
    group_id = forms.ModelChoiceField(queryset=Groups.objects.all(), \
                                        to_field_name='group', \
                                        empty_label="Select group")

class SelectPurchaseForm(forms.Form):
    purchase_id = forms.ModelChoiceField(queryset=Purchases.objects.all(), \
                                        to_field_name='purchase', \
                                        empty_label="Select purchase")

class SelectProductForm(forms.Form):
    product_id = forms.ModelChoiceField(queryset=Products.objects.all(), \
                                        to_field_name='product_id', \
                                        empty_label="Select product")

class SelectCategoriesForm(forms.Form):
    category_id = forms.ModelChoiceField(queryset=Categories.objects.all(), \
                                        to_field_name='id', \
                                        empty_label="Select category")

#Analytics

class SinglePurchaseDetailsForm(forms.Form):
    purchase_id = forms.ModelChoiceField(queryset=Purchases.objects.all(), \
                                        to_field_name='purchase', \
                                        empty_label="Select purchase")

class UserPurchaseDetailsForm(forms.Form):
    user_id = forms.ModelChoiceField(queryset=Users.objects.all(), \
                                        to_field_name='user', \
                                        empty_label="Select user")

class LastPurchasesForm(forms.Form):
    n = forms.IntegerField(max_value=20, min_value=1)

class UserMthlyDetailsForm(forms.Form):
    user_id = forms.ModelChoiceField(queryset=Users.objects.all(), \
                                        to_field_name='user', \
                                        empty_label="Select user")
    year = forms.ChoiceField(choices=YEAR_CHOICES)
    month = forms.ChoiceField(choices=MONTH_CHOICES)

class GroupMthlyDetailsForm(forms.Form):
    group_id = forms.ModelChoiceField(queryset=Groups.objects.all(), \
                                        to_field_name='group', \
                                        empty_label="Select group")
    year = forms.ChoiceField(choices=YEAR_CHOICES)
    month = forms.ChoiceField(choices=MONTH_CHOICES)

class GroupInfoForm(forms.Form):
    group_id = forms.ModelChoiceField(queryset=Groups.objects.all(), \
                                        to_field_name='group', \
                                        empty_label="Select group")

class PurchaseAnalysisForm(forms.Form):
    purchase_id = forms.ModelChoiceField(queryset=Purchases.objects.all(), \
                                        to_field_name='purchase', \
                                        empty_label="Select purchase")

class MonthlyAnalysisForm(forms.Form):
    user_id = forms.ModelChoiceField(queryset=Users.objects.all(), \
                                        to_field_name='user', \
                                        empty_label="Select user")
    year = forms.ChoiceField(choices=YEAR_CHOICES)
    month = forms.ChoiceField(choices=MONTH_CHOICES)

class GroupMonthlyAnalysisForm(forms.Form):
    group_id = forms.ModelChoiceField(queryset=Groups.objects.all(), \
                                        to_field_name='group', \
                                        empty_label="Select group")
    year = forms.ChoiceField(choices=YEAR_CHOICES)
    month = forms.ChoiceField(choices=MONTH_CHOICES)
    
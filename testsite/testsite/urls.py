"""testsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.contrib import admin
from django.urls import path, include
from expense_tracking import views
from django.views.generic import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
    
    path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url("favicon.ico")),),
    path('userform/', views.load_data_form_view,{'check_date':True, 'form_type':'UserForm'}, name='userform'),
    path('groupform/', views.load_data_form_view,{'check_date':False, 'form_type':'GroupForm'}, name='groupform'),
    path('purchaseform/', views.load_data_form_view,{'check_date':False, 'form_type':'PurchaseForm'}, name='purchaseform'),
    path('productform/', views.load_data_form_view,{'check_date':False, 'form_type':'ProductsForm'}, name='productform'),
    path('categoriesform/', views.load_data_form_view,{'check_date':False, 'form_type':'CategoriesForm'}, name='categoriesform'),
    
    path('userview/', views.data_list_view,{'form_type':'UserForm'}, name='userview'),
    path('groupview/', views.data_list_view,{'form_type':'GroupForm'}, name='groupview'),
    path('purchaseview/', views.data_list_view,{'form_type':'PurchaseForm'}, name='purchaseview'),
    path('productview/', views.data_list_view,{'form_type':'ProductsForm'}, name='productview'),
    path('categoriesview/', views.data_list_view,{'form_type':'CategoriesForm'}, name='categoriesview'),
    
    path('useredit/', views.edit_selection_view,{'form_type':'UserForm'},name='userselect'),
    path('groupedit/', views.edit_selection_view,{'form_type':'GroupForm'},name='groupselect'),
    path('purchaseedit/', views.edit_selection_view,{'form_type':'PurchaseForm'},name='purchaseselect'),
    path('productedit/', views.edit_selection_view,{'form_type':'ProductsForm'},name='productselect'),
    path('categoriesedit/', views.edit_selection_view,{'form_type':'CategoriesForm'},name='categoriesselect'),

    path('datatable/singlepurchase/', views.dataTablesSelection,{'form_type':'SinglePurchase'},name='singlepurchaseselect'),
    path('datatable/userpurchases/', views.dataTablesSelection,{'form_type':'UserPurchases'},name='userpurchaseselect'),
    path('datatable/lastpurchases/', views.dataTablesSelection,{'form_type':'LastPurchases'},name='lastpurchaseselect'),
    path('datatable/usermonthlypurchases/', views.dataTablesSelection,{'form_type':'UserMthlyPurchases'},name='usermthlypurchaseselect'),
    path('datatable/groupmonthlypurchases/', views.dataTablesSelection,{'form_type':'GroupMthlyPurchases'},name='groupmthlypurchaseselect'),
    path('datatable/usersingroup/', views.dataTablesSelection,{'form_type':'UsersInGroup'},name='groupselect'),

    path('singlepurchaseinfo/<int:p_id>/', views.getSinglePurchaseInfo),
    path('userpurchaseinfo/<int:u_id>/', views.getUserPurchaseInfo),
    path('lastpurchases/<int:n>/', views.getLastPurchases),
    path('usermthlyinfo/<int:userid>/<int:year>/<int:month>/', views.getUserMonthlyPurchases),
    path('groupmthlyinfo/<int:groupid>/<int:year>/<int:month>/', views.getGroupMonthlyPurchases),
    path('groupinfo/<int:gr_id>/', views.getUsersInGroup),

    path('analytics/singlepurchase/', views.analysisSelection,{'form_type':'SinglePurchaseAnalysis'},name='singlepurchaseanalysis'),
    path('analytics/monthlypurchases/', views.analysisSelection,{'form_type':'MonthlyPurchaseAnalysis'},name='monthlypurchaseanalysis'),
    path('analytics/groupmonthlypurchases/', views.analysisSelection,{'form_type':'GroupMonthlyPurchaseAnalysis'},name='grpmonthlypurchaseanalysis'),
    
    path('purchaseanalysis/<int:p_id>/', views.uniquePurchaseAnalysis),
    path('mthlyanalysis/<int:userid>/<int:year>/<int:month>/', views.monthlyPurchaseAnalysis),
    path('grpmthlyanalysis/<int:groupid>/<int:year>/<int:month>/', views.analyseGroupMonthlyPurchases),

    path('importtable/', views.importTable),

    path('home/', views.home_view, name='home'),
    path('',RedirectView.as_view(pattern_name='home', permanent=False), name='root')
]

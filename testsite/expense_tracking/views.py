from django.shortcuts import render, redirect
from .models import Users, Groups, Purchases, Products, Categories
from .forms import *
from datetime import datetime
from django.core.exceptions import ValidationError
from .externals import categorization_funcs
import matplotlib.pyplot as plt
import csv
import numpy as np
import calendar

def load_data_form_view(request, **kwargs):
    """Loads row of data into selected table

    Args:
        request (_type_): HTTP request
        kwargs['check_date']: Verify date isn't greater than current date
        kwargs['form_type']: Model table chosen to load data

    Raises:
        ValidationError: _description_

    Returns:
        _type_: Render request to defined template
    """
    checkDate = kwargs['check_date']
    formType = kwargs['form_type']

    if request.method=="POST":
        if formType == 'UserForm':
            form = UserForm(request.POST)
            if form.is_valid():
                my_date = form.cleaned_data['date_created']
                repeated_data_1 = form.cleaned_data['user']
                repeated_data_2 = form.cleaned_data['email']
                if [repeated_data_1, repeated_data_2] in Users.objects.all():
                    expl = 'Data already on DB'
                    return render(request, 'form-error.html', {'explanation':expl})

        elif formType == 'GroupForm':
            form = GroupForm(request.POST)
            if form.is_valid():
                if form.cleaned_data['group'] in Groups.objects.all():
                    expl = 'Data already on DB'
                    return render(request, 'form-error.html', {'explanation':expl})

        elif formType == 'PurchaseForm':
            form = PurchasesForm(request.POST)
            if form.is_valid():
                if form.cleaned_data['purchase'] in Purchases.objects.all():
                    expl = 'Data already on DB'
                    return render(request, 'form-error.html', {'explanation':expl})

        elif formType == 'ProductsForm':
            form = ProductsForm(request.POST)
            if form.is_valid():
                if form.cleaned_data['purchase'] in Products.objects.all():
                    expl = 'Data already on DB'
                    return render(request, 'form-error.html', {'explanation':expl})

        elif formType == 'CategoriesForm':
            form = CategoriesForm(request.POST)

        else:
            return render(request, 'form-error.html', {'explanation':'Inexistent form'})
        
        if form.is_valid():
            #Fecha invalida
            print(form)
            print(checkDate)
            if checkDate:
                my_date_str = ('%s' % (my_date))
                my_date_time = datetime.strptime(my_date_str, '%Y-%m-%d')
                if datetime.today() <= my_date_time:
                    raise ValidationError(u'Date greater that actual date! "%s"' % my_date_time)   
            
            form.save()
            return render(request, 'form-success.html', {})
        else:
            form = UserForm()
            return render(request, 'form-error.html', {'explanation':'Protocol error'})

    else:
        #GET method, first loading of the page
        if formType == 'UserForm':
            form = UserForm(request.POST)
        elif formType == 'GroupForm':
            form = GroupForm(request.POST)
        elif formType == 'PurchaseForm':
            form = PurchasesForm(request.POST)
        elif formType == 'ProductsForm':
            form = ProductsForm(request.POST)
        elif formType == 'CategoriesForm':
            form = CategoriesForm(request.POST)
        return render(request, 'regular-form.html', {'form':form})

def data_list_view(request, **kwargs):
    formType = kwargs['form_type']

    if request.method=="POST":
        if formType == 'UserForm':
            form = UserForm(request.POST)

        elif formType == 'GroupForm':
            form = GroupForm(request.POST)

        elif formType == 'PurchaseForm':
            form = PurchasesForm(request.POST)

        elif formType == 'ProductsForm':
            form = ProductsForm(request.POST)

        elif formType == 'CategoriesForm':
            form = CategoriesForm(request.POST)

        else:
            return render(request, 'form-error.html', {'explanation':'Inexistent form'})
        
        if form.is_valid():
            #Fecha invalida
            form.save()
            return render(request, 'form-success.html', {})
        else:
            form = UserForm()
            return render(request, 'form-error.html', {'explanation':'Protocol error'})

    else:
        #GET method, first loading of the page
        if formType == 'UserForm':
            data = Users.objects.all()
            title = "Users"
            templates = 'table-users.html'
        elif formType == 'GroupForm':
            data = Groups.objects.all()
            title = "Groups"
            templates = 'table-groups.html'
        elif formType == 'PurchaseForm':
            data = Purchases.objects.all()
            title = "Purchases"
            templates = 'table-purchases.html'
        elif formType == 'ProductsForm':
            data = Products.objects.all()
            title = "Products"
            templates = 'table-products.html'
        elif formType == 'CategoriesForm':
            data = Categories.objects.all()
            title = "Categories"
            templates = 'table-categories.html'
        return render(request, templates, {'title':title,'table':data})

def edit_selection_view(request, **kwargs):
    formType = kwargs['form_type']

    if request.method=="POST":
        if formType == 'UserForm':
            form = SelectUserForm(request.POST)
            if form.is_valid():
                selected_user = form.cleaned_data['user_id'].pk
                print(selected_user)
                redir_url = '../userform/' + str(selected_user) + '/'
            else:
                print(form.errors) 

        elif formType == 'GroupForm':
            form = GroupForm(request.POST)
            if form.is_valid():
                selected_group = form.cleaned_data['group'].pk
                redir_url = '../groupform/' + str(selected_group) + '/'
            else:
                print(form.errors)    

        elif formType == 'PurchaseForm':
            form = PurchasesForm(request.POST)
            if form.is_valid():
                selected_purchase = form.cleaned_data['purchase_id']
                redir_url = '../purchaseform/' + str(selected_purchase) + '/' 
            else:
                print(form.errors) 

        elif formType == 'ProductsForm':
            form = ProductsForm(request.POST)
            if form.is_valid():
                selected_product = form.cleaned_data['product_id']
                redir_url = 'productform/' + str(selected_product) + '/' 
            else:
                print(form.errors) 

        elif formType == 'CategoriesForm':
            form = CategoriesForm(request.POST)
            if form.is_valid():
                selected_category = form.cleaned_data['id']
                redir_url = 'categoriesform/' + str(selected_category) + '/' 
            else:
                print(form.errors) 

        else:
            return render(request, 'form-error.html', {'explanation':'Inexistent form'})

        print (redir_url)
        return redirect(redir_url)

    else:
        #GET
        if formType == 'UserForm':
            form = SelectUserForm(request.POST)
            
        elif formType == 'GroupForm':
            form = SelectGroupForm(request.POST)

        elif formType == 'PurchaseForm':
            form = SelectPurchaseForm(request.POST)

        elif formType == 'ProductsForm':
            form = SelectProductForm(request.POST)

        elif formType == 'CategoriesForm':
            form = SelectCategoriesForm(request.POST)

        else:
            return render(request, 'form-error.html', {'explanation':'Inexistent form'})

        return render(request,'regular-form.html', {'form':form}) 

def getSinglePurchaseInfo(request, p_id):
    """Returns purchase info for purchase id

    Args:
        request (_type_): HTTP request
        p_id (int): Purchase id
    """
    single_purchase = list(Purchases.objects.filter(purchase=p_id).values_list('user_id','store_id','purchase_date','purchase_total','purchase'))

    column_headers = ('user_id','store_id','purchase_date','purchase_total','purchase')
    table_title = 'Purchase detail for purchase id: '
    query_subject = str(p_id)

    if single_purchase == []:
        return render(request, "no-data.html")
    else:
        return render(request, "data-table.html",context={'data':single_purchase, 'header':column_headers, 'table_title':table_title, 'subject':query_subject})

def getUserPurchaseInfo(request, u_id):
    """Returns all the purchases made by a user

    Args:
        request (_type_): HTTP request
        u_id (int): User id
    """
    user_purchases = list(Purchases.objects.filter(user_id=u_id).values_list('user_id','store_id','purchase_date','purchase_total','purchase'))
    column_headers = ('user_id','store_id','purchase_date','purchase_total','purchase')
    table_title = 'Purchases detail for user: '
    query_subject = Users.objects.filter(user=u_id).values_list('user_name')[0][0]

    if user_purchases == []:
        return render(request, "no-data.html")
    else:
        return render(request, "data-table.html", context={'data':user_purchases, 'header':column_headers, 'table_title':table_title, 'subject':query_subject})

def uniquePurchaseAnalysis(request, p_id):
    """Categorizacion de compra (unica) y pie chart opcional

        Args:
            p_id (int): ID de compra para querys en multiples tablas

        Returns:
            uniqueCats (list[string]): Lista de las categorias 
            uniqueAmts (np.array[float]): Array de total para cada categoria
    """ 
    purchase_details = list(Products.objects.filter(purchase_id=p_id).values_list('product_description','product_total_price'))
    purchase_date = list(Purchases.objects.filter(purchase=p_id).values_list('purchase_date'))[0][0]
    userid = list(Purchases.objects.filter(purchase=p_id).values_list('user_id'))[0][0]

    purchase_details = np.array([list(item) for item in purchase_details])

    labels = purchase_details[:,0]
    amounts = purchase_details[:,1]

    cat = categorization_funcs.Categorization("expense_tracking/externals/categorias.csv")
    categories = cat.categorizeItems(labels, cutoff=0.4)
    uniqueCats, uniqueAmts = cat.addCategoriesTotal(categories, amounts)
    
    if (list(Categories.objects.filter(purchase_id=p_id).values_list('purchase_id')) == []):
        for i in range(len(uniqueCats)):
            row = Categories(purchase_id=Purchases.objects.get(purchase=p_id), category_text=uniqueCats[i], amount=uniqueAmts[i])
            row.save()
    
    user_name = list(Users.objects.filter(user=userid).values_list('user_name'))[0][0]

    title = 'Compra de ' + user_name + ' el día ' + purchase_date.strftime("%d %b %Y")
    createPieChart(uniqueAmts, uniqueCats, title, save=True)
    
    return render(request, "pie-plot.html")

def getLastPurchases(request, n): 
    """Returns the las n purchases

    """
    last_purchases = list(Purchases.objects.order_by('-purchase_date')[:n].values_list('user_id','store_id','purchase_date','purchase_total','purchase'))
    column_headers = ('user_id','store_id','purchase_date','purchase_total','purchase')
    table_title = 'Last 5 purchases: '

    if last_purchases == []:
        return render(request, "no-data.html")
    else:    
        return render(request, "data-table.html", context={'data':last_purchases, 'header':column_headers, 'table_title':table_title, 'subject':''})

def getUsersInGroup(request, gr_id):
    """Returns users in selected group

    Args:
        group_nr (int): Group number
    """
    users_in_group = Users.objects.filter(group_id=gr_id).values_list('user_name', 'email', 'user_age', 'date_created')
    column_headers = ('Name', 'Email', 'Age', 'Date created')
    table_title = 'Usuarios en grupo: '
    query_subject = list(Groups.objects.filter(group=gr_id).values_list('group_name'))[0][0]

    if users_in_group == []:
        return render(request, "no-data.html")
    else:
        return render(request, "data-table.html",context={'data':users_in_group, 'header':column_headers, 'table_title':table_title, 'subject':query_subject})

def getUserMonthlyPurchases(request, userid, year, month):
    """Returns the details of purchases made by a user on a given month and year

    Args:
        user_id (int): User ID
        month (int): Month of purchases
        year (int): Year of purchases
    """  
    end_day = calendar.monthrange(year, month)[1]
    month_end = str(year) + '-' + str(month) + '-' + str(end_day)
    month_start = str(year) + '-' + str(month) + '-1'     

    monthly_purchases = list(Purchases.objects.filter(user_id=userid).filter(purchase_date__lte=month_end).filter(purchase_date__gte=month_start).values_list('user_id','store_id','purchase_date','purchase_total','purchase'))
    column_headers = ('user_id','store_id','purchase_date','purchase_total','purchase')
    table_title = 'Purchases detail for user: '
    query_subject = Users.objects.filter(user=userid).values_list('user_name')[0][0]
    query_subject = query_subject + ' | Month: ' + str(month) + " - Year: " + str(year)

    if monthly_purchases == []:
        return render(request, "no-data.html")
    else:
        return render(request, "data-table.html", context={'data':monthly_purchases, 'header':column_headers, 'table_title':table_title, 'subject':query_subject})

def categorizePurchase(pid):
    """Categorization and pie chart for purchases made by selected user in given month

    Args:
        user_id (int): User ID
        month (int): Month of purchases
        year (int): Year of purchases
    """
    purchase_details = list(Products.objects.filter(purchase_id=pid).values_list('product_description','product_total_price'))
    userid = list(Purchases.objects.filter(purchase=pid).values_list('user_id'))[0][0]

    purchase_details = np.array([list(item) for item in purchase_details])

    labels = purchase_details[:,0]
    amounts = purchase_details[:,1]

    cat = categorization_funcs.Categorization("expense_tracking/externals/categorias.csv")
    categories = cat.categorizeItems(labels, cutoff=0.4)
    uniqueCats, uniqueAmts = cat.addCategoriesTotal(categories, amounts)
    
    if (list(Categories.objects.filter(purchase_id=userid).values_list('purchase_id')) == []):
        for i in range(len(uniqueCats)):
            row = Categories(purchase_id=Purchases.objects.get(purchase=userid), category_text=uniqueCats[i], amount=uniqueAmts[i])
            row.save()

    return uniqueCats, uniqueAmts

def monthlyPurchaseAnalysis(request, userid, year, month):
    """Categorization and pie chart for purchases made by selected user in given month

    Args:
        user_id (int): User ID
        month (int): Month of purchases
        year (int): Year of purchases
    """
    end_day = calendar.monthrange(year, month)[1]
    month_end = str(year) + '-' + str(month) + '-' + str(end_day)
    month_start = str(year) + '-' + str(month) + '-1'    

    monthly_purchases_ids = list(Purchases.objects.filter(user_id=userid).filter(purchase_date__lte=month_end).filter(purchase_date__gte=month_start).values_list('purchase', flat=True))

    uniqueMthlyCats = []
    uniqueMthlyAmts = np.zeros(1)

    userMthlyCats = []
    userMthlyAmts = np.zeros(1)

    if monthly_purchases_ids != []:
        for id in monthly_purchases_ids:
            user_unique_labels, user_unique_amounts = categorizePurchase(pid=id)

            userMthlyCats.extend(user_unique_labels)
            userMthlyAmts = np.append(userMthlyAmts, user_unique_amounts)

        cat = categorization_funcs.Categorization("expense_tracking/externals/categorias.csv")
        uniqueMthlyCats, uniqueMthlyAmts = cat.addCategoriesTotal(userMthlyCats, userMthlyAmts)

        user_name = list(Users.objects.filter(user=userid).values_list('user_name'))[0][0]

        plotTitle = 'Compras de ' + user_name + ' el mes ' + str(month) + "/" + str(year)
        createPieChart(uniqueMthlyAmts, uniqueMthlyCats, plotTitle, save=True)
                
        return render(request, "pie-plot.html")

    else:
        return render(request, "no-data.html")

def queryGroupMonthlyPurchases(groupid, year, month):
    """Returns the details of purchases made by all users members of a group on a given month and year

    Args:
        groupid (int): Group ID
        month (int): Month of purchases
        year (int): Year of purchases
    """  
    users_ids = list(Users.objects.filter(group_id=groupid).values_list('user', flat=True))

    end_day = calendar.monthrange(year, month)[1]
    month_end = str(year) + '-' + str(month) + '-' + str(end_day)
    month_start = str(year) + '-' + str(month) + '-1' 

    groupMthlyCats = []
    groupMthlyAmts = np.zeros(1)

    if users_ids != []:
        for id in users_ids:
            purchaseids = list(Purchases.objects.filter(user_id=id).filter(purchase_date__lte=month_end).filter(purchase_date__gte=month_start).values_list('purchase', flat=True))
            
            if purchaseids != []:
                for pid in purchaseids:
                    userPurchaseLabels, userPurchaseAmts = categorizePurchase(pid=pid)
                    groupMthlyCats.extend(userPurchaseLabels)
                    groupMthlyAmts = np.append(groupMthlyAmts, userPurchaseAmts)
        
        cat = categorization_funcs.Categorization("expense_tracking/externals/categorias.csv")
        uniqueMthlyCats, uniqueMthlyAmts = cat.addCategoriesTotal(groupMthlyCats, groupMthlyAmts)

        return uniqueMthlyAmts, uniqueMthlyCats 
    else:
        return [],[]

def getGroupMonthlyPurchases(request, groupid, year, month):
    """Returns the details of purchases made by all users members of a group on a given month and year

    Args:
        groupid (int): Group ID
        month (int): Month of purchases
        year (int): Year of purchases
    """  
    users_ids = list(Users.objects.filter(group_id=groupid).values_list('user', flat=True))

    end_day = calendar.monthrange(year, month)[1]
    month_end = str(year) + '-' + str(month) + '-' + str(end_day)
    month_start = str(year) + '-' + str(month) + '-1' 

    column_headers = ('user_id','store_id','purchase_date','purchase_total','purchase')
    table_title = 'Purchases detail for group: '
    query_subject = Groups.objects.filter(group=groupid).values_list('group_name')[0][0]
    query_subject = query_subject + ' | Month: ' + str(month) + " - Year: " + str(year)

    monthly_purchases = []

    if users_ids != []:
        for id in users_ids:
            purchaseids = list(Purchases.objects.filter(user_id=id).filter(purchase_date__lte=month_end).filter(purchase_date__gte=month_start).values_list('user_id','store_id','purchase_date','purchase_total','purchase'))
            monthly_purchases.extend(purchaseids)

        if monthly_purchases != []:    
            return render(request, "data-table.html", context={'data':monthly_purchases, 'header':column_headers, 'table_title':table_title, 'subject':query_subject}) 
        else:
            return render(request, "no-data.html")   
    else:
        return render(request, "no-data.html")

def analyseGroupMonthlyPurchases(request, groupid, year, month):
    """Categorization and pie chart for purchases made by all users belonging to a group in given month

    Args:
        groupid (int): User ID
        month (int): Month of purchases
        year (int): Year of purchases
    """
    groupMthlyCats = []
    groupMthlyAmts = np.zeros(1)

    groupMthlyAmts, groupMthlyCats = queryGroupMonthlyPurchases(groupid, year, month)

    group_name = list(Groups.objects.filter(group=groupid).values_list('group_name'))[0][0]

    if groupMthlyAmts != []:
        title = 'Compras del grupo ' + group_name + ' el mes ' + str(month) + "/" + str(year)
        createPieChart(groupMthlyAmts, groupMthlyCats, title)
        return render(request, "pie-plot.html")
    else:
        return render(request, "no-data.html")

def createPieChart(amounts, categories, plotTitle, save=True):
    """Grafica pie chart de categorias acorde a totales

    Args:
        amounts (np.array[float]): Array de totales
        categories (list[string]): Lista de categorias
        plotTitle (string): Titulo
    """        
    fig1, ax1 = plt.subplots()
    exp = np.ones_like(amounts)/50
    ax1.pie(amounts, labels=categories, autopct='%1.1f%%', shadow=False, startangle=90, explode=exp)
    ax1.axis('equal')
    plt.title(plotTitle, y=1.08)
    if save:
        plt.savefig('expense_tracking/static/expense_tracking/images/plot.png')
    else:    
        plt.show()

def home_view(request):
    sel_p_form = PurchaseAnalysisForm(request.POST)
    context ={'selec_purchase_form':sel_p_form}
    return render(request, "home.html", context)

def importTable(request):
    """Funcion auxiliar

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
    with open('expense_tracking/db2.csv', newline='', encoding='latin-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            print(row)
            pk = row[0]
            desc = row[1]
            qty = row[2]
            unit_amt = row[3]
            total_amt = row[4]
            pid = row[5]
            product = Products(product_id=pk, product_description=desc, product_quantity=qty, product_unit_price=unit_amt, product_total_price=total_amt)
            product.purchase_id = Purchases.objects.get(purchase=pid)
            product.save()
    return render(request, "no-data.html")

def dataTablesSelection(request, **kwargs):
    formType = kwargs['form_type']

    if request.method=="POST":
        if formType == 'SinglePurchase':
            form = SinglePurchaseDetailsForm(request.POST)
            if form.is_valid():
                p_id = form.cleaned_data['purchase_id']
                print(p_id)
                redir_url = '../../singlepurchaseinfo/' + str(p_id) + '/'
            else:
                print(form.errors) 

        elif formType == 'UserPurchases':
            form = UserPurchaseDetailsForm(request.POST)
            if form.is_valid():
                u_id = form.cleaned_data['user_id'].pk
                redir_url = '../../userpurchaseinfo/' + str(u_id) + '/'
            else:
                print(form.errors)    

        elif formType == 'LastPurchases':
            form = LastPurchasesForm(request.POST)
            if form.is_valid():
                number = form.cleaned_data['n']
                redir_url = '../../lastpurchases/' + str(number) + '/' 
            else:
                print(form.errors) 

        elif formType == 'UserMthlyPurchases':
            form = UserMthlyDetailsForm(request.POST)
            if form.is_valid():
                u_id = form.cleaned_data['user_id'].pk
                year = form.cleaned_data['year']
                month = form.cleaned_data['month']
                redir_url = '../../usermthlyinfo/' + str(u_id) + '/' + str(year) + '/' + str(month) + '/'
            else:
                print(form.errors) 

        elif formType == 'GroupMthlyPurchases':
            form = GroupMthlyDetailsForm(request.POST)
            if form.is_valid():
                gr_id = form.cleaned_data['group_id'].pk
                year = form.cleaned_data['year']
                month = form.cleaned_data['month']
                redir_url = '../../groupmthlyinfo/' + str(gr_id) + '/' + str(year) + '/' + str(month) + '/'
            else:
                print(form.errors) 

        elif formType == 'UsersInGroup':
            form = GroupInfoForm(request.POST)
            if form.is_valid():
                group = form.cleaned_data['group_id'].pk
                redir_url = '../../groupinfo/' + str(group) + '/' 
            else:
                print(form.errors)

        else:
            return render(request, 'form-error.html', {'explanation':'Inexistent form'})

        print (redir_url)
        return redirect(redir_url)
    else:
        #GET
        if formType == 'SinglePurchase':
            form = SinglePurchaseDetailsForm(request.POST)
            
        elif formType == 'UserPurchases':
            form = UserPurchaseDetailsForm(request.POST)

        elif formType == 'LastPurchases':
            form = LastPurchasesForm(request.POST)

        elif formType == 'UserMthlyPurchases':
            form = UserMthlyDetailsForm(request.POST)

        elif formType == 'GroupMthlyPurchases':
            form = GroupMthlyDetailsForm(request.POST)

        elif formType == 'UsersInGroup':
            form = GroupInfoForm(request.POST)

        else:
            return render(request, 'form-error.html', {'explanation':'Inexistent form'})

        return render(request,'regular-form.html', {'form':form}) 

def analysisSelection(request, **kwargs):
    formType = kwargs['form_type']

    if request.method=="POST":
        if formType == 'SinglePurchaseAnalysis':
            form = PurchaseAnalysisForm(request.POST)
            if form.is_valid():
                p_id = form.cleaned_data['purchase_id']
                print(p_id)
                redir_url = '../../purchaseanalysis/' + str(p_id) + '/'
            else:
                print(form.errors) 

        elif formType == 'MonthlyPurchaseAnalysis':
            form = MonthlyAnalysisForm(request.POST)
            if form.is_valid():
                u_id = form.cleaned_data['user_id'].pk
                year = form.cleaned_data['year']
                month = form.cleaned_data['month']
                redir_url = '../../mthlyanalysis/' + str(u_id) + '/' + str(year) + '/' + str(month) + '/'
            else:
                print(form.errors)    

        elif formType == 'GroupMonthlyPurchaseAnalysis':
            form = GroupMonthlyAnalysisForm(request.POST)
            if form.is_valid():
                gr_id = form.cleaned_data['group_id'].pk
                year = form.cleaned_data['year']
                month = form.cleaned_data['month']
                redir_url = '../../grpmthlyanalysis/' + str(gr_id) + '/' + str(year) + '/' + str(month) + '/' 
            else:
                print(form.errors) 

        else:
            return render(request, 'form-error.html', {'explanation':'Inexistent form'})

        print (redir_url)
        return redirect(redir_url)
    else:
        #GET
        if formType == 'SinglePurchaseAnalysis':
            form = PurchaseAnalysisForm(request.POST)
            
        elif formType == 'MonthlyPurchaseAnalysis':
            form = MonthlyAnalysisForm(request.POST)

        elif formType == 'GroupMonthlyPurchaseAnalysis':
            form = GroupMonthlyAnalysisForm(request.POST)

        else:
            return render(request, 'form-error.html', {'explanation':'Inexistent form'})

        return render(request,'regular-form.html', {'form':form}) 


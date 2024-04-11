from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from libapp.models import Book, UserPaymentDetails, NetBankingDetails, UserImage
from libapp.forms import UserForm, BookForm, PaymentOptionsForm, DebitCardForm, NetBankingRegisterForm, NetBankingLoginForm, NetBankingTransactionDetails, UpiTransactionDetails, ImageForm, UserProfileUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.conf import settings
import os

# Create your views here.

# REGISTER BOOK
def register_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        try:
            if form.is_valid():
                title = form.cleaned_data['title']
                author = form.cleaned_data['author']
                sdesc = form.cleaned_data['small_description']
                price  = form.cleaned_data['price']
                # setting table column values
                records = Book.objects.get_or_create(title=title,author=author,sdesc=sdesc,price=price)
                # redirecting to home page
                return redirect('/')
        except Exception as e:
            return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        else:
            try:
                form = BookForm()
                content = {'form':form,'err':'Failed To Register !'}
                return render(request,'registerbook.html',content)
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
    else:
       try:
            # if GET request show form
            form = BookForm()
            content = {'form':form}
            return render(request,'registerbook.html',content)
       except Exception as e:
            return HttpResponse("Error Occurred: {}".format(str(e),status=500))
# HOME PAGE
def home(request):
    records = Book.objects.all().order_by('price')
    records2 = Book.objects.all().values_list('purchase')
    records3 = Book.objects.all().values_list('borrow')
    is_purchase = 0
    is_borrow = 0
    # checking if books are purchased or not
    for x in range(len(records2)):
        # checking if books are purchased
        if records2[x][0] == 1:
            is_purchase += records2[x][0]
    # checking if books are borrowed or not        
    for x in range(len(records3)):
        # checking if books are borrowed or not
        if records3[x][0] == 1:
            is_borrow += records3[x][0]
    # records count for displaying 'BuyAll', 'AddToCartAll' & 'ReturnAll', 'RemoveFromCartAll' buttons
    record_count = records.count()
    content = {'data':records,'data2':records,'record_count':record_count,'is_purchase':is_purchase,
               'length':len(records2),'is_borrow':is_borrow,'length2':len(records3)}
    return render(request,'home.html',content)

# REGISTER USER
def register_user(request):
    if request.method == "POST":
        # retrieving form input data using request.POST
        form = UserForm(request.POST)
        # if form input data is correct
        if form.is_valid():
            # saving user information in auth_user table
            form.save()
            return redirect("/user-login")
        else:
            # if form input data is wrong show error message
            form = UserForm()
            content = {'data':form,'err':"Failed To Create User !"}
            return render(request,'registeruser.html',content)
    else:
       # if GET request show form
       form = UserForm()
       content = {'data':form}
       return render(request,'registeruser.html',content)

# LOGIN USER
def user_login(request):
    if request.method == "POST":
        # AuthenticationForm() provides username & password fields
        # AuthenticationForm() takes 2 parameters  
        # request = request_object & variable = request.POST
        form = AuthenticationForm(request=request,data=request.POST)
        # if form input data is correct
        if form.is_valid():
            # retrieving username & password for double confirmation
            # AuthenticationForm() use cleaned_data[] to retrieve form input values
            # 'username' & 'password' are dictionary keys to which form input values are linked
            user_name = form.cleaned_data['username']
            user_pass = form.cleaned_data['password']
            # double checking in auth_user table whether username & password exists
            user_exist = authenticate(username=user_name,password=user_pass)
            # if exist
            if user_exist:
                # create session
                login(request,user_exist)
                return redirect('/user-dashboard')
        else:
            # if form input data is wrong
            form = AuthenticationForm()
            content = {'data':form,'err':"Invalid Username OR Password"}
            return render(request,"userlogin.html",content)
    else:
        # if GET request show form
        form = AuthenticationForm()
        content = {'data':form}
        return render(request,"userlogin.html",content)

# PROFILE IMAGE (PENDING)
def profile_image(request):
    if request.method == "POST":
        # extracting imageform data
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            # extracting image
            image = form.cleaned_data['image']
            # checking if image exist
            record = UserImage.objects.filter(image=image).exists()
            # if record exist
            if record:
                return redirect('/')     
            else: 
                # when same user updates a different account picture 
                # since we have defined OneToOne relationship in UserImage model
                # we have to first delete existing account image of current user
                user = request.user.id
                # checking if image exist
                exist = UserImage.objects.filter(user_id=user).exists()
                # if account picture of current user exist
                if exist == True:
                    # deleting existing account image from images folder
                    exist = UserImage.objects.filter(user_id=user).values('image')[0].get('image')
                    os.remove(os.path.join(settings.MEDIA_ROOT,exist))
                    # delete existed account image of current user from database
                    UserImage.objects.filter(user_id=user).delete() 
                    # then update new account image of current user
                    record = UserImage.objects.get_or_create(image=image,user_id=user)
                # if account picture doesn't exist for current user    
                elif exist == False:
                    # then update new account image of current user
                    record = UserImage.objects.get_or_create(image=image,user_id=user)
                return redirect('/')  
        else:
            # if form is invalid throw error
            form = ImageForm()
            content = {'form':form,'err':'Invalid File !'}
            return render(request,'profileimageform.html',content)
    else:
        # GET
        form = ImageForm()
        content = {'form':form}
        return render(request,'profileimageform.html',content)

# USER DASHBOARD
def user_dashboard(request):
    # logged-in user must only see books borrowed OR purchased by him
    condition_1 = Q(uid=request.user.id)
    records = Book.objects.filter(condition_1) 
    record_count = records.count()
    content = {'data':records,'record_count':record_count}
    return render(request,'userdash.html',content)

# USER LOGOUT
def user_logout(request):
    # destroying sessions for current request
    # other sessions created by current user gets cleared
    logout(request)
    return redirect('/user-login')

# BORROW BOOK
def borrow_book(request,rid,uid):
    # filtering book record based on bookid
    record = Book.objects.filter(id=rid)
    # updating above book record as borrowed
    record.update(borrow=1,uid=uid,cart=0)
    return redirect('/')

# SHOW CART
def my_cart(request):
    # filtering User object & passing that object to user_id field
    user = User.objects.filter(id=request.user.id).values('id')[0].get('id')
    record = Book.objects.filter(cart=1,uid=user)
    record_count = record.count()
    content = {'data':record,'record_count':record_count}
    return render(request,'cart.html',content)

# ADD TO CART
def add_to_cart(request,rid,uid):
    record = Book.objects.filter(id=rid)
    record.update(cart=1,uid=uid)
    return redirect('/')

# ADD ALL BOOKS TO CART
def books_to_cart(request):
    # filtering books which are borrowed
    record = Book.objects.filter(borrow=1)
    if record.exists():
        # addding books in cart 
        record.update(cart=1,borrow=0) 
        return redirect('/user-dashboard')
    else:
        condition_1 = Q(uid=request.user.id)
        records = Book.objects.filter(condition_1)
        record_count = records.count()
        content = {'data':records,'err':'Borrow Book First !','record_count':record_count}
        return render(request,'userdash.html',content) 

# ADD BOOKS TO CART (HOME)
def all_books_to_cart(request):
    record = Book.objects.filter(purchase=0,borrow=0).update(cart=1,uid=request.user.id)
    return redirect('/')

# BORROW BOOK FROM CART
def borrow_from_cart(request,rid,uid):
    # filtering book record based on bookid
    record = Book.objects.filter(id=rid)
    # updating above book record as borrowed
    record.update(borrow=1,uid=uid,cart=0)
    return redirect('/my-cart')

# REMOVE FROM CART
def remove_from_cart(request,rid):
    record = Book.objects.filter(id=rid)
    record.update(cart=0,uid=0,borrow=0) 
    return redirect('/my-cart')

# REMOVE ALL BOOKS FROM CART
def remove_all_books(request):
    # filtering books added in cart
    record = Book.objects.filter(cart=1)
    if record.exists():
        # removing books from cart
        record.update(cart=0,uid=0,borrow=0)
        return redirect('/my-cart')
    else: # if no books are added to cart
        record = Book.objects.filter(cart=1,uid=request.user.id)
        record_count = record.count()
        content = {'data':record,'record_count':record_count,'err':'Cart Is Empty'}
        return render(request,'cart.html',content)

# RETURN BOOK
def return_book(request,rid):
    # filtering book record based on bookid
    record = Book.objects.filter(id=rid)
    # updating above book record as returned
    record.update(borrow=0, uid=0)
    return redirect('/user-dashboard')

# RETURN ALL BOOKS
def return_all_books(request):
    record = Book.objects.filter(borrow=1,uid=request.user.id)
    record.update(borrow=0,uid=0)
    return redirect('/user-dashboard')
    
# PAYMENT OPTIONS (SINGLE BOOK PURCHASE)
def buy_book(request,rid,uid):
    if request.method == 'POST':
        # retrieving payment method number
        payment_method = request.POST['payment_methods']
        # debit card method
        if payment_method == '1':
            # saving payment method number in session for further manipulation
            request.session['payment_method'] = payment_method
            record = Book.objects.filter(id=rid)
            # debit card form
            form = DebitCardForm(initial={'price':record[0].price})
            content = {'form':form,'data':record}
            return render(request,"debitcardform.html",content) 
        # netbanking method
        elif payment_method == '2':
            # saving payment method number in session for further manipulation
            request.session['payment_method'] = payment_method
            # netbanking form
            form = NetBankingLoginForm()
            content = {'form':form}
            return render(request,"netbankingloginform2.html",content) 
        # upi method
        elif payment_method == '3':
            # saving payment method number in session for further manipulation
            request.session['payment_method'] = payment_method
            # retrieving Book record based on record_id
            record_id = request.session['record_id']
            user_id = request.session['user_id']
            record = Book.objects.filter(id=record_id)
            # prefilling input box with above book's price
            # initial -> attribute need dictionary
            # key must be same as the form label name
            # in this case form label name is `amount` hence key is also `amount`
            form = UpiTransactionDetails(initial={'amount':record[0].price})
            record = Book.objects.filter(id=record_id)
            content = {'form':form,'data':record}
            return render(request,'upipaymentdetails.html',content)
    else:
        # GET
        # book record_id
        record_id = rid
        # logged-in user_id 
        user_id = uid 
        # saving record_id & book_id in session for further manipulation
        request.session['record_id'] = record_id
        request.session['user_id'] = user_id
        # payment method form
        form = PaymentOptionsForm()
        record = Book.objects.filter(id=rid)
        content = {'form':form,'data':record}
        return render(request,'paymentmethods.html',content)
            
# TRANSACTION DETAILS (NETBANKING LOGIN HANDLER)
def transaction_details(request):
    if request.method == 'POST':
        form = NetBankingLoginForm(request.POST)
        if form.is_valid():
            # retrieving form data
            uname = form.cleaned_data['username']
            upass = form.cleaned_data['password']
            # saving username & password in session for further manipulation
            request.session['uname'] = uname
            request.session['upass'] = upass
            # if username & password exist
            record = NetBankingDetails.objects.filter(username=uname,password=upass).exists()
            if record:
                # retrieving book based on bookid
                record_id = request.session['record_id']
                record2 = Book.objects.filter(id=record_id)
                # prefilling input box with above book's price
                # initial -> attribute need dictionary
                # key must be same as the form label name
                # in this case form label name is `amount` hence key is also `amount`  
                form2 = NetBankingTransactionDetails(initial={'amount':record2[0].price})
                content = {'form':form2,'data':record2}
                return render(request,'netbanktransactiondetails.html',content)
            else:
                form = NetBankingLoginForm()
                content = {'form':form,'err':'Invalid Username OR Password'}
                return render(request,'netbankingloginform.html',content)

# PAYMENT PROCESSING (ALL METHODS FOR SINGLE BOOK)
def payment(request):
    # this session method gets the session key
    payment_method =  request.session['payment_method'] 
    # debit card payment
    if payment_method == '1':
        # retrieving debit card form data
        name = request.POST['name']
        card_num = request.POST['debit_card_num']
        cvv = request.POST['cvv']
        # these session methods gets the session key 
        uid = request.session['user_id']
        record_id = request.session['record_id']
        # values('column_name') -> used to get values of specific column 
        user = User.objects.filter(id=uid).values('id')[0].get('id')
        # print("USER IS -> ",type(user[0].get('id')))
        # print("USER -> ",type(request.user.id))
        # saving payment method details 
        # get_or_create() method will create object if does not exist
        # when purchase is done by same debit card this method won't create same entry again
        records = UserPaymentDetails.objects.get_or_create(name=name,debit_card_num=card_num,cvv=cvv,user_id=user)
        # updating book as purchased
        records_2 = Book.objects.filter(id=record_id)
        records_2.update(purchase=1,uid=user,borrow=0,cart=0)
        return redirect('/') 
    # netbanking payment
    elif payment_method == '2':
        # these session methods gets the session key & then deletes the key from session
        uid = request.session['user_id']
        record_id = request.session['record_id']
        # saving payment method details 
        record2 = Book.objects.filter(id=record_id)
        record2.update(purchase=1,uid=uid,borrow=0)
        return redirect("/")
    # upi payment
    elif payment_method == '3':
        # these session methods gets the session key 
        uid = request.session['user_id']
        # retrieving Book record based on record_id
        record_id = request.session['record_id']
        # updating book as purchased
        record2 = Book.objects.filter(id=record_id)
        record2.update(purchase=1,uid=uid,borrow=0)
        return redirect("/")

# NETBANKING REGISTRATION FORM
def netbanking_register(request):
    if request.method == 'POST':
        form = NetBankingRegisterForm(request.POST)
        if form.is_valid():
            # retrieving form data
            fname = form.cleaned_data['first_name']
            lname = form.cleaned_data['last_name']
            accnum = form.cleaned_data['account_number']
            mobnum = form.cleaned_data['mobile_number']  
            uname = form.cleaned_data['username']
            upass = form.cleaned_data['password']

            # getting user id 
            user = User.objects.filter(id=request.user.id).values('id')[0].get('id')

            # saving netbanking details
            # get_or_create() method will create record if does not exist
            # and if record exist it will not create another copy of same record
            record = NetBankingDetails.objects.get_or_create(first_name=fname,last_name=lname,
                                                    account_num=accnum,mobile_num=mobnum,
                                                    username=uname,password=upass,user_id=user)
            # redirecting to netbanking login page
            form = NetBankingLoginForm()
            content = {'form':form}
            return render(request,"netbankingloginform.html",content) 
        else:
            # if form data is not valid show error message
            form = NetBankingRegisterForm()
            content = {'form':form,'err':'Registration Failed !'}
            return render(request,'netbankingregisterform.html',content)    
    else:
        # GET REQUEST
        form = NetBankingRegisterForm()
        content = {'form':form}
        return render(request,'netbankingregisterform.html',content)

# BORROW ALL BOOKS (HOME)
def borrow_all_books(request):
    record = Book.objects.filter(purchase=0,cart=0).update(borrow=1,uid=request.user.id,purchase=0,cart=0)
    return redirect('/')

# BORROW ALL BOOKS (CART)
def borrow_all_books2(request):
    record = Book.objects.filter(purchase=0,cart=1).update(borrow=1,uid=request.user.id,purchase=0,cart=0)
    return redirect('/')

def buy_all_books(request):
    if request.method == "POST":
        # retrieving payment method number
        payment_method = request.POST['payment_methods']
        # debit card method
        if payment_method == '1':
            # saving payment method number in session for further manipulation
            request.session['payment_method'] = payment_method
            # retrieving price column from book model
            record = Book.objects.filter(purchase=0).values_list('price')
            record2 = Book.objects.filter(purchase=0)
            # stores all prices of books
            mylist = []
            #total amount of all books
            amount = 0
            # list of prices
            for x in record:
                mylist.append(x[0])
                # total amount
                amount += x[0]
            # debit card form 
            form = DebitCardForm(initial={"price":amount}) 
            content = {'form':form,'data':record2}
            return render(request,"debitcardform2.html",content) 
        # netbanking method
        elif payment_method == '2':
            # saving payment method number in session for further manipulation
            request.session['payment_method'] = payment_method
            # netbanking form
            form = NetBankingLoginForm()
            content = {'form':form}
            return render(request,"netbankingloginform2.html",content) 
        # upi method
        elif payment_method == '3':
            # saving payment method number in session for further manipulation
            request.session['payment_method'] = payment_method
            # retrieving price column from book model
            record = Book.objects.filter(purchase=0).values_list('price')
            # for diplaying list of books which user is about to buy
            record2 = Book.objects.filter(purchase=0)
            # stores all prices of books
            mylist = []
            #total amount of all books
            amount = 0
            # list of prices
            for x in record:
                mylist.append(x[0])
                # total amount
                amount += x[0]
            # prefilling input box with above book's price
            # initial -> attribute need dictionary
            # key must be same as the form label name
            # in this case form label name is `amount` hence key is also `amount`
            form = UpiTransactionDetails(initial={'amount':amount})
            content = {'form':form,'data':record2}
            return render(request,'upipaymentdetails2.html',content)
    else:
        form = PaymentOptionsForm()
        record = Book.objects.filter(purchase=0)
        content = {'form':form,'data':record}
        return render(request,'paymentmethods.html',content)

# PAYMENT PROCESSING (ALL BOOK)
def payment_2(request):
    if request.method == "POST":
        # this session method gets the session key
        payment_method =  request.session['payment_method'] 
        # debit card payment
        if payment_method == '1':
            try:
                # retrieving debit card form data
                name = request.POST['name']
                card_num = request.POST['debit_card_num']
                cvv = request.POST['cvv']
                # saving payment method details 
                # get_or_create() method will create object if does not exist
                # when purchase is done by same debit card this method won't create same entry again
                records = UserPaymentDetails.objects.get_or_create(name=name,debit_card_num=card_num,cvv=cvv,user_id=request.user.id)
                if records.count() > 1:
                    # updating book as purchased
                    records_2 = Book.objects.all().update(purchase=1,uid=request.user.id,borrow=0,cart=0)
                    return redirect('/')
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        # netbanking payment
        elif payment_method == '2':
            try:
                # updating book as purchased
                record2 = Book.objects.all().update(purchase=1,uid=request.user.id,borrow=0,cart=0)
                return redirect("/")
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        # upi payment
        elif payment_method == '3':
            try:
                # updating book as purchased
                record2 = Book.objects.all().update(purchase=1,uid=request.user.id,borrow=0,cart=0)
                return redirect("/")
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))

# TRANSACTION DETAILS (NETBANKING LOGIN HANDLER FOR ALL BOOKS)
def transaction_details_2(request):
    if request.method == 'POST':
        form = NetBankingLoginForm(request.POST)
        if form.is_valid():
            # retrieving form data
            uname = form.cleaned_data['username']
            upass = form.cleaned_data['password']
            # saving username & password in session for further manipulation
            request.session['uname'] = uname
            request.session['upass'] = upass
            # if username & password exists
            record = NetBankingDetails.objects.filter(username=uname,password=upass).exists()
            if record:
               # retrieving price column from book model
                record = Book.objects.all().values_list('price')
                record2 = Book.objects.all() 
                # stores all prices of books
                mylist = []
                #total amount of all books
                amount = 0
                # list of prices
                for x in record:
                    mylist.append(x[0])
                    # total amount
                    amount+=x[0]                   
                # prefilling input box with above book's price
                # initial -> attribute need dictionary
                # key must be same as the form label name
                # in this case form label name is `amount` hence key is also `amount`  
                form2 = NetBankingTransactionDetails(initial={'amount':amount})
                content = {'form':form2,'data':record2}
                return render(request,'netbanktransactiondetails2.html',content)
            else:
                form = NetBankingLoginForm()
                content = {'form':form,'err':'Invalid Username OR Password'}
                return render(request,'netbankingloginform2.html',content)

# FILTER BY AUTHOR (HOME)
def filter_by_author(request,authorname):
    # to show prices in price filter
    records = Book.objects.all().order_by('price')
    # to show data on table
    record = Book.objects.filter(author=authorname,borrow=0,purchase=0)
    # to show author names in author filter
    allrecords = Book.objects.all()
    content = {'data':record,'data2':records,'data3':allrecords}
    return render(request,'home.html',content)


#     return render(request,'home.html',content)

# FILTER BY PRICE (HOME)
def filter_by_price(request,price):
    # to show data on table
    record = Book.objects.filter(price__lte=price,borrow=0,purchase=0).order_by('price')
    # to show prices in price filter
    records = Book.objects.all().order_by('price')
    content = {'data':record,'data2':records}
    return render(request,'home.html',content)

# SORT IN ASCENDING ORDER
def ascending(request):
    # to show prices in price filter
    records = Book.objects.all().order_by('price')
    # to show data in ascending order
    record = Book.objects.all().order_by('price')
    content = {'data':record,'data2':records}
    return render(request,'home.html',content)

# SORT IN DESCENDING ORDER
def descending(request):
    # to show prices in price filter
    records = Book.objects.all().order_by('-price')
    # to show data in ascending order
    record = Book.objects.all().order_by('-price')
    content = {'data':record,'data2':records}
    return render(request,'home.html',content)

def update_profile(request):
    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            record = User.objects.filter(id=request.user.id).update(first_name=first_name,last_name=last_name,username=username,email=email)
            return redirect('/')
        else: 
            # if form input data is wrong show error message
            form = UserProfileUpdateForm()
            content = {'data':form,'err':"Failed To Update User Profile Details !"}
            return render(request,'updateprofile.html',content)
    else:
        form = UserProfileUpdateForm(initial={'first_name':request.user.first_name,'last_name':request.user.last_name,
                                              'username':request.user.username,'email':request.user.email})
        content = {'form':form}
        return render(request,'updateprofile.html',content)
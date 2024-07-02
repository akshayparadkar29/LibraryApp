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
from django.views import View


class StaticUrls(View):
    # GET METHODS
    def get(self,request,*args,**kwargs):
        # HOME PAGE (GET)
        if request.path == '/':
            records = Book.objects.all().order_by('price')
            records2 = Book.objects.all().values_list('purchase','borrow')
            purchase_count = 0
            borrow_count = 0
            for index in range(0,len(records2),1):
                if records2[index][0] == 1:
                    purchase_count += 1
                elif records2[index][1] == 1:
                    borrow_count += 1
            content = {'data':records,'data2':records,'total_record':len(records),'is_purchase':purchase_count}
            return render(request,'home.html',content)
        
        # REGISTER BOOK (GET)
        elif request.path == '/register-book':
            try:
                # if GET request show form
                form = BookForm()
                content = {'form':form}
                return render(request,'registerbook.html',content)
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # REGISTER USER (GET)
        elif request.path == '/register-user':
            try:
                # if GET request show form
                form = UserForm()
                content = {'data':form}
                return render(request,'registeruser.html',content)
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # USER LOGIN (GET)
        elif request.path == '/user-login':
            try:
                form = AuthenticationForm()
                content = {'data':form}
                return render(request,"userlogin.html",content)   
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # PROFILE PICTURE UPDATE (GET)
        elif request.path == '/profile-image':
            try:
                form = ImageForm()
                content = {'form':form}
                return render(request,'profileimageform.html',content)
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # USER DASHBOARD (GET)
        elif request.path == '/user-dashboard':
            try:
                # only logged-in user must see books borrowed OR purchased by him
                condition_1 = Q(uid=request.user.id)
                records = Book.objects.filter(condition_1) 
                record_count = len(records)
                # print("MY RECORDS COUNT ->",record_count)
                content = {'data':records,'record_count':record_count}
                return render(request,'userdash.html',content)
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # USER LOGOUT (GET)
        elif request.path == '/user-logout':
            try:
                # destroying sessions for current request
                # other sessions created by current user gets cleared
                logout(request)
                return redirect('/user-login')
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
         # CART (GET)
        elif request.path == '/my-cart':
            try:
                record = Book.objects.filter(cart=1,uid=request.user.id)
                record_count = record.count()
                content = {'data':record,'record_count':record_count}
                return render(request,'cart.html',content)
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # ADD BOOKS TO CART USER-DASHBOARD (GET)
        elif request.path == '/books-to-cart':
            try:
                records = Book.objects.filter(borrow=1,uid=request.user.id)
                records.update(cart=1,borrow=0)
                return redirect('/user-dashboard')
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))

        # ADD BOOKS TO CART HOMEPAGE (GET) 
        elif request.path == '/allbooks-to-cart':
            try:
                record = Book.objects.filter(purchase=0,borrow=0).update(cart=1,uid=request.user.id)
                return redirect('/')
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # REMOVE BOOKS FROM CART (GET)   
        elif request.path == '/remove-all-books':
            # filtering books added in cart
            record = Book.objects.filter(cart=1)
            if record.exists():
                # removing books from cart
                record.update(cart=0,uid=0)
                return redirect('/my-cart')
        
        # RETURN BOOKS (GET)
        elif request.path == '/return-all-books':
            try:
                record = Book.objects.filter(borrow=1,uid=request.user.id)
                record.update(borrow=0,uid=0)
                return redirect('/user-dashboard')
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # NET_BANKING REGISTRATION (GET) 
        elif request.path == '/netbanking-register-form':
            try:
                form = NetBankingRegisterForm()
                content = {'form':form}
                return render(request,'netbankingregisterform.html',content)
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # BORROW BOOKS HOME (GET)
        elif request.path == '/borrow-all-books':
            record = Book.objects.filter(purchase=0,cart=0,borrow=0).update(borrow=1,uid=request.user.id,purchase=0,cart=0)
            return redirect('/')
        
        # BORROW BOOKS CART (GET)
        elif request.path == '/borrow-all-books2':
            record = Book.objects.filter(purchase=0,cart=1).update(borrow=1,uid=request.user.id,purchase=0,cart=0)
            return redirect('/my-cart')
        
        # BUY BOOKS CART (GET)
        elif request.path == '/buy-all-books':
            form = PaymentOptionsForm()
            record = Book.objects.filter(purchase=0)
            content = {'form':form,'data':record}
            return render(request,'paymentmethods.html',content)
        
        # ASCENDING FILTER
        elif request.path == '/ascending':
            # to show prices in price filter
            records = Book.objects.all().order_by('price')
            # to show data in ascending order
            record = Book.objects.all().order_by('price')
            content = {'data':record,'data2':records}
            return render(request,'home.html',content)
        
        # DESCENDING FILTER
        elif request.path == '/descending':
            # to show prices in price filter
            records = Book.objects.all().order_by('-price')
            # to show data in ascending order
            record = Book.objects.all().order_by('-price')
            content = {'data':record,'data2':records}
            return render(request,'home.html',content)
        
        elif request.path == '/update-profile':
            form = UserProfileUpdateForm(initial={'first_name':request.user.first_name,'last_name':request.user.last_name,
                                              'username':request.user.username,'email':request.user.email})
            content = {'form':form}
            return render(request,'updateprofile.html',content)
            
            
#----------------------------------------------------------------------------------------------------------------
        
    # POST METHODS
    def post(self,request,*args,**kwargs):
        # REGISTER BOOK (POST)
        if request.path == '/register-book':
            try:
                form = BookForm(request.POST)
                if form.is_valid():
                    title = form.cleaned_data['title']
                    author = form.cleaned_data['author']
                    sdesc = form.cleaned_data['small_description']
                    price  = form.cleaned_data['price']
                    # setting table column values
                    records = Book.objects.get_or_create(title=title,author=author,sdesc=sdesc,price=price)
                    # redirecting to home page
                    return redirect('/')
                # if form data invalid
                else: 
                    try:
                        form = BookForm()
                        content = {'form':form,'err':'Failed To Register !'}
                        return render(request,'registerbook.html',content)
                    except Exception as e:
                        return HttpResponse("Error Occurred: {}".format(str(e),status=500))
            # error handling
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # REGISTER USER (POST)
        elif request.path == '/register-user':
            try:
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
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
            
        # USER LOGIN (POST)
        elif request.path == '/user-login':
            try:
                # AuthenticationForm() provides username & password fields
                # AuthenticationForm() takes 2 parameters  
                # request = request_object & variable = request.POST
                form = AuthenticationForm(request=request,data=request.POST)
                # If Form Valid
                if form.is_valid():
                    # retrieving username & password for double confirmation
                    # AuthenticationForm() use cleaned_data[] to retrieve form input values
                    # 'username' & 'password' are dictionary keys to which form input values are linked
                    user_name = form.cleaned_data['username']
                    user_pass = form.cleaned_data['password']
                    # double checking in auth_user table whether username & password exists
                    # authenticate() will check the auth_user table by default
                    user_exist = authenticate(username=user_name,password=user_pass)
                    # if exist
                    if user_exist:
                        # create session
                        login(request,user_exist)
                        return redirect('/user-dashboard')
                else:
                    # If Form Invalid
                    form = AuthenticationForm()
                    content = {'data':form,'err':"Invalid Username OR Password"}
                    return render(request,"userlogin.html",content)
            except Exception as e:
                return HttpResponse()
            
        # PROFILE PICTURE UPDATE (POST)
        elif request.path == '/profile-image':
            try:
                # extracting imageform data
                form = ImageForm(request.POST, request.FILES)
                if form.is_valid():
                    # extracting image
                    image = form.cleaned_data['image']
                    # if user updates same profile picture 
                    # checking if image exist
                    record = UserImage.objects.filter(image=image).exists()
                    # if same profile picture exist
                    if record:
                        return redirect('/')     
                    else: 
                        # when same user updates a different account picture 
                        # since we have defined OneToOne relationship in UserImage model
                        # we have to first delete existing account image of current user
                        user = request.user.id
                        # checking if image exist
                        exist = UserImage.objects.filter(user_id=user).exists()
                        # .values('image') -> return queryset of all images from UserImage model -> <QuerySet [{'image': '20220623_160508.jpg'}]>
                        # [0] -> returns first object from queryset -> {'image': '20220623_160508.jpg'}
                        # .get('image') -> returns the name of the image with extension -> '20220623_160508.jpg'
                        exist = UserImage.objects.filter(user_id=user).values('image')[0].get('image')
                        # deleting existing account image from images folder
                        os.remove(os.path.join(settings.MEDIA_ROOT,exist))
                        # delete existed account image of current user from database
                        UserImage.objects.filter(user_id=user).delete() 
                        # then update new account image of current user
                        record = UserImage.objects.get_or_create(image=image,user_id=user)
                        return redirect('/')  
                else:
                    # if form is invalid throw error
                    form = ImageForm()
                    content = {'form':form,'err':'Invalid File !'}
                    return render(request,'profileimageform.html',content)
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
            
        # NET BANKING LOGIN DATA VALIDATION (POST)
        elif request.path == '/transaction-details':
            if request.method == 'POST':
                try:
                    form = NetBankingLoginForm(request.POST)
                    if form.is_valid():
                        # retrieving form data
                        uname = form.cleaned_data['username']
                        upass = form.cleaned_data['password']
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
                            return render(request,'netbanktransactiondetails2.html',content)
                        else:
                            form = NetBankingLoginForm()
                            content = {'form':form,'err':'Invalid Username OR Password'}
                            return render(request,'netbankingloginform.html',content)
                except Exception as e:
                    return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # PAYMENT PROCESSING (POST)            
        elif request.path == '/payment':
            # Getting Session Value
            payment_method =  request.session['payment_method'] 
            # Debit Card Payment Processing
            if payment_method == '1':
                try:
                    # Debit Card Form Data
                    name = request.POST['name']
                    card_num = request.POST['debit_card_num']
                    cvv = request.POST['cvv']
                    # Current User Id 
                    uid = request.user.id
                    # Record Id
                    record_id = request.session['record_id']
                    # get_or_create() -> 'get' will retrieve the record if exist, 
                    # orelse it will create new reocord using 'create'
                    # If purchase is done using same Debit Card again, duplicate entry won't be created
                    records = UserPaymentDetails.objects.get_or_create(name=name,debit_card_num=card_num,cvv=cvv,user_id=uid)
                    # Updating Record
                    records_2 = Book.objects.filter(id=record_id)
                    records_2.update(purchase=1,uid=uid,borrow=0,cart=0)
                    return redirect('/') 
                except Exception as e:
                    return HttpResponse("Error Occurred: {}".format(str(e),status=500))
            # Net-Banking Payment Processing
            elif payment_method == '2':
                try:
                    # these session methods gets the session key & then deletes the key from session
                    uid = request.session['user_id']
                    record_id = request.session['record_id']
                    # saving payment method details 
                    record2 = Book.objects.filter(id=record_id)
                    record2.update(purchase=1,uid=uid,borrow=0)
                    return redirect("/")
                except Exception as e:
                    return HttpResponse("Error Occurred: {}".format(str(e),status=500))
            # Upi Payment Processing
            elif payment_method == '3':
                try:
                    # these session methods gets the session key 
                    uid = request.session['user_id']
                    # retrieving Book record based on record_id
                    record_id = request.session['record_id']
                    # updating book as purchased
                    record2 = Book.objects.filter(id=record_id)
                    record2.update(purchase=1,uid=uid,borrow=0)
                    return redirect("/")
                except Exception as e:
                    return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # NET-BANKING REGISTRATION (POST)
        elif request.path == '/netbanking-register-form':
            form = NetBankingRegisterForm(request.POST)
            if form.is_valid():
                try:
                    # retrieving form data
                    fname = form.cleaned_data['first_name']
                    lname = form.cleaned_data['last_name']
                    accnum = form.cleaned_data['account_number']
                    mobnum = form.cleaned_data['mobile_number']  
                    uname = form.cleaned_data['username']
                    upass = form.cleaned_data['password']
                
                    # getting user id 
                    user = request.user.id
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
                except Exception as e:
                    return HttpResponse("Error Occurred: {}".format(str(e),status=500))
            else:
                try:
                    # if form data is not valid show error message
                    form = NetBankingRegisterForm()
                    content = {'form':form,'err':'Registration Failed !'}
                    return render(request,'netbankingregisterform.html',content) 
                except Exception as e:
                    return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # BUY BOOKS CART (POST)        
        elif request.path == '/buy-all-books':
            # retrieving payment method number
            payment_method = request.POST['payment_methods']
            # debit card method
            if payment_method == '1':
                # saving payment method number in session for further manipulation
                request.session['payment_method'] = payment_method
                # retrieving price column from book model
                record = Book.objects.filter(purchase=0).values_list('price')
                record2 = Book.objects.filter(purchase=0)
                #total amount of all books
                amount = 0
                # list of prices
                for x in record:   
                    # total amount
                    amount += x[0]
                # debit card form 
                form = DebitCardForm(initial={"price":amount}) 
                content = {'form':form,'data':record2,'price':amount}
                return render(request,"debitcardform2.html",content) 
            # netbanking method
            elif payment_method == '2':
                # saving payment method number in session for further manipulation
                request.session['payment_method'] = payment_method
                # retrieving price column from book model
                record = Book.objects.filter(purchase=0).values_list('price')
                record2 = Book.objects.filter(purchase=0)
                #total amount of all books
                amount = 0
                # list of prices
                for x in record:   
                    # total amount
                    amount += x[0]
                request.session['total_price'] = amount
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
                #total amount of all books
                amount = 0
                # list of prices
                for x in record:
                    # total amount
                    amount += x[0]
                # prefilling input box with above book's price
                # initial -> attribute need dictionary
                # key must be same as the form label name
                # in this case form label name is `amount` hence key is also `amount`
                form = UpiTransactionDetails(initial={'amount':amount})
                content = {'form':form,'data':record2}
                return render(request,'upipaymentdetails2.html',content)
        
        # BOOKS PAYMENT PROCCESSING (POST)    
        elif request.path == '/payment-2':
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
                    print("Record Count-> ",len(records))
                    if len(records) > 1:
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
                
        # NETBANKING LOGIN HANDLER ALL BOOKS (POST)       
        elif request.path == '/transaction-details-2':
            try:
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
                        #total amount of all books
                        amount = 0
                        # list of prices
                        for x in record:
                            # total amount
                            amount += x[0]                   
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
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        elif request.path == '/update-profile':
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
       
#----------------------------------------------------------------------------------------------------------------

class DynamicUrls(View):
    # GET METHODS
    def get(self,request,*args,**kwargs):
        # BORROW BOOK (GET)
        if 'rid' in kwargs and request.path == f'/book-borrow/{self.kwargs['rid']}':
            try:
                # filtering book record based on bookid
                record = Book.objects.filter(id=self.kwargs['rid'])
                # updating above book record as borrowed
                record.update(borrow=1,uid=request.user.id,cart=0)
                return redirect('/')
            except Exception as e:
                return HttpResponse("Erorr Occurred: {}".format(str(e),status=500))
        
        # ADD BOOK TO CART (GET)
        elif 'rid' in kwargs and request.path == f'/add-to-cart/{self.kwargs['rid']}':
            try:
                record = Book.objects.filter(id=self.kwargs['rid'])
                record.update(cart=1,uid=request.user.id)
                return redirect('/')
            except Exception as e:
                return HttpResponse("Erorr Occurred: {}".format(str(e),status=500))
        
        # BORROW BOOK FROM CART (GET)
        elif 'rid' in kwargs and request.path == f'/borrow-from-cart/{self.kwargs['rid']}':
            try:
                # filtering book record based on bookid
                record = Book.objects.filter(id=self.kwargs['rid'])
                # updating above book record as borrowed
                record.update(borrow=1,uid=request.user.id,cart=0)
                return redirect('/my-cart')
            except Exception as e:
                return HttpResponse("Erorr Occurred: {}".format(str(e),status=500))
        
        # REMOVE BOOK FROM CART (GET)
        elif 'rid' in kwargs and request.path == f'/remove-from-cart/{self.kwargs['rid']}':
            try:
                record = Book.objects.filter(id=self.kwargs['rid'])
                record.update(cart=0,uid=0,borrow=0) 
                return redirect('/my-cart')
            except Exception as e:
                return HttpResponse("Erorr Occurred: {}".format(str(e),status=500))
        
        # RETURN BOOK DASHBOARD (GET)    
        elif 'rid' in kwargs and request.path == f'/book-return/{self.kwargs['rid']}':
            try:
                print("RETURN BOOK")
                # filtering book record based on bookid
                record = Book.objects.filter(id=self.kwargs['rid'])
                # updating above book record as returned
                record.update(borrow=0, uid=0)
                return redirect('/user-dashboard')
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))
        
        # BUY BOOK HOMEPAGE (GET)
        elif 'rid' in kwargs and request.path == f'/book-buy/{self.kwargs['rid']}':
            try:
                # Book Id
                record_id = self.kwargs['rid']
                # saving record_id & book_id in session for further manipulation
                request.session['record_id'] = record_id
                # payment method form
                form = PaymentOptionsForm()
                record = Book.objects.filter(id=record_id)
                content = {'form':form,'data':record}
                return render(request,'paymentmethods.html',content)
            except Exception as e:
                return HttpResponse("Error Occurred: {}".format(str(e),status=500))

        # AUTHOR FILTER (GET)
        elif 'authorname' in kwargs and request.path == f'/filter-by-author/{self.kwargs['authorname']}':
            # to show prices in price filter
            records = Book.objects.all().order_by('price')
            # to show data on table
            record = records.filter(author=self.kwargs['authorname'],borrow=0,purchase=0)
            # to show author names in author filter
            allrecords = Book.objects.all()
            content = {'data':record,'data2':records}
            return render(request,'home.html',content)
        
        # PRICE FILTER
        elif 'price' in kwargs and request.path == f'/filter-by-price/{self.kwargs['price']}':
                # to show data on table
                record = Book.objects.filter(price__lte=self.kwargs['price'],borrow=0,purchase=0).order_by('price')
                # to show prices in price filter
                records = Book.objects.all().order_by('price')
                content = {'data':record,'data2':records}
                return render(request,'home.html',content)
#-----------------------------------------------------------------------------------------------------

    def post(self,request,*args,**kwargs):
        # PAYMENT METHODS (POST)
        if 'rid' in kwargs and request.path == f'/book-buy/{self.kwargs['rid']}':
            # retrieving payment method number
            payment_method = request.POST['payment_methods']
            # debit card method
            if payment_method == '1':
                try:
                    # saving payment method number in session for further manipulation
                    request.session['payment_method'] = payment_method
                    record = Book.objects.filter(id=self.kwargs['rid'])
                    # debit card form
                    # initial = {} is used to prefill form inputs
                    form = DebitCardForm(initial={'price':record[0].price})
                    content = {'form':form,'data':record,'price':record[0].price}
                    return render(request,"debitcardform.html",content) 
                except Exception as e:
                    return HttpResponse("Error Occurred: {}".format(str(e),status=500)) 
           
            # netbanking method
            elif payment_method == '2':
                try:
                    # saving payment method number in session for further manipulation
                    request.session['payment_method'] = payment_method
                    # netbanking form
                    form = NetBankingLoginForm()
                    content = {'form':form}
                    return render(request,"netbankingloginform.html",content) 
                except Exception as e:
                    return HttpResponse("Error Occurred: {}".format(str(e),status=500))
                
            # upi method
            elif payment_method == '3':
                try:
                    # saving payment method number in session for further manipulation
                    request.session['payment_method'] = payment_method
                    # retrieving Book record based on record_id
                    record_id = request.session['record_id']
                    record = Book.objects.filter(id=record_id)
                    # prefilling input box with above book's price
                    # initial -> attribute need dictionary
                    # key must be same as the form label name
                    # in this case form label name is `amount` hence key is also `amount`
                    form = UpiTransactionDetails(initial={'amount':record[0].price})
                    record = Book.objects.filter(id=record_id)
                    content = {'form':form,'data':record}
                    return render(request,'upipaymentdetails.html',content)
                except Exception as e:
                    return HttpResponse("Error Occurred: {}".format(str(e),status=500))
                
#------------------------------------------------------------------------------------------------------------



def update_profile(request):
    if request.method == "POST":
        pass
    else:
        pass
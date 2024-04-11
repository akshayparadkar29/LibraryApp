from django.urls import path
from libapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name='home_page'),
    path('register-book',views.register_book,name='register_book_page'),
    path('register-user',views.register_user,name='register_user_page'),
    path('user-dashboard',views.user_dashboard),
    path('user-login',views.user_login),
    path('user-logout',views.user_logout),
    path('book-borrow/<rid>/<uid>',views.borrow_book), 
    path('borrow-all-books',views.borrow_all_books),
    path('borrow-all-books2',views.borrow_all_books2),
    path('borrow-from-cart/<rid>/<uid>',views.borrow_from_cart), 
    path('book-return/<rid>',views.return_book),
    path('return-all-books',views.return_all_books),
    path('book-buy/<rid>/<uid>',views.buy_book),
    path('buy-all-books',views.buy_all_books),
    path('remove-all-books',views.remove_all_books),
    path('update-profile',views.update_profile),
    path('books-to-cart',views.books_to_cart), 
    path('allbooks-to-cart',views.all_books_to_cart),
    path('netbanking-register-form',views.netbanking_register),
    path('transaction-details',views.transaction_details),
    path('transaction-details-2',views.transaction_details_2),
    path('payment',views.payment),
    path('payment-2',views.payment_2),
    path('my-cart',views.my_cart),    
    path('add-to-cart/<rid>/<uid>',views.add_to_cart),
    path('remove-from-cart/<rid>',views.remove_from_cart),
    path('profile-image',views.profile_image),
    path('filter-by-author/<authorname>',views.filter_by_author),
    path('filter-by-price/<price>',views.filter_by_price),
    path('ascending',views.ascending),
    path('descending',views.descending),
]   

# url settings for serving media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
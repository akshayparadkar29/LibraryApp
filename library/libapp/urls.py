from django.urls import path
from libapp import views
from django.conf import settings
from django.conf.urls.static import static
from libapp.views import StaticUrls,DynamicUrls

urlpatterns = [
    # Static Urls
    path('',StaticUrls.as_view(),name='home_page'),
    path('register-book',StaticUrls.as_view(),name='register_book_page'),
    path('register-user',StaticUrls.as_view(),name='register_user_page'),
    path('user-dashboard',StaticUrls.as_view()),
    path('user-login',StaticUrls.as_view()),
    path('user-logout',StaticUrls.as_view()),
    path('borrow-all-books',StaticUrls.as_view()),
    path('borrow-all-books2',StaticUrls.as_view()),
    path('return-all-books',StaticUrls.as_view()),
    path('buy-all-books',StaticUrls.as_view()),
    path('remove-all-books',StaticUrls.as_view()),
    path('update-profile',StaticUrls.as_view()),
    path('books-to-cart',views.StaticUrls.as_view()), 
    path('allbooks-to-cart',StaticUrls.as_view()),
    path('netbanking-register-form',StaticUrls.as_view()),
    path('transaction-details',StaticUrls.as_view()),
    path('transaction-details-2',StaticUrls.as_view()),
    path('payment',StaticUrls.as_view()),
    path('payment-2',StaticUrls.as_view()),
    path('my-cart',StaticUrls.as_view()),
    path('profile-image',StaticUrls.as_view()),
    path('ascending',StaticUrls.as_view()),
    path('descending',StaticUrls.as_view()),
    
    # Dynamic Urls
    path('book-borrow/<rid>',DynamicUrls.as_view()), 
    path('borrow-from-cart/<rid>',DynamicUrls.as_view()), 
    path('book-return/<rid>',DynamicUrls.as_view()),
    path('book-buy/<rid>',DynamicUrls.as_view()),
    path('add-to-cart/<rid>',DynamicUrls.as_view()),
    path('remove-from-cart/<rid>',DynamicUrls.as_view()),
    path('filter-by-author/<authorname>',DynamicUrls.as_view()),
    path('filter-by-price/<price>',DynamicUrls.as_view()),
    
]   

# url settings for serving media files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
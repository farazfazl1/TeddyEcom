from django.urls import path
from store import views

app_name = 'store'

urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail_url'),
    path('search/', views.search, name='search'),
    
    #path for reviews
    path('submit/review/<int:product_id>', views.submit_review, name='submit-review'),
]

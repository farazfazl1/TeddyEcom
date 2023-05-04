from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static
from django.conf import settings

admin.autodiscover()
admin.site.enable_nav_sidebar = False

urlpatterns = [
    path('admin/', admin.site.urls),
    # -----------------------------------
    path('', include('pages.urls')),
    # -----------------------------------
    path('category/', include('category.urls')),
    # -----------------------------------
    path('store/', include('store.urls')),
    # -----------------------------------
    path('cart/', include('carts.urls')),
    # -----------------------------------
    path('account/', include('accounts.urls')),
    # ------------------------------------
    path('orders/', include('orders.urls'))
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

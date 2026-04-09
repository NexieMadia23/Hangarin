from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Change 'admin.site.id' to 'admin.site.urls'
    path('admin/', admin.site.urls), 
    
    # The allauth patterns for Google/Github
    path('accounts/', include('allauth.urls')), 
    
    # Your main app
    path('', include('core.urls')), 

    path('', include('pwa.urls')),
]
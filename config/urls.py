from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Including the core URLs and allowing the app's internal namespacing
    path('', include('core.urls', namespace='core')), 
]
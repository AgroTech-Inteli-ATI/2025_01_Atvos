from django.urls import path, include

urlpatterns = [

    path('api/', include('travels.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path("users/", include("users.urls")),
]

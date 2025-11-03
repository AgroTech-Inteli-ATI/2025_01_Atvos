from django.urls import path

from users.views import login, register, get_user, delete_user, update_user

app_name = 'users'

urlpatterns = [
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('<int:user_id>', get_user, name='get'),
    path('update/<int:user_id>', update_user, name='update'),
    path('delete/<int:user_id>', delete_user, name='delete'),
]

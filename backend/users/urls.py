from django.urls import include, path
from recipes.views import FollowViewSet, favorites, shoping_list, subscriptions
from rest_framework.routers import DefaultRouter

app_name = 'users'

router_v1 = DefaultRouter()

router_v1.register('users', FollowViewSet, basename='users')


urlpatterns = [
    path('users/subscriptions/', subscriptions),
    path('users/favorites/', favorites),
    path('users/shoping_list/', shoping_list),
    path('', include('djoser.urls')),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

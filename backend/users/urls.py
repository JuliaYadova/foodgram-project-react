from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import FollowViewSet, subscriptions

app_name = 'users'

router_v1 = DefaultRouter()

router_v1.register('users', FollowViewSet, basename='users')


urlpatterns = [
    path('users/subscriptions/', subscriptions, name='subscriptions'),
    path('', include('djoser.urls')),
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

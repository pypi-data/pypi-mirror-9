from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib.auth.models import User, Group

admin.autodiscover()

from rest_framework import routers

from api.views import *

# Routers provide an easy way of automatically determining the URL conf
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'api/v1/dad/users', UserViewSet)
router.register(r'api/v1/dad/groups', GroupViewSet) 
router.register(r'api/v1/dad/profiles', ProfileViewSet) 
router.register(r'api/v1/dad/facilities', FacilityViewSet)  
router.register(r'api/v1/dad/affiliates', AffiliateViewSet) 
router.register(r'api/v1/dad/locations', LocationViewSet)    
router.register(r'api/v1/dad/addresses', AddressViewSet) 

router.register(r'api/v1/facilities', EmberFacilityViewSet)                              
router.register(r'api/v1/places', EmberPlaceViewSet)                                     
router.register(r'api/v1/cities', EmberCityViewSet)   
router.register(r'api/v1/states', EmberStateViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = patterns('',
     url(r'^$', 'api.views.home', name='home'),
     url(r'^', include(router.urls)),
     url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
     url(r'^secret', 'api.views.secret', name='secret'),
     url(r'^home?$', 'api.views.home', name='home'),
     url(r'^token', 'api.views.token', name='token'),      
     url(r'^procedure', 'api.views.procedure', name='procedure'),
     url(r'^testing', 'api.views.testing', name='testing'),      
     url(r'^export', 'api.views.export', name='export'),   
)

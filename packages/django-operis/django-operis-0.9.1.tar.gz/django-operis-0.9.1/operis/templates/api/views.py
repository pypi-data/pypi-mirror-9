import datetime
import StringIO
import xlsxwriter

from django.template.context import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_list_or_404, get_object_or_404, \
                             redirect, render
from django.utils.safestring import SafeString
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext as _  

from rest_framework import filters
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.renderers import XMLRenderer

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope, TokenHasScope

from login.models import *

from api.renderers import EmberJSONRenderer 
from api.filters import *
from api.serializers import *
from api.forms import *
from api.utils import WEEKDAYS_AS_STRING
from api.authentication import KeyAuthentication

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    model = User
    serializer_class = UserSerializer
    filter_fields = ['username','email',] 
    renderer_classes = (EmberJSONRenderer,XMLRenderer,)
    filter_backends = (SearchFilter,)
    search_fields = ['username','email',]
    queryset = User.objects.all()

class GroupViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['groups']
    model = Group
    serializer_class = GroupSerializer
    filter_fields = ['name',] 
    renderer_classes = (EmberJSONRenderer,XMLRenderer,)
    filter_backends = (SearchFilter,)
    search_fields = ['name']
    queryset = Group.objects.all()
    
class ProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    model = Profile
    serializer_class = ProfileSerializer
    filter_fields = ['first_name','last_name',] 
    renderer_classes = (EmberJSONRenderer,XMLRenderer,)
    filter_backends = (SearchFilter,)
    search_fields = ['first_name','last_name',]
    queryset = Profile.objects.all()

class AddressViewSet(viewsets.ModelViewSet):
    model = Address
    serializer_class = LimitAddressSerializer
    renderer_classes = (EmberJSONRenderer,XMLRenderer,)
    filter_backends = (AddressFilter,OrderingFilter,)
    search_fields = ['name',]
    queryset = Address.objects.using('ppfa_extranet_rep').all()
    
class AffiliateViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    model = Affiliate
    serializer_class = AffiliateSerializer
    renderer_classes = (EmberJSONRenderer,XMLRenderer,)
    filter_backends = (SearchFilter,)
    filter_fields = ['name',] 
    search_fields = ['name',]
    queryset = Affiliate.objects.using('ppfa_extranet_rep').all()

class LocationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    model = Location
    serializer_class = LocationSerializer
    renderer_classes = (EmberJSONRenderer,XMLRenderer,)
    filter_backends = (SearchFilter,)
    filter_fields = ['name',] 
    search_fields = ['location_name',]
    queryset = Location.objects.using('ppfa_extranet_rep').all()

class FacilityViewSet(viewsets.ModelViewSet):
    #authentication_classes = (KeyAuthentication,)
    #permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    permission_classes = [permissions.AllowAny]
    model = Facility
    serializer_class = FacilitySerializer
    renderer_classes = (EmberJSONRenderer,XMLRenderer,)
    filter_backends = (FacilityFilter,OrderingFilter,filters.SearchFilter,)
    ordering_fields = ('display_name', 'location__address__postal_code')
    ordering = ('display_name', 'location__address__postal_code', )
    search_fields = ('display_name',)
    queryset = Facility.objects.using('ppfa_extranet_rep').all()

class EmberStateViewSet(viewsets.ModelViewSet):
    #authentication_classes = (KeyAuthentication,)
    #permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    permission_classes = [permissions.AllowAny]
    model = StateLocation
    serializer_class = EmberStateSerializer
    renderer_classes = (EmberJSONRenderer,XMLRenderer,)
    filter_backends = (OrderingFilter,filters.SearchFilter,)
    ordering_fields = ('state_name','state_abbr',)
    ordering = ('state_name','state_abbr', )
    search_fields = ('state_name','state_abbr',)
    queryset = StateLocation.objects.using('c5').all()
    
class EmberFacilityViewSet(viewsets.ModelViewSet):
    #authentication_classes = (KeyAuthentication,)
    #permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    permission_classes = [permissions.AllowAny]
    model = Facility
    serializer_class = EmberFacilitySerializer
    renderer_classes = (EmberJSONRenderer,)
    filter_backends = (FacilityFilter,OrderingFilter,filters.SearchFilter,)
    #ordering_fields = ('display_name', 'location__address__postal_code')
    #ordering = ('display_name', 'location__address__postal_code', )
    search_fields = ('display_name','location__address__city','location__address__state__state_abbr')
    queryset = Facility.objects.using('ppfa_extranet_rep').all()

class EmberPlaceViewSet(viewsets.ModelViewSet):
    #authentication_classes = (KeyAuthentication,)
    #permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    permission_classes = [permissions.AllowAny]
    model = ZipCode
    serializer_class = EmberPlaceSerializer
    renderer_classes = (EmberJSONRenderer,)
    filter_backends = (PlaceFilter,OrderingFilter,filters.SearchFilter,) 
    ordering = ('state', 'city', 'zip_code', )
    search_fields = ('zip_code','city','state','stateObject__state_name')
    queryset = ZipCode.objects.using('c5').all()

class EmberCityViewSet(viewsets.ModelViewSet):
    #authentication_classes = (KeyAuthentication,)
    #permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    permission_classes = [permissions.AllowAny]
    model = ZipIndex
    serializer_class = EmberCitySerializer
    renderer_classes = (EmberJSONRenderer,)
    filter_backends = (PlaceFilter,OrderingFilter,filters.SearchFilter,) 
    ordering = ('state', 'city', )
    search_fields = ('city','state')
    queryset = ZipIndex.objects.using('c5').all()
                        
def home(request):
    """
    page index
    """
    response_dict = {
        'ember_app_name': settings.EMBER_APP_NAME,
        'ember_env': SafeString(settings.EMBER_ENV),
    }
    
    term = ""
    results = []
       
    return render_to_response('home.html', { 'results':results,
                                             'settings': response_dict,
                                             'term': term,
                                             'location': "Home", }, 
            context_instance=RequestContext(request))

def token(request):
    """
    page index
    """
    
    response_dict = {
        'ember_app_name': settings.EMBER_APP_NAME,
        'ember_env': SafeString(settings.EMBER_ENV),
    }
    return render_to_response('token.html', { 'settings': response_dict,
                                              'location': "Token", }, 
            context_instance=RequestContext(request))

def procedure(request):
    """
    page index
    """
    
    """
    Use the following for a state search
    stateAbbr = 'NY'
    orderBy = str(1)
    
    results = FacilityProcedureDetails.objects.using('ppfa_extranet_rep').filter_by_procedure('usp_PPOL_getFacilityInfo_BasicByState', stateAbbr,orderBy)
    """
    
    """
    Use the following for a zip proximity search
    try:
        ziplocation = ZipCode.objects.using('c5').get(zip_code="10001")
    except ObjectDoesNotExist:                                                    
        return None            
    
    orderBy = str(1)
    centersToShow = str(10)
    startLong = ziplocation.longitude
    startLat = ziplocation.latitude
    
    results = FacilityProcedureDetails.objects.using('ppfa_extranet_rep').filter_by_procedure('usp_PPOL_getFacilityInfo_BasicByGeoCodes', startLat,startLong,centersToShow,orderBy)
    """
    results = Facility.objects.nearby_locations("10001", 100).filter(location__affiliate__b_archive=0,facility_details__Published=1,).exclude(location__address__geocode__latitude=0,location__address__geocode__longitude=0,)
    
    return render_to_response('procedure.html', { 
                                            'results': results }, 
            context_instance=RequestContext(request))
                        
def testing(request):
    """
    page index
    """
    
    results = []
    if request.method == 'POST':
        form = RequestForm(request.POST,user=request.user)
        if form.is_valid():
            results = form.save()
        else:
            pass
            #form._errors = ErrorList(['All fields are required, please check your data.'])
    else:
        form = RequestForm(user=request.user)
        
    return render_to_response('testing.html', { 
                                            'form':form,
                                            'results': results }, 
            context_instance=RequestContext(request))
            
def export(request):
    """
    Excel Export
    """
    # create a workbook in memory
    output = StringIO.StringIO()
    thedate = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    filename = 'test_'+thedate+'.xlsx'
    
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('PPFA Facilities')
    
    header_format = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': 'blue'})
    filename = 'affiliate_report_'+thedate+'.xlsx'
    headers = [ 'Name',
                'Affiliate ID', 
                'Facility ID', 
                'Display Name',
                'Address', 
                'Address 2', 
                'City', 
                'State Abbr', 
                'Postal Code', 
                'Phone', 
                'URL']
                
    for service in FACILITY_SERVICES:
            headers.append(_(service[0]))
     
    for day in WEEKDAYS_AS_STRING:
            headers.append(day)
       
    facility_list = Facility.objects.using('ppfa_extranet_rep').filter(location__affiliate__b_archive=0,facility_details__Published=1,).exclude(location__address__geocode__latitude=0,location__address__geocode__longitude=0,).order_by('name')
    
    j=0
    for header in headers:
        worksheet.write(0, j, header, header_format)
        j=j+1
    
    i=1
    
    for facility in facility_list:
        j=0
        worksheet.write(i, j, facility.name)
        j=j+1
        worksheet.write(i, j, facility.location.affiliate.affiliate_id)
        j=j+1
        worksheet.write(i, j, facility.facility_id)
        j=j+1
        worksheet.write(i, j, facility.display_name)
        j=j+1
        worksheet.write(i, j, facility.location.address.address)
        j=j+1
        worksheet.write(i, j, facility.location.address.address2)
        j=j+1
        worksheet.write(i, j, facility.location.address.city)
        j=j+1
        worksheet.write(i, j, facility.location.address.state.state_abbr)
        j=j+1
        worksheet.write(i, j, facility.location.address.postal_code)
        j=j+1
        worksheet.write(i, j, facility.main_line)
        j=j+1   
        worksheet.write(i, j, facility.facility_url)
        j=j+1
        for service in FACILITY_SERVICES:
            if getattr(facility.facility_details,service[1]):
                worksheet.write(i, j,"True")
            else:
                worksheet.write(i, j,"False")
            j=j+1
        for hour in facility.hours:
            worksheet.write(i, j, str(hour[1]))
            j=j+1
        i=i+1
    
    workbook.close()

    # construct response
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; filename=" + filename

    return response
    
    #return HttpResponse('Secret contents!', status=200)
    
@login_required()
def secret(request, *args, **kwargs):
    return HttpResponse('Secret contents!', status=200)

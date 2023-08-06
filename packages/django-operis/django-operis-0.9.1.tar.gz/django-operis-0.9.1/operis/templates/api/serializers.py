from datetime import time,tzinfo

from django.contrib.auth.models import User, Group
from django.db.models import F   
from django.conf import settings   
from django.contrib.auth.models import User, Group

from operis.utils import convert_friendly, convert

from rest_framework import pagination
from rest_framework import serializers

from api.fields import *
from api.models import *
from api.utils import WEEKDAYS_AS_STRING 

from login.models import *

class CustomMetaSerializer(serializers.Serializer):
    count = serializers.ReadOnlyField(source='paginator.count')
    num_pages = serializers.ReadOnlyField(source='paginator.num_pages')
    current_page = CurrentPageField(source='paginator')
    rpp = serializers.ReadOnlyField(source='paginator.per_page')
    
class CustomPaginationSerializer(pagination.BasePaginationSerializer):
    # Takes the page object as the source
    meta = CustomMetaSerializer(source='*')
    results_field = 'results'

class UserSerializer(serializers.ModelSerializer):
    
    id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    username = serializers.CharField(required=False,
                                  max_length=254)
    email = serializers.EmailField(required=False,
                                  max_length=254) 
        
    class Meta:
        model = User
        #meta_dict = dict()
        #meta_dict['foo'] = 'bar'
        resource_name = 'users'
        fields = ('id', 'username', 'email',)
        
    def restore_object(self, attrs, instance=None):
        if instance:
            # Update existing instance
            instance.username = attrs.get('username', instance.username)
            instance.email = attrs.get('email', instance.email)
            return instance

        # Create new instance
        return User(**attrs)
        
class GroupSerializer(serializers.ModelSerializer):
    
    id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    name = serializers.CharField(required=False,
                                  max_length=254)
        
    class Meta:
        model = Group
        #meta_dict = dict()
        #meta_dict['foo'] = 'bar'
        resource_name = 'groups'
        fields = ('id', 'name',)
        
class ProfileSerializer(serializers.ModelSerializer):
    
    id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    first_name = serializers.CharField(required=False,
                                  max_length=100)
    last_name = serializers.CharField(required=False,
                                  max_length=100)
    date_submitted =serializers.DateTimeField(required=False,
                                  format='iso-8601')
    approved = serializers.BooleanField(required=False)  
        
    class Meta:
        model = Profile
        #meta_dict = dict()
        #meta_dict['foo'] = 'bar'
        resource_name = 'profiles'
        fields = ('id', 'user', 'first_name', 'last_name', 'date_submitted', 'approved',)
        
class StateSerializer(serializers.ModelSerializer):
    
    state_id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    state_name =serializers.CharField(required=False,
                                  max_length=50)
    state_abbr = serializers.CharField(required=False,
                                  max_length=50)
    
    class Meta:
        model = State
        resource_name = 'states'
        fields = ('state_name', 'state_abbr',)      

class AngelGeoCodeSerializer(serializers.ModelSerializer):
    
    geoCodeID = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    
    class Meta:
        model = AngelGeoCode
        resource_name = 'geo_codes'
        fields = ('latitude', 'longitude',)

class LimitAddressSerializer(serializers.ModelSerializer):
    
    address_id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    address = serializers.CharField(required=False,
                                  max_length=100)
    address2 = serializers.CharField(required=False,
                                  max_length=100)
    city = serializers.CharField(required=False,
                                  max_length=100)
    #affiliate = serializers.PrimaryKeyRelatedField(read_only=True,)
    state = StateSerializer(read_only=True,)
    postal_code = serializers.CharField(required=False,
                                  max_length=50)
    geocode = AngelGeoCodeSerializer(read_only=True,)
    
    class Meta:
        model = Address
        resource_name = 'addresses'
        fields = ('address', 'address2','city','state','postal_code','geocode',)
                
class AddressSerializer(serializers.ModelSerializer):
    
    address_id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    address = serializers.CharField(required=False,
                                  max_length=100)
    address2 = serializers.CharField(required=False,
                                  max_length=100)
    city = serializers.CharField(required=False,
                                  max_length=100)
    #affiliate = serializers.PrimaryKeyRelatedField(read_only=True,)
    state = StateSerializer(read_only=True,)
    postal_code = serializers.CharField(required=False,
                                  max_length=50)
    geocode = AngelGeoCodeSerializer()
    proximity_miles = serializers.SerializerMethodField()

    def get_proximity_miles(self, obj):
        request = self.context['request']
        if 'p' in request.query_params:
            return obj.proximity(request.query_params['p'])
        return None
        
    class Meta:
        model = Address
        resource_name = 'addresses'
           
class AffiliateExtendedSerializer(serializers.ModelSerializer):
    
    affiliate_id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    short_name = serializers.CharField(required=False,style={'type': 'textarea'}) 
    on_portal = serializers.BooleanField(required=False)
    on_portal_directory = serializers.CharField(required=False,style={'type': 'textarea'}) 
    off_portal_url = serializers.CharField(required=False,style={'type': 'textarea'}) 
    archived = serializers.BooleanField(required=False)
    
    class Meta:
        model = AffiliateExtended
        resource_name = 'affiliate_extended'
                                     
class AffiliateSerializer(serializers.ModelSerializer):
    
    affiliate_id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    name = serializers.CharField(required=False,
                                  max_length=150)
    accreditation_status_id = serializers.IntegerField(required=False,)
    name = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    website = serializers.CharField(required=False)
    affiliate_education_website = serializers.CharField(required=False)
    turf = serializers.CharField(required=False,style={'type': 'textarea'}) 
    fiscal_year_end = serializers.DateTimeField(required=False)
    budget_size = serializers.FloatField(required=False)
    client_base_unduplicated = serializers.IntegerField(required=False)
    client_base_total = serializers.IntegerField(required=False)
    programs = serializers.CharField(required=False,style={'type': 'textarea'}) 
    best_practices = serializers.CharField(required=False,style={'type': 'textarea'}) 
    awards_and_grants = serializers.CharField(required=False,style={'type': 'textarea'}) 
    ancillary_organizations = serializers.CharField(required=False,style={'type': 'textarea'}) 
    funding_information = serializers.CharField(required=False,style={'type': 'textarea'}) 
    b_archive = serializers.BooleanField(required=False) 
    region = serializers.CharField(required=False)
    b_abortion_provider = serializers.BooleanField(required=False) 
    pp_since = serializers.DateTimeField(required=False)
    affiliate_tax_id = serializers.CharField(required=False)
    hist_begin_ts = serializers.DateTimeField(required=False)
    affiliate_extended = AffiliateExtendedSerializer(read_only=True,)
        
    class Meta:
        model = Affiliate
        resource_name = 'affiliates'  
        
class LocationSerializer(serializers.ModelSerializer):
    
    location_id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    location_name = serializers.CharField(required=False,
                                  max_length=150)
    affiliate = AffiliateSerializer()
    address = AddressSerializer(read_only=True,)
    
    class Meta:
        model = Location
        resource_name = 'locations'
        fields = ('location_id', 'location_name','affiliate','address',)

class DayOfWeekSerializer(serializers.ModelSerializer):
    
    day_of_week_name = serializers.CharField(required=False,max_length=50,) 
    
    class Meta:
        model = DayOfWeek
        resource_name = 'days_of_week'
     
class FacilityExtendedSerializer(serializers.ModelSerializer):
    
    facilityID = serializers.IntegerField(required=False)
    operatedBy = serializers.CharField(required=False,max_length=150) 
    alternateWebsite = serializers.CharField(required=False,max_length=150) 
    displayAbortion  = serializers.BooleanField(required=False)
    displayAbortionReferral  = serializers.BooleanField(required=False)
    displayBirthControl  = serializers.BooleanField(required=False)
    displayEmergencyContraception  = serializers.BooleanField(required=False)
    displayGeneralHealthcare  = serializers.BooleanField(required=False)
    displayHIVTesting  = serializers.BooleanField(required=False)
    displayHPVHepatitis  = serializers.BooleanField(required=False)
    displayLGBT  = serializers.BooleanField(required=False)
    displayMens  = serializers.BooleanField(required=False)
    displayPatientEducation  = serializers.BooleanField(required=False)
    displayPregnancyTesting  = serializers.BooleanField(required=False)
    displaySTDTtesting  = serializers.BooleanField(required=False)
    displayWomens  = serializers.BooleanField(required=False)
    displayDonationsText  = serializers.BooleanField(required=False)
    isGYT09Participant  = serializers.BooleanField(required=False)
    isCenterClosed  = serializers.BooleanField(required=False)
    abortionLicenseNum = serializers.CharField(required=False) 
    displayLawsAndRegulations  = serializers.BooleanField(required=False)
    displayPatientsUnder18Text  = serializers.BooleanField(required=False)
    isCenterClosedEmergency  = serializers.BooleanField(required=False)
    centerClosedEmergencyMessage = serializers.CharField(required=False,style={'type': 'textarea'}) 
    isGYT10Participant  = serializers.BooleanField(required=False)
    requestAppointmentAltText = serializers.CharField(required=False) 
    askExpertAltText = serializers.CharField(required=False) 
    orderBirthAltText = serializers.CharField(required=False) 
    orderContraceptionAltText = serializers.CharField(required=False) 
    refillBirthAltText = serializers.CharField(required=False) 
    accessFormsAltText = serializers.CharField(required=False) 
    makePaymentAltText = serializers.CharField(required=False) 
    requestAppointmentAltTextSp = serializers.CharField(required=False) 
    askExpertAltTextSp = serializers.CharField(required=False) 
    orderBirthAltTextSp = serializers.CharField(required=False) 
    orderContraceptionAltTextSp = serializers.CharField(required=False) 
    refillBirthAltTextSp = serializers.CharField(required=False) 
    accessFormsAltTextSp = serializers.CharField(required=False) 
    makePaymentAltTextSp = serializers.CharField(required=False) 
    isGYT11Participant  = serializers.BooleanField(required=False)
    isChatParticipantWeb  = serializers.BooleanField(required=False)
    isChatParticipantMobile  = serializers.BooleanField(required=False)
    titleAltText = serializers.CharField(required=False,style={'type': 'textarea'}) 
    titleAltTextSp = serializers.CharField(required=False,style={'type': 'textarea'}) 
    h1AltText = serializers.CharField(required=False,style={'type': 'textarea'}) 
    h1AltTextSp = serializers.CharField(required=False,style={'type': 'textarea'}) 
    metaDescriptionAltText = serializers.CharField(required=False,style={'type': 'textarea'}) 
    metaDescriptionAltTextSp = serializers.CharField(required=False,style={'type': 'textarea'}) 
    displayLGBTMessage  = serializers.BooleanField(required=False)
    infoAbortionReferral = serializers.CharField(required=False,style={'type': 'textarea'}) 
    centerDisclaimerMessage = serializers.CharField(required=False,style={'type': 'textarea'}) 
    displayCenterDisclaimerMessage  = serializers.BooleanField(required=False)
    customTrackingCode = serializers.CharField(required=False,style={'type': 'textarea'}) 
    
    class Meta:
        model = FacilityExtended
        resource_name = 'facility_extended'
               
class FacilityHoursSerializer(serializers.ModelSerializer):
    
    day_of_week = DayOfWeekSerializer(required=False)
    timeOpen = serializers.IntegerField(required=False,)
    timeClose = serializers.IntegerField(required=False,)
    notes = serializers.CharField(required=False,
                                  max_length=50)
        
    class Meta:
        model = FacilityHours
        resource_name = 'facility_hours'

class FacilityTypeSerializer(serializers.ModelSerializer):
    
    facility_type_id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field. 
    facility_level_code_id = serializers.IntegerField()
    facility_type_name = serializers.CharField(required=False,
                                  max_length=255)
    hist_begin_ts = serializers.DateTimeField() 
        
    class Meta:
        model = FacilityType
        resource_name = 'facility_types'
                          
class FacilityDetailSerializer(serializers.ModelSerializer):
    
    facility_detail_id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    offersAbortionServices = serializers.BooleanField()
    offersBirthControl = serializers.BooleanField() 
    offersEmergencyContraception  = serializers.BooleanField() 
    offersGeneralHealthCare  = serializers.BooleanField() 
    offersHIVTesting  = serializers.BooleanField() 
    offersHPVHepTesting  = serializers.BooleanField() 
    offersLGBTServices  = serializers.BooleanField() 
    offersMensServices  = serializers.BooleanField() 
    offersPatientEducation  = serializers.BooleanField() 
    offersPregnancyTesting  = serializers.BooleanField() 
    offersSTDTesting  = serializers.BooleanField() 
    offersWomensServices  = serializers.BooleanField() 
    hoursNotes = serializers.CharField(style={'type': 'textarea'})
    walkIn  = serializers.BooleanField() 
    walkInDescription = serializers.CharField(style={'type': 'textarea'})
    allAvailWalkIn  = serializers.BooleanField() 
    scheduledAppointmentOptionId = serializers.IntegerField()
    limitedScheduledAppointmentOptionId = serializers.IntegerField()
    walkInMorningAfterPill  = serializers.BooleanField() 
    teenClinic  = serializers.BooleanField() 
    teenClinicDescription = serializers.CharField(style={'type': 'textarea'})
    birthControlRefills  = serializers.BooleanField() 
    birthControlRefillsDescription = serializers.CharField(style={'type': 'textarea'})
    walkInOtherInformation = serializers.CharField(style={'type': 'textarea'})
    languageSpanish  = serializers.BooleanField() 
    languageFrench  = serializers.BooleanField() 
    languageOtherDescription = serializers.CharField(style={'type': 'textarea'})
    languageOtherByPhone  = serializers.BooleanField() 
    languageOtherByPhoneDescription = serializers.CharField(style={'type': 'textarea'})
    quickAppointments  = serializers.BooleanField() 
    quickAppointmentOptionId = serializers.IntegerField()
    quickApptCustomText = serializers.CharField(style={'type': 'textarea'})
    quickApptPillsNow  = serializers.BooleanField() 
    quickApptPlanNow  = serializers.BooleanField() 
    quickApptPillsByMail  = serializers.BooleanField() 
    quickApptBringForms  = serializers.BooleanField() 
    quickApptDevDisabledStaff  = serializers.BooleanField() 
    quickApptDevDisabledMaterials  = serializers.BooleanField() 
    quickApptPhysDisabledStaff  = serializers.BooleanField() 
    quickApptChildCareProvided  = serializers.BooleanField() 
    quickApptChildCareTimes = serializers.CharField(style={'type': 'textarea'})
    quickApptChildrenWaitingAgeLimit  = serializers.BooleanField() 
    quickApptChildrenWaitingAgeLimitAge = serializers.IntegerField()
    quickApptBabyTransport  = serializers.BooleanField() 
    quickApptArriveTime  = serializers.BooleanField() 
    quickApptArriveTimeMinutes = serializers.IntegerField()
    quickApptDirections = serializers.CharField(style={'type': 'textarea'})
    quickApptOtherInformation = serializers.CharField(style={'type': 'textarea'})
    insuranceInformationOptionId = serializers.IntegerField()
    insurancePlans = serializers.CharField(style={'type': 'textarea'})
    insuranceHealthCenterAllServiceAreas  = serializers.BooleanField() 
    insuranceHealthCenterHome  = serializers.BooleanField() 
    insuranceAbortionServices  = serializers.BooleanField() 
    insuranceBirthControl  = serializers.BooleanField() 
    insuranceEmergencyContraception  = serializers.BooleanField() 
    insuranceGeneralHealthCare  = serializers.BooleanField() 
    insuranceHIVTesting  = serializers.BooleanField() 
    insuranceHPVandHepatitisVaccines  = serializers.BooleanField() 
    insuranceLGBTServices  = serializers.BooleanField() 
    insuranceMensServices  = serializers.BooleanField() 
    insurancePatientEducation  = serializers.BooleanField() 
    insurancePregnancyTestingAndServices  = serializers.BooleanField() 
    insuranceSTDTestingAndTreatment  = serializers.BooleanField() 
    insuranceWomensServices  = serializers.BooleanField() 
    medicaidAccepted  = serializers.BooleanField() 
    medicaidHealthCenterAllServiceAreas  = serializers.BooleanField() 
    medicaidHealthCenterHome  = serializers.BooleanField() 
    medicaidAbortionServices  = serializers.BooleanField() 
    medicaidBirthControl  = serializers.BooleanField() 
    medicaidEmergencyContraception  = serializers.BooleanField() 
    medicaidGeneralHealthCare  = serializers.BooleanField() 
    medicaidHIVTesting  = serializers.BooleanField() 
    medicaidHPVandHepatitisVaccines  = serializers.BooleanField() 
    medicaidLGBTServices  = serializers.BooleanField() 
    medicaidMensServices  = serializers.BooleanField() 
    medicaidPatientEducation  = serializers.BooleanField() 
    medicaidPregnancyTestingAndServices  = serializers.BooleanField() 
    medicaidSTDTestingAndTreatment  = serializers.BooleanField() 
    medicaidWomensServices  = serializers.BooleanField() 
    spMedicaidAccepted  = serializers.BooleanField() 
    spMedicaidText = serializers.CharField(style={'type': 'textarea'})
    uninsuredAccepted  = serializers.BooleanField() 
    uninsuredBringDocuments  = serializers.BooleanField() 
    uninsuredBirthCertificate  = serializers.BooleanField() 
    uninsuredPayStub  = serializers.BooleanField() 
    uninsuredPhotoId  = serializers.BooleanField() 
    uninsuredProofOfResidence  = serializers.BooleanField() 
    uninsuredOtherDocuments = serializers.CharField(style={'type': 'textarea'})
    uninsuredHealthCenterAllServiceAreas  = serializers.BooleanField() 
    uninsuredHealthCenterHome  = serializers.BooleanField() 
    uninsuredAbortionServices  = serializers.BooleanField() 
    uninsuredBirthControl  = serializers.BooleanField() 
    uninsuredEmergencyContraception  = serializers.BooleanField() 
    uninsuredGeneralHealthCare  = serializers.BooleanField() 
    uninsuredHIVTesting  = serializers.BooleanField() 
    uninsuredHPVandHepatitisVaccines  = serializers.BooleanField() 
    uninsuredLGBTServices  = serializers.BooleanField() 
    uninsuredMensServices  = serializers.BooleanField() 
    uninsuredPatientEducation  = serializers.BooleanField() 
    uninsuredPregnancyTestingAndServices  = serializers.BooleanField() 
    uninsuredSTDTestingAndTreatment  = serializers.BooleanField() 
    uninsuredWomensServices  = serializers.BooleanField() 
    uninsuredFeesBasedOnIncome  = serializers.BooleanField() 
    uninsuredProofOfIncome  = serializers.BooleanField() 
    notTurnedAwayInabilityToPay  = serializers.BooleanField() 
    paymentInformationOptionId = serializers.IntegerField()
    paymentCash  = serializers.BooleanField() 
    paymentCheck  = serializers.BooleanField() 
    paymentCreditCard  = serializers.BooleanField() 
    paymentMoneyOrder  = serializers.BooleanField() 
    paymentOther = serializers.CharField(style={'type': 'textarea'})
    payExpTimeService  = serializers.BooleanField() 
    payExpHealthCenterAllServiceAreas  = serializers.BooleanField() 
    payExpHealthCenterHome  = serializers.BooleanField() 
    payExpAbortionServices  = serializers.BooleanField() 
    payExpBirthControl  = serializers.BooleanField() 
    payExpEmergencyContraception  = serializers.BooleanField() 
    payExpGeneralHealthCare  = serializers.BooleanField() 
    payExpHIVTesting  = serializers.BooleanField() 
    payExpHPVandHepatitisVaccines  = serializers.BooleanField() 
    payExpLGBTServices  = serializers.BooleanField() 
    payExpMensServices  = serializers.BooleanField() 
    payExpPatientEducation  = serializers.BooleanField() 
    payExpPregnancyTestingAndServices  = serializers.BooleanField() 
    payExpSTDTestingAndTreatment  = serializers.BooleanField() 
    payExpWomensServices  = serializers.BooleanField() 
    paymentPlansAvailManyServices  = serializers.BooleanField() 
    paymentOtherCreditCardLetter  = serializers.BooleanField() 
    paymentOtherSpecificInformation = serializers.CharField(style={'type': 'textarea'})
    paymentPromotionInformation = serializers.CharField(style={'type': 'textarea'})
    linkRequestAnAppointment = serializers.CharField(style={'type': 'textarea'})
    linkAskAnExpert = serializers.CharField(style={'type': 'textarea'})
    linkOrderBirthControl = serializers.CharField(style={'type': 'textarea'})
    linkOrderEmergencyContraception = serializers.CharField(style={'type': 'textarea'})
    linkRefillBirthControl = serializers.CharField(style={'type': 'textarea'})
    linkAccessOurMedicalForms = serializers.CharField(style={'type': 'textarea'})
    Published  = serializers.BooleanField() 
    LastPublishedDate = serializers.DateTimeField() 
    hist_begin_ts = serializers.DateTimeField() 
    linkMakeAPayment = serializers.CharField(style={'type': 'textarea'})
        
    class Meta:
        model = FacilityDetail
        resource_name = 'facility_detail'
                
class FacilitySerializer(serializers.ModelSerializer):
    
    facility_id = serializers.ReadOnlyField()  # Note: `Field` is an untyped read-only field.
    name = serializers.CharField(required=False,
                                  max_length=150)
    general_email = serializers.EmailField(required=False,
                                  max_length=150)
    facility_type = FacilityTypeSerializer()
    main_line = serializers.CharField(required=False,source="ppol_display_name")
    fax = serializers.CharField(required=False)
    notes = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    display_name = serializers.CharField(required=False)
    b_qualified_340b = serializers.BooleanField(required=False) 
    titlex340b_code = serializers.CharField(required=False)
    s318340b_code = serializers.CharField(required=False)
    plan_line = serializers.CharField(required=False)
    inside_line = serializers.CharField(required=False)
    stars_loc_code = serializers.CharField(required=False)
    facility_hour_list = serializers.SerializerMethodField()
     
    location = LocationSerializer(read_only=True,)
    facility_details = FacilityDetailSerializer(read_only=True,)
    facility_extended = FacilityExtendedSerializer(read_only=True,) 
    
    class Meta:
        model = Facility
        resource_name = 'facilities'
        fields = ('facility_id', 'name','general_email','facility_type', 
                    'main_line', 'fax', 'notes', 'name', 'display_name',
                    'b_qualified_340b', 'titlex340b_code', 's318340b_code',
                    'plan_line', 'inside_line',  
                    'stars_loc_code', 'location', 'facility_details', 
                    'facility_extended', 'facility_hour_list', )                    
        
    def get_facility_hour_list(self,obj):
        
        result = []
        for day in obj.hours:
            
            item = {}
            item["day_of_week"] = WEEKDAYS_AS_STRING[day[0]]
            
            if day[1]:
                item["start_time_as_string"] = day[1].startTimeAsString
                item["end_time_as_string"] = day[1].endTimeAsString     
                item["start_time"] = day[1].startTime
                item["end_time"] = day[1].endTime
            else:
                item["start_time_as_string"] = None
                item["end_time_as_string"] = None
                item["start_time"] = None
                item["end_time"] = None
            
            result.append(item)
            
        return result
        #return [("monday","10:00","11:00")]
        
class EmberFacilitySerializer(serializers.ModelSerializer):
    
    latlong = None
    
    id = serializers.ReadOnlyField(source="facility_id")  # Note: `Field` is an untyped read-only field.
    facility_id = serializers.IntegerField()
    location_id = serializers.IntegerField(source="location.location_id")
    name = serializers.CharField(required=False,
                                  max_length=150)
    general_email = serializers.EmailField(required=False,
                                  max_length=150)
    name = serializers.CharField(required=False)
    display_name = serializers.CharField(required=False)
    address = serializers.CharField(source="location.address.address")
    address2 = serializers.CharField(source="location.address.address2")
    city = serializers.CharField(source="location.address.city")
    state = serializers.CharField(source="location.address.state.state_abbr")
    postal_code = serializers.CharField(source="location.address.postal_code")
    main_line = serializers.CharField(required=False,source="ppol_display_name")
    fax = serializers.CharField(required=False)
    
    proximity = serializers.SerializerMethodField(required=False)
    latitude = serializers.FloatField(source="location.address.geocode.latitude")
    longitude = serializers.FloatField(source="location.address.geocode.longitude")
    facility_hour_list = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    oas = serializers.BooleanField(source="is_oas")
    
    class Meta:
        model = Facility
        resource_name = 'facilities'
        fields = ('id', 'facility_id', 'location_id', 'name','display_name','general_email',
                    'address','address2','city','state','postal_code',
                    'main_line','fax','proximity','latitude','longitude',
                    'facility_hour_list','services','oas',)                    
        
    def get_proximity(self,obj):
        #if not self.latlong:
        #    self,latlong = obj.lat_and_long
        
        if hasattr(obj,'proximity'):
            return obj.proximity
        else:
            return None
    
    
    def get_latitude(self,obj):
        #if not self.latlong:
        #    self,latlong = obj.lat_and_long
        
        return obj.lat_and_long[0]
    
    def get_longitude(self,obj):
        #if not self.latlong:
        #    self,latlong = obj.lat_and_long
        
        return obj.lat_and_long[1]
            
    def get_facility_hour_list(self,obj):
        
        result = []
        for day in obj.hours:

            item = {}
            item["day_of_week"] = WEEKDAYS_AS_STRING[day[0]]
            
            if day[1]:
                item["start_time_as_string"] = day[1].startTimeAsString
                item["end_time_as_string"] = day[1].endTimeAsString     
                item["start_time"] = day[1].startTime
                item["end_time"] = day[1].endTime
            else:
                item["start_time_as_string"] = None
                item["end_time_as_string"] = None
                item["start_time"] = None
                item["end_time"] = None
            
            result.append(item)
            
        return result
        
    def get_services(self,obj):
        
        return obj.services
        
class EmberPlaceSerializer(serializers.ModelSerializer):
    
    city = serializers.SerializerMethodField()
    state_name = serializers.CharField(source="stateObject.state_name")
    
    class Meta:
        model = ZipCode
        #meta_dict = dict()
        #meta_dict['foo'] = 'bar'
        resource_name = 'places'
    
    def get_city(self,obj):
        return obj.city.title()
        
class EmberCitySerializer(serializers.ModelSerializer):
    
    city = serializers.SerializerMethodField()
    
    class Meta:
        model = ZipIndex
        resource_name = 'cities'
    
    def get_city(self,obj):
        return obj.city.title()
        
class EmberStateSerializer(serializers.ModelSerializer):
    
    id = serializers.ReadOnlyField(source="state_id")  # Note: `Field` is an untyped read-only field.
    name = serializers.CharField(required=False,
                                  max_length=50, source="state_name")
    abbr = serializers.CharField(required=False,
                                  max_length=50, source="state_abbr")
    zip_code = serializers.CharField(required=False,
                                  max_length=5)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    zoom = serializers.IntegerField()
    
    class Meta:
        model = State
        resource_name = 'states'
        fields = ('id','name', 'abbr', 'zip_code', 'latitude', 'longitude', 'zoom', )   
    
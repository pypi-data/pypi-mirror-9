from rest_framework.test import APIClient
from datetime import datetime

from django.utils import timezone 

class OperisTestClient(APIClient):

    def get_iteration_string(self,iteration=None):
        if not iteration:
            return ""
        return str(iteration)
        
    def generate_test_data(self,fields,iteration=None,omit_id=True):
        item = {}
        for field in fields:
            if field['name'] == 'id' and omit_id:
                continue
            item[field['name']] = self.generate_field_data(field,iteration)
        return item
            
    def generate_field_data(self,field,iteration=None):
        """
        'AutoField', 'BLANK_CHOICE_DASH', 'BigIntegerField', 'BinaryField',
        'BooleanField', 'CharField', 'CommaSeparatedIntegerField', 'DateField',
        'DateTimeField', 'DecimalField', 'EmailField', 'Empty', 'Field',
        'FieldDoesNotExist', 'FilePathField', 'FloatField',
        'GenericIPAddressField', 'IPAddressField', 'IntegerField', 'NOT_PROVIDED',
        'NullBooleanField', 'PositiveIntegerField', 'PositiveSmallIntegerField',
        'SlugField', 'SmallIntegerField', 'TextField', 'TimeField', 'URLField',
        """
        
        if field['class'] == 'EmailField':
            return "test%s@test.com" % self.get_iteration_string(iteration)
        elif field['class'] == 'IntegerField':
            return 1
        elif field['class'] == 'CharField':
            return "test%s" % self.get_iteration_string(iteration)
        elif field['class'] == 'DateTimeField':
            value = str(timezone.now().isoformat())
            if value.endswith('+00:00'):
                value = value[:-6] + 'Z'
            return value
        elif field['class'] == 'ForeignKey':
            #We've created fixtures with PK 1 elsewhere
            return 1
        else:
            return None

    
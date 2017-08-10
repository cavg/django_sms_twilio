from django.shortcuts import render
from django.http import HttpResponse
from .models import SMS
from django.views.decorators.csrf import csrf_exempt
import logging
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


# 'SmsStatus': ['sent'], 'MessageSid': ['SM5b22787151274748a3c2f9d4a8f762e9'], 'MessageStatus': ['sent'], 'ApiVersion': ['2010-04-01'], 'SmsSid': ['SM5b22787151274748a3c2f9d4a8f762e9'], 'From': ['+56964590279'], 'To': ['+56951074530'], 'AccountSid': ['AC8acd164ef4c16be2293b2d2fde61b02c']
@csrf_exempt
def callback(request):
    sms = get_object_or_404(SMS, sid=request.POST['MessageSid'])
    sms.status = request.POST['MessageStatus']
    sms.save()
    return HttpResponse(status=204)

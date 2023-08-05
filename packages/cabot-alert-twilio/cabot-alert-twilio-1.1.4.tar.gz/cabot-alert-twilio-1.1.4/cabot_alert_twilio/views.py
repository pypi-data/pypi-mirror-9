from django.http import HttpResponse
from cabot.cabotapp.models import Service
from django.template import Context, Template
from twilio.rest import TwilioRestClient
from twilio import twiml

telephone_template = "This is an urgent message from Arachnys monitoring. Service \"{{ service.name }}\" is erroring. Please check Cabot urgently."

def telephone_alert_twiml_callback(service):
    c = Context({'service': service})
    t = Template(telephone_template).render(c)
    r = twiml.Response()
    r.say(t, voice='woman')
    r.hangup()
    return r

def twiml_callback(request, service_id):
    service = Service.objects.get(id=service_id)
    twiml = telephone_alert_twiml_callback(service)
    return HttpResponse(twiml, content_type='application/xml')
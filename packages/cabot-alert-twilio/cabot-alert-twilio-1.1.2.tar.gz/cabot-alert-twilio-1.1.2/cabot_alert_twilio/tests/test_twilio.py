from cabot.cabotapp.tests.tests_basic import LocalTestCase
from mock import Mock, patch

from cabot.cabotapp.models import UserProfile, Service
from cabot_alert_twilio import models
from cabot.cabotapp.alert import update_alert_plugins


class TestTwilioAlerts(LocalTestCase):
    def setUp(self):
        super(TestTwilioAlerts, self).setUp()

        self.user_profile = UserProfile(user=self.user)
        self.user_profile.save()
        self.service.users_to_notify.add(self.user)
        self.service.save()

        self.twilio_user_data = models.TwilioUserData(
            phone_number="0123456789",
            user = self.user_profile,
            title= models.TwilioUserData.name
            )
        self.twilio_user_data.save()

        update_alert_plugins()
        self.sms_alert = models.TwilioSMS.objects.get(title=models.TwilioSMS.name)
        self.sms_alert.save()
        self.phone_alert = models.TwilioPhoneCall.objects.get(title=models.TwilioPhoneCall.name)
        self.phone_alert.save()

        self.service.alerts.add(self.sms_alert)
        self.service.alerts.add(self.phone_alert)
        self.service.save()
        self.service.update_status()


    def test_model_attributes(self):
        self.assertEqual(self.service.users_to_notify.all().count(), 1)
        self.assertEqual(self.service.users_to_notify.get(pk=1).username, self.user.username)

        self.assertEqual(self.service.alerts.all().count(), 2)

    def test_phone_number_save(self):
        self.twilio_user_data.phone_number = "+1234567890"
        self.twilio_user_data.save()
        self.assertEqual(self.twilio_user_data.phone_number, "1234567890")
        self.twilio_user_data.phone_number = "1234567890"
        self.twilio_user_data.save()
        self.assertEqual(self.twilio_user_data.phone_number, "1234567890")

    @patch('cabot_alert_twilio.models.client')
    def test_sms_alert(self, fake_send_sms):

        # Alerting only happens with critical
        self.service.old_overall_status = Service.PASSING_STATUS
        self.service.overall_status = Service.CRITICAL_STATUS

        self.service.alert()
        fake_send_sms.assert_called_with("ayy")

    @patch('cabot_alert_twilio.models')
    def test_phone_alert(self, fake_phone_call):
        self.service.old_overall_status = Service.PASSING_STATUS
        self.service.overall_status = Service.CRITICAL_STATUS
        self.service.alert()



    # @patch('cabot_alert_email.models.send_mail')
    # def test_failure_alert(self, fake_send_mail):
    #     # Most recent failed
    #     self.service.overall_status = Service.CALCULATED_FAILING_STATUS
    #     self.service.old_overall_status = Service.PASSING_STATUS
    #     self.service.save()
    #     self.service.alert()
    #     fake_send_mail.assert_called_with(message=u'Service Service http://localhost/service/1/ alerting with status: failing.\n\nCHECKS FAILING:\n\nPassing checks:\n  PASSING - Graphite Check - Type: Metric check - Importance: Error\n  PASSING - Http Check - Type: HTTP check - Importance: Critical\n  PASSING - Jenkins Check - Type: Jenkins check - Importance: Error\n\n\n', subject='failing status for service: Service', recipient_list=[u'test@userprofile.co.uk'], from_email='Cabot <cabot@example.com>')
    #     
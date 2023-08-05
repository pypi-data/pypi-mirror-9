from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from ..compat import get_user_model
from ..models import create_notice_type, NoticeSetting, NoticeType
from ..views import notice_settings

from . import get_backend_id


class TestViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username="test_user", email="test@user.com", password="123456")

    def test_notice_settings(self):
        create_notice_type("label_1", "display", "description")
        notice_type_1 = NoticeType.objects.get(label="label_1")
        create_notice_type("label_2", "display", "description")
        notice_type_2 = NoticeType.objects.get(label="label_2")
        email_id = get_backend_id("email")
        setting = NoticeSetting.for_user(self.user, notice_type_2, email_id)
        setting.send = False
        setting.save()
        url = reverse("notification_notice_settings")
        request = self.factory.get(url)
        request.user = self.user
        response = notice_settings(request)
        self.assertEqual(response.status_code, 200)  # pylint: disable-msg=E1103

        post_data = {
            "label_2_{}".format(email_id): "on",
        }
        request = self.factory.post(url, data=post_data)
        request.user = self.user
        response = notice_settings(request)
        self.assertEqual(response.status_code, 302)  # pylint: disable-msg=E1103
        self.assertFalse(NoticeSetting.for_user(self.user, notice_type_1, email_id).send)
        self.assertTrue(NoticeSetting.for_user(self.user, notice_type_2, email_id).send)

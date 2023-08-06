# from django.test import TestCase
# from elasticsearch_dsl.connections import connections
# from djes.management.commands.sync_es import get_indexes, sync_index


# class BaseIndexableTestCase(TestCase):
#     """A TestCase which handles setup and teardown of elasticsearch indexes."""

#     def setUp(self):
#         self.es = connections.get_connection("default")
#         self.indexes = get_indexes()

#         for index in list(self.indexes):
#             self.es.indices.delete_alias("{}_*".format(index), "_all", ignore=[404])
#             self.es.indices.delete("{}_*".format(index), ignore=[404])

#         for index, body in self.indexes.items():
#             sync_index(index, body)

#     def tearDown(self):
#         for index in list(self.indexes):
#             self.es.indices.delete_alias("{}_*".format(index), "_all", ignore=[404])
#             self.es.indices.delete("{}_*".format(index), ignore=[404])


import json
import random

from six import PY3
from elastimorphic.tests.base import BaseIndexableTestCase
from elastimorphic.models import polymorphic_indexable_registry
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from model_mommy import mommy
from rest_framework.test import APIClient

from bulbs.content.models import Content


def make_content(*args, **kwargs):
    if "make_m2m" not in kwargs:
        kwargs["make_m2m"] = True

    if len(args) == 1:
        klass = args[0]
    else:
        models = polymorphic_indexable_registry.families[Content]
        model_keys = [key for key in models.keys() if key != "content_content"]
        key = random.choice(model_keys)
        klass = polymorphic_indexable_registry.all_models[key]

    content = mommy.make(klass, **kwargs)
    return content


class JsonEncoder(json.JSONEncoder):
    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        iso = _iso_datetime(value)
        if iso:
            return iso
        if not PY3 and isinstance(value, str):
            return unicode(value, errors='replace')  # TODO: Be stricter.
        if isinstance(value, set):
            return list(value)
        return super(JsonEncoder, self).default(value)


def _iso_datetime(value):
    """
    If value appears to be something datetime-like, return it in ISO format.

    Otherwise, return None.
    """
    if hasattr(value, 'strftime'):
        if hasattr(value, 'hour'):
            return value.isoformat()
        else:
            return '%sT00:00:00' % value.isoformat()


class BaseAPITestCase(BaseIndexableTestCase):
    """A base test case, allowing tearDown and setUp of the ES index"""

    def setUp(self):
        super(BaseAPITestCase, self).setUp()
        User = get_user_model()
        admin = self.admin = User.objects.create_user("admin", "tech@theonion.com", "secret")
        admin.is_staff = True
        admin.save()
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=admin)
        # reverse("content-detail")

    def give_permissions(self):
        publish_perm = Permission.objects.get(codename="publish_content")
        change_perm = Permission.objects.get(codename="change_content")
        promote_perm = Permission.objects.get(codename="promote_content")
        self.admin.user_permissions.add(publish_perm, change_perm, promote_perm)

    def give_author_permissions(self):
        publish_perm = Permission.objects.get(codename="publish_own_content")
        self.admin.user_permissions.add(publish_perm)

    def remove_permissions(self):
        self.admin.user_permissions.clear()

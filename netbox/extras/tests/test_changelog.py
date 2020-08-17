from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import status

from dcim.models import Site
from extras.choices import *
from extras.models import CustomField, CustomFieldValue, ObjectChange, Tag
from utilities.testing import APITestCase


class ChangeLogTest(APITestCase):

    def setUp(self):
        super().setUp()

        # Create a custom field on the Site model
        ct = ContentType.objects.get_for_model(Site)
        cf = CustomField(
            type=CustomFieldTypeChoices.TYPE_TEXT,
            name='my_field',
            required=False
        )
        cf.save()
        cf.obj_type.set([ct])

        # Create some tags
        tags = (
            Tag(name='Tag 1', slug='tag-1'),
            Tag(name='Tag 2', slug='tag-2'),
            Tag(name='Tag 3', slug='tag-3'),
        )
        Tag.objects.bulk_create(tags)

    def test_create_object(self):
        data = {
            'name': 'Test Site 1',
            'slug': 'test-site-1',
            'custom_fields': {
                'my_field': 'ABC'
            },
            'tags': [
                {'name': 'Tag 1'},
                {'name': 'Tag 2'},
            ]
        }
        self.assertEqual(ObjectChange.objects.count(), 0)
        url = reverse('dcim-api:site-list')
        self.add_permissions('dcim.add_site')

        response = self.client.post(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_201_CREATED)

        site = Site.objects.get(pk=response.data['id'])
        # First OC is the creation; second is the tags update
        oc_list = ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk
        ).order_by('pk')
        self.assertEqual(oc_list[0].changed_object, site)
        self.assertEqual(oc_list[0].action, ObjectChangeActionChoices.ACTION_CREATE)
        self.assertEqual(oc_list[0].object_data['custom_fields'], data['custom_fields'])
        self.assertEqual(oc_list[1].action, ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(oc_list[1].object_data['tags'], ['Tag 1', 'Tag 2'])

    def test_update_object(self):
        site = Site(name='Test Site 1', slug='test-site-1')
        site.save()

        data = {
            'name': 'Test Site X',
            'slug': 'test-site-x',
            'custom_fields': {
                'my_field': 'DEF'
            },
            'tags': [
                {'name': 'Tag 3'}
            ]
        }
        self.assertEqual(ObjectChange.objects.count(), 0)
        self.add_permissions('dcim.change_site')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})

        response = self.client.put(url, data, format='json', **self.header)
        self.assertHttpStatus(response, status.HTTP_200_OK)

        site = Site.objects.get(pk=response.data['id'])
        # Get only the most recent OC
        oc = ObjectChange.objects.filter(
            changed_object_type=ContentType.objects.get_for_model(Site),
            changed_object_id=site.pk
        ).first()
        self.assertEqual(oc.changed_object, site)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_UPDATE)
        self.assertEqual(oc.object_data['custom_fields'], data['custom_fields'])
        self.assertEqual(oc.object_data['tags'], ['Tag 3'])

    def test_delete_object(self):
        site = Site(
            name='Test Site 1',
            slug='test-site-1'
        )
        site.save()
        site.tags.set(*Tag.objects.all()[:2])
        CustomFieldValue.objects.create(
            field=CustomField.objects.get(name='my_field'),
            obj=site,
            value='ABC'
        )
        self.assertEqual(ObjectChange.objects.count(), 0)
        self.add_permissions('dcim.delete_site')
        url = reverse('dcim-api:site-detail', kwargs={'pk': site.pk})

        response = self.client.delete(url, **self.header)
        self.assertHttpStatus(response, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Site.objects.count(), 0)

        oc = ObjectChange.objects.first()
        self.assertEqual(oc.changed_object, None)
        self.assertEqual(oc.object_repr, site.name)
        self.assertEqual(oc.action, ObjectChangeActionChoices.ACTION_DELETE)
        self.assertEqual(oc.object_data['custom_fields'], {'my_field': 'ABC'})
        self.assertEqual(oc.object_data['tags'], ['Tag 1', 'Tag 2'])

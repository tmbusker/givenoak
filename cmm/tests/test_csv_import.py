from os import path
import pytest

from django.test import Client
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from ..models import IMPORT_CSV, AuthUser
from givenoak.settings import BASE_DIR

@pytest.fixture(name='app_site')
def fixture_app_site() -> str:
    """app site"""
    return "cmmSite"

@pytest.fixture(name='app_label')
def fixture_app_label() -> str:
    """app label"""
    return "cmm"

@pytest.fixture(name='model_name')
def fixture_model_name() -> str:
    """mode name"""
    return "shikuchoson"

@pytest.fixture(name='csv_import_url')
def fixture_csv_import_url(app_site, app_label, model_name):
    """reverse url"""
    return reverse('admin:' + '_'.join([app_label, model_name, 'csv_import']), current_app = app_site)

@pytest.fixture(name='importer')
@pytest.mark.django_db()
def fixture_importer(app_label, model_name):
    """import user"""
    importer, _ = AuthUser.objects.get_or_create(username='importer', is_superuser=False, is_staff=True, is_active=True)
    content_type, _ = ContentType.objects.get_or_create(app_label=app_label, model=model_name)
    # view_shikuchoson権限はログインに必要
    view_permission, _ = Permission.objects.get_or_create(content_type=content_type, codename='view_' + model_name)
    import_permission, _ = Permission.objects.get_or_create(content_type=content_type,
                                                            codename=IMPORT_CSV + '_' + model_name)
    add_permission, _ = Permission.objects.get_or_create(content_type=content_type, codename='add_' + model_name)
    change_permission, _ = Permission.objects.get_or_create(content_type=content_type, codename='change_' + model_name)
    delete_permission, _ = Permission.objects.get_or_create(content_type=content_type, codename='delete_' + model_name)
    importer.user_permissions.add(view_permission, import_permission, add_permission, change_permission,
                                  delete_permission)
    return importer

@pytest.mark.django_db()
def test_importer(importer):
    """test import user"""
    assert importer.username == 'importer'
    assert 'view_shikuchoson' in [up.codename for up in importer.user_permissions.all()]
    assert 'import_csv_shikuchoson' in [up.codename for up in importer.user_permissions.all()]

@pytest.fixture(name='import_client')
@pytest.mark.django_db()
def fixture_import_client(importer):
    """import client"""
    client = Client()
    client.force_login(importer)
    return client

# @pytest.mark.skip
@pytest.mark.django_db()
def test_reverse_url(import_client, csv_import_url):
    """reverse url"""
    response = import_client.get(csv_import_url)
    assert csv_import_url == '/commonsite/cmm/shikuchoson/csv_import/'
    assert response.status_code == 200

@pytest.mark.django_db()
def test_import_csv(import_client, csv_import_url):
    """import csv"""
    csv_file = path.join(BASE_DIR.parent, 'yutools/cmm_data/000730858_市区町村12.csv')
    with open(csv_file, encoding='utf-8') as file:
        data = {'name': 'shikuchoson', 'attachment': file}
        response = import_client.post(csv_import_url, format='multipart', data=data)
        assert response.status_code == 200
        # assert Shikuchoson.objects.count() > 0

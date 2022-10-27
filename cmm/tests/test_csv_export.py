from urllib.parse import quote
import pytest
from django.test import Client
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from ..models import AuthUser, EXPORT_CSV

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

@pytest.fixture(name='changelist_url')
def fixture_changelist_url(app_site, app_label, model_name):
    """reverse url"""
    return reverse('admin:' + '_'.join([app_label, model_name, 'changelist']), current_app = app_site)

@pytest.fixture(name='exporter')
@pytest.mark.django_db()
def fixture_exporter(app_label, model_name):
    """export user"""
    exporter, _ = AuthUser.objects.get_or_create(username='exporter', is_superuser=False, is_staff=True, is_active=True)
    content_type, _ = ContentType.objects.get_or_create(app_label=app_label, model=model_name)
    # view_shikuchoson権限はログインに必要
    view_permission, _ = Permission.objects.get_or_create(content_type=content_type, codename='view_' + model_name)
    export_permission, _ = Permission.objects.get_or_create(content_type=content_type, 
                                                            codename=EXPORT_CSV + '_' + model_name)
    exporter.user_permissions.add(view_permission, export_permission)
    return exporter

@pytest.mark.django_db()
def test_exporter(exporter):
    """export user"""
    assert exporter.username == 'exporter'
    assert 'view_shikuchoson' in [up.codename for up in exporter.user_permissions.all()]
    assert 'export_csv_shikuchoson' in [up.codename for up in exporter.user_permissions.all()]

@pytest.fixture(name='export_client')
def fixture_export_client(exporter):
    """export client"""
    client = Client()
    client.force_login(exporter)
    return client

# @pytest.mark.skip
@pytest.mark.django_db()
def test_reverse_url(export_client, changelist_url):
    """reverse url"""
    # ログインユーザーがView権限を持っていれば、follow=Trueは必要なし
    # response = export_client.get(changelist_url, follow=True)
    response = export_client.get(changelist_url)
    assert changelist_url == '/commonsite/cmm/shikuchoson/'
    assert response.status_code == 200

@pytest.mark.django_db()
def test_export_csv_get(export_client, changelist_url):
    """export csv"""
    data = {'action': 'export_csv'}
    # ここはなぜかfollow=Trueを外すと、response.status_codeが302になる
    response = export_client.get(changelist_url, data, follow=True)
    assert response.status_code == 200
    assert response.headers.get('Content-Type') == "text/html; charset=utf-8"

@pytest.mark.django_db()
def test_export_csv_post_superuser(admin_user, changelist_url):
    """super user post csv"""
    client = Client()
    client.force_login(admin_user)
    data = {'action': 'export_csv', '_selected_action':['1', '2', '3']}
    response = client.post(changelist_url, data)
    assert response.status_code == 200
    assert response.headers.get('Content-Type') == "text/csv; charset=UTF-8"
    # assert response.headers.get('Content-Disposition') == "attachment; filename=" + quote('市区町村.csv')

@pytest.mark.django_db()
def test_export_csv_post_exporter(export_client, changelist_url):
    """export user post csv"""
    data = {'action': 'export_csv', '_selected_action':['1', '2', '3']}
    response = export_client.post(changelist_url, data)
    assert response.status_code == 200
    assert response.headers.get('Content-Type') == "text/csv; charset=UTF-8"
    # assert response.headers.get('Content-Disposition') == "attachment; filename=" + quote('市区町村.csv')

from django.contrib.auth import get_user_model
from rest_framework import status
from app.models import Category, Transaction
import pytest
from model_bakery import baker
from rest_framework.authtoken.models import Token



User = get_user_model()


@pytest.fixture
def authenticate(api_client):
    def authenticate_user(is_staff=False):
        user = User.objects.create(username="testuser", is_staff=is_staff)
        api_client.force_authenticate(user=user)
        return user

    return authenticate_user


@pytest.mark.django_db
class TestTransaction:
    endpoint = "/v1/transaction/"

    def test_if_unauthorized_user_create_returns_401(self, api_client):
        res = api_client.post(
            self.endpoint, {"title": "a", "category": "income", "amount": 100}
        )

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_all_users_get_returns_200(self, api_client):

        res = api_client.get(self.endpoint)

        assert res.status_code == status.HTTP_200_OK

    def test_if_unauthorized_user_get_item_returns_404(self, api_client):
        res = api_client.get(f"{self.endpoint}1/")

        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_if_unauthorized_user_update_returns_404(self, api_client):
        res = api_client.patch(
            f"{self.endpoint}1/", {"title": "a", "category": "income", "amount": 100}
        )

        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_if_unauthorized_user_delete_returns_404(self, api_client):
        res = api_client.patch(
            f"{self.endpoint}1/",
        )

        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_if_authenticate_user_create_returns_201(self, authenticate, api_client):
        user = authenticate()

        category = baker.make(Category, name="income")
        res = api_client.post(
            self.endpoint,
            {"category": category.name, "title": "a", "amount": 100, "user": user.id},
        )

        assert res.status_code == status.HTTP_201_CREATED
        transaction = Transaction.objects.latest("created_at")
        assert transaction.user == user

    def test_if_authenticate_user_get_item_returns_200(self, authenticate, api_client):
        user = authenticate()

        obj = baker.make(Category, name="income")
        data = api_client.post(
            self.endpoint,
            {"category": obj.name, "title": "a", "amount": 100, "user": user.id},
        )
        res = api_client.get(f"{self.endpoint}{data.data['id']}/")
        assert res.status_code == status.HTTP_200_OK

    def test_if_authenticate_user_patch_returns_200(self, authenticate, api_client):
        user = authenticate()

        obj = baker.make(Category, name="income")
        data = api_client.post(
            self.endpoint,
            {"category": obj.name, "title": "a", "amount": 100, "user": user.id},
        )

        api_client.patch(f"{self.endpoint}3/", {"title": "b"})
        res = api_client.get(f"{self.endpoint}{data.data['id']}/")
        assert res.data["title"] == "b"

    def test_if_authenticate_user_delete_returns_204(self, authenticate, api_client):
        user = authenticate()

        obj = baker.make(Category, name="income")
        data = api_client.post(
            self.endpoint,
            {"category": obj.name, "title": "a", "amount": 100, "user": user.id},
        )

        res = api_client.delete(f"{self.endpoint}{data.data['id']}/")
        assert res.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestAuth:

    def test_if_anonymous_register_returns_201(self, api_client):
        url = '/v1/register/'

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        }
        res = api_client.post(url, data)
        
        
        assert res.status_code == status.HTTP_201_CREATED

    def test_if_registered_user_login_returns_200(self, api_client):
        url = '/v1/login/'
        
        User.objects.create_user(username='testuser',email='test@example.com', password='testpassword')
        token_key = Token.generate_key()
        
        data = {
            "email": "test@example.com",
            "password": "testpassword",
        }
        
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token_key)
        res = api_client.post(url, data)
        
        assert res.status_code == status.HTTP_200_OK
        assert 'token' in res.data

    

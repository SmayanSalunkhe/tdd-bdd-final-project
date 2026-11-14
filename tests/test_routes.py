"""Tests for the Product REST API."""
import logging
import os
import unittest
from decimal import Decimal

from service import app
from service.common import status
from service.models import Category, Product, db, init_db
from tests.factories import ProductFactory

DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///test.db")
BASE_URL = "/products"


class TestProductRoutes(unittest.TestCase):
    """Exercise Product API CRUD and query endpoints."""

    @classmethod
    def setUpClass(cls):
        app.config.update(
            TESTING=True,
            DEBUG=False,
            SQLALCHEMY_DATABASE_URI=DATABASE_URI,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def setUp(self):
        self.client = app.test_client()
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _payload(self, **overrides):
        product = ProductFactory(**overrides)
        return product.serialize()

    def _create_products(self, count=1):
        created = []
        for _ in range(count):
            response = self.client.post(BASE_URL, json=self._payload())
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created.append(response.get_json())
        return created

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Catalog Administration", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["message"], "OK")

    def test_create_product(self):
        payload = self._payload(name="Fedora")
        response = self.client.post(BASE_URL, json=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.get_json()
        self.assertEqual(data["name"], "Fedora")
        self.assertTrue(response.headers.get("Location", "").endswith(f"/products/{data['id']}"))

    def test_create_product_with_no_name(self):
        payload = self._payload()
        del payload["name"]
        response = self.client.post(BASE_URL, json=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        response = self.client.post(BASE_URL, data="bad data")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        response = self.client.post(BASE_URL, data="{}", content_type="text/plain")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_read_a_product(self):
        product = self._create_products()[0]
        response = self.client.get(f"{BASE_URL}/{product['id']}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["id"], product["id"])

    def test_read_nonexistent_product(self):
        response = self.client.get(f"{BASE_URL}/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_a_product(self):
        product = self._create_products()[0]
        payload = dict(product, description="Updated description")
        response = self.client.put(f"{BASE_URL}/{product['id']}", json=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.get_json()["description"], "Updated description")

    def test_update_nonexistent_product(self):
        response = self.client.put(f"{BASE_URL}/99999", json=self._payload())
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_a_product(self):
        product = self._create_products()[0]
        response = self.client.delete(f"{BASE_URL}/{product['id']}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(f"{BASE_URL}/{product['id']}").status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_product(self):
        response = self.client.delete(f"{BASE_URL}/99999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_all_products(self):
        self._create_products(3)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.get_json()), 3)

    def test_list_products_by_name(self):
        self.client.post(BASE_URL, json=self._payload(name="Fedora"))
        self.client.post(BASE_URL, json=self._payload(name="Boot"))
        response = self.client.get(BASE_URL, query_string={"name": "Fedora"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["name"] for item in response.get_json()], ["Fedora"])

    def test_list_products_by_category(self):
        self.client.post(BASE_URL, json=self._payload(category=Category.FOOD))
        response = self.client.get(BASE_URL, query_string={"category": "FOOD"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(item["category"] == "FOOD" for item in response.get_json()))

    def test_list_products_by_availability(self):
        self.client.post(BASE_URL, json=self._payload(available=True))
        self.client.post(BASE_URL, json=self._payload(available=False))
        response = self.client.get(BASE_URL, query_string={"available": "true"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(item["available"] is True for item in response.get_json()))

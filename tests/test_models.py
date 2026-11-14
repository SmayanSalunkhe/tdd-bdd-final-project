"""Unit tests for the Product model."""
import logging
import os
import unittest
from decimal import Decimal

from service import app
from service.models import Category, DataValidationError, Product, db
from tests.factories import ProductFactory

DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///test.db")


class TestProductModel(unittest.TestCase):
    """Test cases for Product model persistence and queries."""

    @classmethod
    def setUpClass(cls):
        app.config.update(
            TESTING=True,
            DEBUG=False,
            SQLALCHEMY_DATABASE_URI=DATABASE_URI,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def setUp(self):
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def test_create_a_product(self):
        product = Product(name="Fedora", description="A red hat", price=12.50,
                          available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertIsNone(product.id)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertTrue(product.available)
        self.assertEqual(Decimal(product.price), Decimal("12.50"))
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        self.assertEqual(Product.all(), [])
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        stored = Product.find(product.id)
        self.assertEqual(stored.name, product.name)

    def test_read_a_product(self):
        """It should Read a Product by ID."""
        product = ProductFactory()
        product.create()
        found = Product.find(product.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)

    def test_update_a_product(self):
        """It should Update an existing Product."""
        product = ProductFactory()
        product.create()
        product.description = "Updated description"
        product.update()
        found = Product.find(product.id)
        self.assertEqual(found.description, "Updated description")

    def test_update_product_without_id_raises_error(self):
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.update()

    def test_delete_a_product(self):
        """It should Delete a Product."""
        product = ProductFactory()
        product.create()
        product_id = product.id
        product.delete()
        self.assertIsNone(Product.find(product_id))

    def test_list_all_products(self):
        """It should List all Products."""
        products = ProductFactory.create_batch(3)
        for product in products:
            product.id = None
            product.create()
        self.assertEqual(len(Product.all()), 3)

    def test_find_by_name(self):
        """It should Find Products by name."""
        product = ProductFactory(name="Fedora")
        product.create()
        self.assertEqual(Product.find_by_name("Fedora").first().id, product.id)

    def test_find_by_category(self):
        """It should Find Products by category."""
        product = ProductFactory(category=Category.FOOD)
        product.create()
        self.assertEqual(Product.find_by_category(Category.FOOD).first().id, product.id)

    def test_find_by_availability(self):
        """It should Find Products by availability."""
        product = ProductFactory(available=False)
        product.create()
        self.assertEqual(Product.find_by_availability(False).first().id, product.id)

    def test_serialize_and_deserialize(self):
        product = ProductFactory()
        data = product.serialize()
        new_product = Product().deserialize(data)
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.category, product.category)

    def test_deserialize_missing_name_raises_error(self):
        with self.assertRaises(DataValidationError):
            Product().deserialize({"description": "Missing fields"})


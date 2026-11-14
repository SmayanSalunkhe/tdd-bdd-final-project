# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
# Licensed under the Apache License, Version 2.0

"""Factory for creating fake Product objects in tests."""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal

from service.models import Category, Product


class ProductFactory(factory.Factory):
    """Creates fake products for testing."""

    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("word")
    description = factory.Faker("sentence")
    price = FuzzyDecimal(1.00, 500.00, precision=2)
    available = FuzzyChoice([True, False])
    category = FuzzyChoice(list(Category))

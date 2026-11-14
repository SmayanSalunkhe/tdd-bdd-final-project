"""Behave steps that load background Product data through the REST API."""
import requests
from behave import given

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("the following products")
def step_impl(context):
    """Delete existing products and load the table's products."""
    endpoint = f"{context.base_url}/products"
    response = requests.get(endpoint, timeout=10)
    assert response.status_code == HTTP_200_OK

    for product in response.json():
        response = requests.delete(f"{endpoint}/{product['id']}", timeout=10)
        assert response.status_code == HTTP_204_NO_CONTENT

    for row in context.table:
        payload = {
            "name": row["name"],
            "description": row["description"],
            "price": row["price"],
            "available": row["available"].strip().lower() == "true",
            "category": row["category"].upper(),
        }
        response = requests.post(endpoint, json=payload, timeout=10)
        assert response.status_code == HTTP_201_CREATED, response.text

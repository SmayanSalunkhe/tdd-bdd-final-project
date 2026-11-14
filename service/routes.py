######################################################################
# Product Store REST API
######################################################################
"""RESTful routes for Product resources."""
from flask import abort, jsonify, request, url_for

from service import app
from service.common import status
from service.models import Category, DataValidationError, Product


@app.route("/health")
def healthcheck():
    """Health check endpoint."""
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


@app.route("/")
def index():
    """Serve the product administration page."""
    return app.send_static_file("index.html")


def check_content_type(content_type):
    """Ensure the request has the expected Content-Type."""
    if request.headers.get("Content-Type") != content_type:
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            description=f"Content-Type must be {content_type}",
        )


@app.route("/products", methods=["POST"])
def create_products():
    """Create a product from the JSON request body."""
    check_content_type("application/json")
    data = request.get_json(silent=True)
    if not data:
        abort(status.HTTP_400_BAD_REQUEST, description="Invalid product data")
    try:
        product = Product().deserialize(data)
        product.create()
    except (DataValidationError, ValueError) as error:
        abort(status.HTTP_400_BAD_REQUEST, description=str(error))
    location_url = url_for("get_product", product_id=product.id, _external=True)
    return jsonify(product.serialize()), status.HTTP_201_CREATED, {"Location": location_url}


@app.route("/products", methods=["GET"])
def list_products():
    """List products, optionally filtered by name, category, or availability."""
    products = Product.all()
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")

    if name:
        products = Product.find_by_name(name)
    if category:
        try:
            category_value = Category[category.upper()]
        except KeyError:
            abort(status.HTTP_400_BAD_REQUEST, description=f"Invalid category: {category}")
        products = Product.find_by_category(category_value)
    if available is not None:
        if available.lower() not in ("true", "false"):
            abort(status.HTTP_400_BAD_REQUEST, description="available must be true or false")
        products = Product.find_by_availability(available.lower() == "true")

    return jsonify([product.serialize() for product in products]), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    """Read a product by its ID."""
    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, description=f"Product with id '{product_id}' was not found")
    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Update an existing product."""
    check_content_type("application/json")
    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, description=f"Product with id '{product_id}' was not found")
    data = request.get_json(silent=True)
    if not data:
        abort(status.HTTP_400_BAD_REQUEST, description="Invalid product data")
    try:
        product.deserialize(data)
        product.id = product_id
        product.update()
    except (DataValidationError, ValueError) as error:
        abort(status.HTTP_400_BAD_REQUEST, description=str(error))
    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Delete a product by its ID."""
    product = Product.find(product_id)
    if product is None:
        abort(status.HTTP_404_NOT_FOUND, description=f"Product with id '{product_id}' was not found")
    product.delete()
    return "", status.HTTP_204_NO_CONTENT

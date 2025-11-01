import pytest
from app.models import Product

def test_product_model():
    product = Product(
        name="Test Product",
        price=99.99,
        description="Test Description",
        category="Test Category"
    )
    
    assert product.name == "Test Product"
    assert product.price == 99.99
    assert product.description == "Test Description"
    assert product.category == "Test Category"
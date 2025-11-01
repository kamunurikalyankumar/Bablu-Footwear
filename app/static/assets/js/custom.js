// Custom JavaScript for Bablu Footwear E-commerce

$(document).ready(function() {
    // Load products on shop page
    if (window.location.pathname.includes('shop.html')) {
        loadProducts();
    }

    // Load featured products on index page
    if (window.location.pathname.includes('index.html') || window.location.pathname === '/') {
        loadFeaturedProducts();
    }

    // Update cart count
    updateCartCount();

    // Handle search
    $('#inputModalSearch, #inputMobileSearch').on('keypress', function(e) {
        if (e.which === 13) {
            const query = $(this).val();
            if (query) {
                searchProducts(query);
            }
        }
    });

    // Handle add to cart
    $(document).on('click', '.add-to-cart', function(e) {
        e.preventDefault();
        const $btn = $(this);
        const productId = $btn.data('product-id');
        
        if (!productId) {
            console.error('No product ID found on button:', $btn);
            alert('Could not add product to cart: Missing product ID');
            return;
        }

        console.log('Adding product to cart:', productId);
        
        // Disable button temporarily
        $btn.prop('disabled', true).text('Adding...');
        
        addToCart(productId, 1, false)
            .then(() => {
                $btn.text('Added!');
                setTimeout(() => {
                    $btn.prop('disabled', false).text('Add to Cart');
                }, 2000);
            })
            .catch(error => {
                console.error('Failed to add to cart:', error);
                $btn.prop('disabled', false).text('Add to Cart');
                alert('Failed to add item to cart. Please try again.');
            });
    });

    // Handle add to cart and buy now from product single page
    $('#add-to-cart-btn').on('click', function() {
        const productId = $('#product-id').val();
        const quantity = parseInt($('#product-quantity').val()) || 1;
        if (productId) {
            addToCart(productId, quantity);
        } else {
            alert('Product not found');
        }
    });

    $('#buy-now-btn').on('click', function() {
        const productId = $('#product-id').val();
        const quantity = parseInt($('#product-quantity').val()) || 1;
        if (productId) {
            addToCart(productId, quantity, true); // true indicates immediate checkout
        } else {
            alert('Product not found');
        }
    });

    // Handle user login/logout
    updateUserUI();

    // Handle quantity selector
    $('#decrease-qty').on('click', function() {
        let qty = parseInt($('#quantity-display').text());
        if (qty > 1) {
            qty--;
            $('#quantity-display').text(qty);
            $('#product-quantity').val(qty);
        }
    });

    $('#increase-qty').on('click', function() {
        let qty = parseInt($('#quantity-display').text());
        qty++;
        $('#quantity-display').text(qty);
        $('#product-quantity').val(qty);
    });

    // Handle size selection
    $('.size-btn').on('click', function() {
        $('.size-btn').removeClass('active');
        $(this).addClass('active');
        $('#product-size').val($(this).data('size'));
    });
});

function loadProducts() {
    $.ajax({
        url: '/api/products/',
        method: 'GET',
        success: function(products) {
            displayProducts(products, '#productsContainer');
        },
        error: function() {
            console.log('Failed to load products');
        }
    });
}

function loadFeaturedProducts() {
    console.log('Loading featured products...');
    $.ajax({
        url: '/api/products/',
        method: 'GET',
        success: function(products) {
            console.log('Received products:', products);
            if (!Array.isArray(products)) {
                console.error('Expected array of products, got:', typeof products);
                return;
            }
            const featured = products.slice(0, 3); // Get first 3 products as featured
            console.log('Featured products:', featured);
            displayProducts(featured, '#featuredProducts');
        },
        error: function(xhr, status, error) {
            console.error('Failed to load featured products:', {status, error, response: xhr.responseText});
            $('#featuredProducts').html(`
                <div class="col-12 text-center">
                    <p class="text-muted">Unable to load featured products at this time.</p>
                </div>
            `);
        }
    });
}

function displayProducts(products, container) {
    let html = '';
    products.forEach(product => {
        // Ensure we have a valid product ID (either from _id or id field)
        const productId = product.id || product._id;
        if (!productId) {
            console.error('Product missing ID:', product);
            return;
        }

        html += `
            <div class="col-12 col-md-4 mb-4">
                <div class="card h-100">
                    <a href="shop-single.html?id=${productId}">
                        <img src="${product.image_url || ''}" class="card-img-top" alt="${product.name}"
                             onerror="this.src='assets/img/default-product.jpg';">
                    </a>
                    <div class="card-body">
                        <ul class="list-unstyled d-flex justify-content-between">
                            <li>
                                <i class="text-warning fa fa-star"></i>
                                <i class="text-warning fa fa-star"></i>
                                <i class="text-warning fa fa-star"></i>
                                <i class="text-muted fa fa-star"></i>
                                <i class="text-muted fa fa-star"></i>
                            </li>
                            <li class="text-muted text-right">$${(product.price || 0).toFixed(2)}</li>
                        </ul>
                        <a href="shop-single.html?id=${productId}" class="h2 text-decoration-none text-dark">
                            ${product.name || 'Unnamed Product'}
                        </a>
                        <p class="card-text">
                            ${(product.description || 'No description available.').substring(0, 100)}...
                        </p>
                        <p class="text-muted">Stock: ${product.stock_quantity || 0}</p>
                        <button class="btn btn-success add-to-cart" data-product-id="${productId}">
                            ${product.stock_quantity > 0 ? 'Add to Cart' : 'Out of Stock'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    });
    $(container).html(html);
}

function searchProducts(query) {
    $.ajax({
        url: `/api/products/search?q=${encodeURIComponent(query)}`,
        method: 'GET',
        success: function(products) {
            displayProducts(products, '#productsContainer');
        },
        error: function() {
            console.log('Search failed');
        }
    });
}

function addToCart(productId, quantity = 1, buyNow = false) {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login to add items to cart');
        window.location.href = 'login.html';
        return;
    }

    $.ajax({
        url: '/api/cart/add',
        method: 'POST',
        contentType: 'application/json',
        headers: { 'Authorization': 'Bearer ' + token },
        data: JSON.stringify({ product_id: productId }),
        success: function() {
            updateCartCount();
            alert('Item added to cart!');
        },
        error: function(xhr) {
            alert(xhr.responseJSON.message || 'Failed to add item to cart');
        }
    });
}

function updateCartCount() {
    const token = localStorage.getItem('token');
    if (!token) return;

    $.ajax({
        url: '/api/cart/',
        method: 'GET',
        headers: { 'Authorization': 'Bearer ' + token },
        success: function(cart) {
            const count = cart.items.reduce((sum, item) => sum + item.quantity, 0);
            $('.fa-cart-arrow-down').next('.badge').text(count);
        },
        error: function() {
            console.log('Failed to update cart count');
        }
    });
}

function updateUserUI() {
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user') || '{}');

    if (token && user.username) {
        $('.fa-user').next('.badge').text(user.username);
        // Add logout option
        $('.fa-user').parent().attr('href', '#').on('click', function(e) {
            e.preventDefault();
            logout();
        });
    } else {
        $('.fa-user').next('.badge').text('+99');
        $('.fa-user').parent().attr('href', 'login.html');
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

function addToCartByName(productName, quantity) {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login to add items to cart');
        window.location.href = 'login.html';
        return;
    }

    // First get product by name
    $.ajax({
        url: `/api/products/by-name/${encodeURIComponent(productName)}`,
        method: 'GET',
        success: function(product) {
            // Now add to cart using the product ID
            $.ajax({
                url: '/api/cart/add',
                method: 'POST',
                contentType: 'application/json',
                headers: { 'Authorization': 'Bearer ' + token },
                data: JSON.stringify({ product_id: product.id, quantity: parseInt(quantity) }),
                success: function() {
                    updateCartCount();
                    alert('Item added to cart!');
                },
                error: function(xhr) {
                    alert(xhr.responseJSON.message || 'Failed to add item to cart');
                }
            });
        },
        error: function(xhr) {
            alert('Product not found');
        }
    });
}

function addToCartWithQuantity(productId, quantity, callback) {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Please login to add items to cart');
        window.location.href = 'login.html';
        return;
    }

    $.ajax({
        url: '/api/cart/add',
        method: 'POST',
        contentType: 'application/json',
        headers: { 'Authorization': 'Bearer ' + token },
        data: JSON.stringify({ product_id: productId, quantity: quantity }),
        success: function() {
            updateCartCount();
            alert('Item added to cart!');
            if (callback) callback();
        },
        error: function(xhr) {
            alert(xhr.responseJSON.message || 'Failed to add item to cart');
        }
    });
}

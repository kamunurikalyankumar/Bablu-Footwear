// Cart functionality

function addToCart(productId, quantity = 1, buyNow = false) {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/login.html';
        return;
    }

    // Ensure we have a valid product ID
    if (!productId) {
        console.error('No product ID provided');
        showMessage('Error: Product ID is missing', 'error');
        return;
    }

    console.log('Adding to cart:', { productId, quantity, buyNow });

    $.ajax({
        url: '/api/cart/add',
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            product_id: productId,
            quantity: quantity
        }),
        success: function(response) {
            updateCartCount();
            if (buyNow) {
                window.location.href = '/cart.html?checkout=true';
            } else {
                showMessage('Item added to cart!', 'success');
            }
        },
        error: function(xhr) {
            if (xhr.status === 401) {
                window.location.href = '/login.html';
            } else {
                showMessage('Failed to add item to cart. ' + (xhr.responseJSON?.message || ''), 'error');
            }
        }
    });
}

function updateCartCount() {
    const token = localStorage.getItem('token');
    if (!token) {
        $('.cart-count').text('0');
        return;
    }

    $.ajax({
        url: '/api/cart/',
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        success: function(response) {
            let itemCount = 0;
            if (response.items) {
                itemCount = response.items.reduce((total, item) => total + item.quantity, 0);
            }
            $('.cart-count').text(itemCount);
        },
        error: function() {
            $('.cart-count').text('0');
        }
    });
}

function showMessage(message, type = 'success') {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    // Remove any existing alerts
    $('.alert').remove();
    
    // Add the new alert at the top of the page
    $('body').prepend(alertHtml);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        $('.alert').alert('close');
    }, 3000);
}

// Load product details on shop-single page
function loadProductDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');
    
    if (!productId) {
        showMessage('Product not found', 'error');
        return;
    }

    $.ajax({
        url: `/api/products/${productId}`,
        method: 'GET',
        success: function(product) {
            // Update product details
            $('#product-id').val(product.id); // Changed from _id to id
            $('.display-4').text(product.name);
            $('.h2.text-muted').text(`$${product.price.toFixed(2)}`);
            $('#main-product-image').attr('src', product.image_url);
            $('.text-muted p').text(product.description);
            
            // Update stock info
            if (product.stock_quantity <= 0) {
                $('#add-to-cart-btn, #buy-now-btn').prop('disabled', true);
                showMessage('This product is out of stock', 'error');
            }

            // Log for debugging
            console.log('Product loaded:', product);
            console.log('Product ID set to:', product.id);
        },
        error: function(xhr) {
            console.error('Error loading product:', xhr);
            showMessage('Failed to load product details', 'error');
        }
    });
}

    // Initialize cart functionality when document is ready
$(document).ready(function() {
    updateCartCount();
    
    // If we're on the shop-single page, load product details
    if (window.location.pathname.includes('shop-single.html')) {
        loadProductDetails();
    }

    // Handle Add to Cart button click
    $('#add-to-cart-btn').on('click', function() {
        const productId = $('#product-id').val();
        const quantity = parseInt($('#quantity-display').text()) || 1;
        console.log('Add to cart clicked:', { productId, quantity });
        
        if (!productId) {
            showMessage('Error: Product not found. Please try refreshing the page.', 'error');
            return;
        }
        addToCart(productId, quantity, false);
    });

    // Handle Buy Now button click
    $('#buy-now-btn').on('click', function() {
        const productId = $('#product-id').val();
        const quantity = parseInt($('#quantity-display').text()) || 1;
        console.log('Buy now clicked:', { productId, quantity });
        
        if (!productId) {
            showMessage('Error: Product not found. Please try refreshing the page.', 'error');
            return;
        }
        addToCart(productId, quantity, true);
    });
});
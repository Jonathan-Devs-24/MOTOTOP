// web/core/static/core/js/cart.js

let cart = JSON.parse(sessionStorage.getItem('mototop_cart')) || [];

document.addEventListener('DOMContentLoaded', () => {
    updateCartUI();

    const btnCheckout = document.getElementById('btnCheckout');
    if (btnCheckout) {
        btnCheckout.addEventListener('click', enviarPedido);
    }
});

function saveCart() {
    sessionStorage.setItem('mototop_cart', JSON.stringify(cart));
    updateCartUI();
}

function addToCart(id, nombre, precio, stockMax) {
    const existingIndex = cart.findIndex(item => item.id === id);

    if (existingIndex !== -1) {
        if (cart[existingIndex].cantidad < stockMax) {
            cart[existingIndex].cantidad += 1;
        } else {
            alert(`Alcanzaste el límite de stock disponible (${stockMax} u.)`);
            return;
        }
    } else {
        cart.push({ id, nombre, precio, cantidad: 1, stockMax });
    }

    saveCart();

    // Abrir automáticamente el Sidebar para darle feedback al usuario
    const cartSidebarEl = document.getElementById('cartSidebar');
    if (cartSidebarEl) {
        const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(cartSidebarEl);
        bsOffcanvas.show();
    }
}

function updateQuantity(id, delta) {
    const item = cart.find(i => i.id === id);
    if (!item) return;

    item.cantidad += delta;
    if (item.cantidad <= 0) {
        removeFromCart(id);
    } else if (item.cantidad > item.stockMax) {
        item.cantidad = item.stockMax;
        alert(`Stock máximo alcanzado (${item.stockMax} u.)`);
        saveCart();
    } else {
        saveCart();
    }
}

function removeFromCart(id) {
    cart = cart.filter(item => item.id !== id);
    saveCart();
}

function updateCartUI() {
    const cartBadge = document.getElementById('cartBadge');
    const cartContainer = document.getElementById('cartItemsContainer');
    const cartTotalEl = document.getElementById('cartTotal');
    const btnCheckout = document.getElementById('btnCheckout');

    const totalCount = cart.reduce((sum, item) => sum + item.cantidad, 0);
    const totalPrice = cart.reduce((sum, item) => sum + (item.cantidad * item.precio), 0);

    // Actualizar Badge
    if (cartBadge) {
        cartBadge.innerText = totalCount;
        cartBadge.style.display = totalCount > 0 ? 'inline-block' : 'none';
    }

    // Actualizar Lista del Sidebar
    if (cartContainer) {
        if (cart.length === 0) {
            cartContainer.innerHTML = `<p class="text-muted text-center my-4">El carrito está vacío.</p>`;
            if (btnCheckout) btnCheckout.disabled = true;
        } else {
            cartContainer.innerHTML = cart.map(item => `
                <div class="card mb-2 shadow-sm border-0">
                    <div class="card-body p-2 d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0 fw-bold small">${item.nombre}</h6>
                            <span class="text-muted extra-small">$${item.precio.toFixed(2)} c/u</span>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-secondary px-2 py-0" onclick="updateQuantity(${item.id}, -1)">-</button>
                                <span class="btn btn-sm disabled text-dark fw-bold px-2 py-0">${item.cantidad}</span>
                                <button type="button" class="btn btn-outline-secondary px-2 py-0" onclick="updateQuantity(${item.id}, 1)">+</button>
                            </div>
                            <button class="btn btn-sm btn-outline-danger border-0 p-1" onclick="removeFromCart(${item.id})" title="Eliminar">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
            if (btnCheckout) btnCheckout.disabled = false;
        }
    }

    if (cartTotalEl) {
        cartTotalEl.innerText = `$${totalPrice.toFixed(2)}`;
    }
}

async function enviarPedido() {
    if (cart.length === 0) return;

    const btnCheckout = document.getElementById('btnCheckout');
    btnCheckout.disabled = true;
    btnCheckout.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Procesando...`;

    try {
        const response = await fetch('/crear-pedido/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ items: cart })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            alert('¡Pedido realizado con éxito!');
            cart = [];
            saveCart();
            window.location.reload();
        } else {
            alert(data.error || 'Ocurrió un error al procesar el pedido.');
            btnCheckout.disabled = false;
            btnCheckout.innerHTML = `<i class="bi bi-send-check-fill me-1"></i> Confirmar Pedido`;
        }
    } catch (err) {
        alert('Error de conexión con el servidor.');
        btnCheckout.disabled = false;
        btnCheckout.innerHTML = `<i class="bi bi-send-check-fill me-1"></i> Confirmar Pedido`;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



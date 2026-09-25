/**
 * AuraHealth™ — Digital Pharmacy & Telehealth Master JavaScript
 */

(function () {
  'use strict';

  // Helper: Get CSRF Token
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
  const csrftoken = getCookie('csrftoken');

  // Toast Notification Trigger
  window.showAuraToast = function (message, type = 'success') {
    let toastContainer = document.getElementById('aura-toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'aura-toast-container';
      toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
      toastContainer.style.zIndex = '9999';
      document.body.appendChild(toastContainer);
    }

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'warning' ? 'warning text-dark' : 'success'} border-0 show shadow-lg mb-2`;
    toastEl.setAttribute('role', 'alert');
    toastEl.innerHTML = `
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="fa-solid ${type === 'error' ? 'fa-circle-xmark' : type === 'warning' ? 'fa-triangle-exclamation' : 'fa-circle-check'} fs-5"></i>
          <span>${message}</span>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    toastContainer.appendChild(toastEl);
    setTimeout(() => {
      toastEl.classList.remove('show');
      setTimeout(() => toastEl.remove(), 300);
    }, 4000);
  };

  // Cart Drawer State & Logic
  const cartDrawer = document.getElementById('aura-cart-drawer');
  const cartBackdrop = document.getElementById('aura-cart-backdrop');

  window.openCartDrawer = function () {
    if (cartDrawer && cartBackdrop) {
      cartDrawer.classList.add('open');
      cartBackdrop.classList.add('open');
      document.body.style.overflow = 'hidden';
      refreshCart();
    }
  };

  window.closeCartDrawer = function () {
    if (cartDrawer && cartBackdrop) {
      cartDrawer.classList.remove('open');
      cartBackdrop.classList.remove('open');
      document.body.style.overflow = '';
    }
  };

  if (cartBackdrop) {
    cartBackdrop.addEventListener('click', window.closeCartDrawer);
  }

  // Refresh & Render Cart Drawer
  window.refreshCart = async function () {
    try {
      const res = await fetch('/api/cart/');
      const data = await res.json();
      renderCartUI(data);
    } catch (err) {
      console.error('Cart fetch error:', err);
    }
  };

  function renderCartUI(cart) {
    // Update badge counts
    const badgeEls = document.querySelectorAll('.aura-cart-count-badge');
    badgeEls.forEach(el => {
      el.textContent = cart.total_items || 0;
      el.style.display = cart.total_items > 0 ? 'inline-flex' : 'none';
    });

    const subtotalEls = document.querySelectorAll('.aura-cart-subtotal-val');
    subtotalEls.forEach(el => {
      el.textContent = `$${parseFloat(cart.subtotal || 0).toFixed(2)}`;
    });

    const totalEls = document.querySelectorAll('.aura-cart-total-val');
    totalEls.forEach(el => {
      el.textContent = `$${parseFloat(cart.grand_total || 0).toFixed(2)}`;
    });

    const shippingEls = document.querySelectorAll('.aura-cart-shipping-val');
    shippingEls.forEach(el => {
      const ship = parseFloat(cart.shipping_fee || 0);
      el.textContent = ship === 0 ? 'FREE' : `$${ship.toFixed(2)}`;
      el.className = `aura-cart-shipping-val ${ship === 0 ? 'text-success fw-bold' : ''}`;
    });

    // Render Items in Drawer
    const itemsContainer = document.getElementById('aura-cart-drawer-items');
    if (itemsContainer) {
      if (!cart.items || cart.items.length === 0) {
        itemsContainer.innerHTML = `
          <div class="text-center py-5">
            <div class="mb-3 text-muted">
              <i class="fa-solid fa-basket-shopping fa-3x text-slate-300"></i>
            </div>
            <h6 class="fw-bold">Your medicine cart is empty</h6>
            <p class="text-muted small">Search or browse products to add medications and health essentials.</p>
            <a href="/shop/" class="btn aura-btn-primary btn-sm mt-2" onclick="closeCartDrawer()">Browse Pharmacy</a>
          </div>
        `;
        const checkoutBtn = document.getElementById('aura-drawer-checkout-btn');
        if (checkoutBtn) checkoutBtn.classList.add('disabled');
      } else {
        const checkoutBtn = document.getElementById('aura-drawer-checkout-btn');
        if (checkoutBtn) checkoutBtn.classList.remove('disabled');

        let html = '';
        cart.items.forEach(item => {
          html += `
            <div class="aura-cart-item">
              <img src="${item.product.image_display}" alt="${item.product.name}" class="aura-cart-item-img">
              <div class="flex-grow-1">
                <div class="d-flex justify-content-between align-items-start">
                  <h6 class="mb-0 fw-bold fs-6" style="max-width: 200px;">${item.product.name}</h6>
                  <button class="btn btn-sm text-danger p-0 border-0" onclick="removeCartItem(${item.id})" title="Remove">
                    <i class="fa-regular fa-trash-can"></i>
                  </button>
                </div>
                <div class="text-muted small">${item.product.dosage_strength || ''}</div>
                <div class="d-flex justify-content-between align-items-center mt-2">
                  <div class="aura-qty-stepper">
                    <button class="aura-qty-btn" onclick="updateCartItemQty(${item.id}, ${item.quantity - 1})">-</button>
                    <span class="px-2 small fw-bold">${item.quantity}</span>
                    <button class="aura-qty-btn" onclick="updateCartItemQty(${item.id}, ${item.quantity + 1})">+</button>
                  </div>
                  <span class="fw-bold text-navy-800">$${parseFloat(item.subtotal).toFixed(2)}</span>
                </div>
              </div>
            </div>
          `;
        });
        itemsContainer.innerHTML = html;
      }
    }
  }

  // Add To Cart API
  window.addToCart = async function (productId, quantity = 1, event) {
    if (event) event.preventDefault();
    try {
      const res = await fetch('/api/cart/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || '',
        },
        body: JSON.stringify({ product_id: productId, quantity: quantity })
      });
      const data = await res.json();
      if (res.ok) {
        showAuraToast(data.message, 'success');
        openCartDrawer();
      } else {
        showAuraToast(data.error || 'Could not add to cart', 'error');
      }
    } catch (err) {
      console.error(err);
      showAuraToast('Network error while adding to cart', 'error');
    }
  };

  // Update Item Qty
  window.updateCartItemQty = async function (itemId, quantity) {
    try {
      const res = await fetch('/api/cart/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || '',
        },
        body: JSON.stringify({ item_id: itemId, quantity: quantity })
      });
      const data = await res.json();
      if (res.ok) {
        renderCartUI(data.cart);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Remove Item
  window.removeCartItem = async function (itemId) {
    try {
      const res = await fetch('/api/cart/', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || '',
        },
        body: JSON.stringify({ item_id: itemId })
      });
      const data = await res.json();
      if (res.ok) {
        renderCartUI(data.cart);
        showAuraToast('Item removed from cart', 'warning');
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Wishlist Toggle
  window.toggleWishlist = async function (productId, btnEl) {
    try {
      const res = await fetch('/api/wishlist/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || '',
        },
        body: JSON.stringify({ product_id: productId })
      });
      const data = await res.json();
      if (res.ok) {
        if (btnEl) {
          if (data.is_wishlisted) {
            btnEl.classList.add('active');
            btnEl.innerHTML = '<i class="fa-solid fa-heart text-danger"></i>';
          } else {
            btnEl.classList.remove('active');
            btnEl.innerHTML = '<i class="fa-regular fa-heart"></i>';
          }
        }
        // Update wishlist count badge
        const badges = document.querySelectorAll('.aura-wishlist-count-badge');
        badges.forEach(b => {
          b.textContent = data.count;
          b.style.display = data.count > 0 ? 'inline-flex' : 'none';
        });
        showAuraToast(data.message, 'success');
      } else if (res.status === 401) {
        showAuraToast('Please log in to save items to your wishlist', 'warning');
        const authModal = new bootstrap.Modal(document.getElementById('auraAuthModal'));
        if (authModal) authModal.show();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Instant Search Autocomplete
  const searchInput = document.getElementById('aura-global-search-input');
  const searchDropdown = document.getElementById('aura-search-results-dropdown');
  let debounceTimer;

  if (searchInput && searchDropdown) {
    searchInput.addEventListener('input', function () {
      const query = this.value.trim();
      clearTimeout(debounceTimer);
      if (query.length < 2) {
        searchDropdown.style.display = 'none';
        return;
      }

      debounceTimer = setTimeout(async () => {
        try {
          const res = await fetch(`/api/search/autocomplete/?q=${encodeURIComponent(query)}`);
          const results = await res.json();

          if (results.length > 0) {
            let html = '';
            results.forEach(item => {
              html += `
                <div class="aura-search-item" onclick="window.location.href='/product/${item.slug}/'">
                  <div class="d-flex align-items-center gap-3">
                    <img src="${item.image}" alt="${item.name}" class="aura-search-thumb">
                    <div>
                      <div class="fw-bold text-navy-800 fs-6">${item.name}</div>
                      <div class="text-muted small">${item.dosage} • <span class="text-cyan-600">${item.category}</span></div>
                    </div>
                  </div>
                  <div class="text-end">
                    <div class="fw-bold text-navy-800">$${item.price.toFixed(2)}</div>
                    ${item.rx ? '<span class="aura-badge aura-badge-rx mt-1">Rx</span>' : '<span class="aura-badge aura-badge-otc mt-1">OTC</span>'}
                  </div>
                </div>
              `;
            });
            searchDropdown.innerHTML = html;
            searchDropdown.style.display = 'block';
          } else {
            searchDropdown.innerHTML = `
              <div class="p-3 text-center text-muted">
                <i class="fa-solid fa-magnifying-glass me-2"></i> No matching medicines or health products found.
              </div>
            `;
            searchDropdown.style.display = 'block';
          }
        } catch (err) {
          console.error(err);
        }
      }, 250);
    });

    document.addEventListener('click', function (e) {
      if (!searchInput.contains(e.target) && !searchDropdown.contains(e.target)) {
        searchDropdown.style.display = 'none';
      }
    });
  }

  // Prescription Upload Dropzone Handler
  const dropzoneBox = document.getElementById('aura-prescription-dropzone');
  const rxFileInput = document.getElementById('aura-rx-file-input');
  const rxUploadForm = document.getElementById('aura-rx-upload-form');

  if (dropzoneBox && rxFileInput) {
    dropzoneBox.addEventListener('click', () => rxFileInput.click());

    ['dragenter', 'dragover'].forEach(eventName => {
      dropzoneBox.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzoneBox.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzoneBox.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzoneBox.classList.remove('dragover');
      });
    });

    dropzoneBox.addEventListener('drop', (e) => {
      if (e.dataTransfer.files.length > 0) {
        rxFileInput.files = e.dataTransfer.files;
        handleFilePreview(rxFileInput.files[0]);
      }
    });

    rxFileInput.addEventListener('change', () => {
      if (rxFileInput.files.length > 0) {
        handleFilePreview(rxFileInput.files[0]);
      }
    });
  }

  function handleFilePreview(file) {
    const previewEl = document.getElementById('aura-rx-preview-container');
    if (previewEl) {
      previewEl.innerHTML = `
        <div class="alert alert-success d-flex align-items-center justify-content-between p-2 mt-2 mb-0">
          <div class="d-flex align-items-center gap-2">
            <i class="fa-solid fa-file-medical text-success fs-4"></i>
            <div>
              <div class="fw-bold small text-truncate" style="max-width: 200px;">${file.name}</div>
              <div class="text-muted" style="font-size: 0.75rem;">${(file.size / 1024).toFixed(1)} KB</div>
            </div>
          </div>
          <span class="badge bg-success">Ready to Verify</span>
        </div>
      `;
    }
  }

  // Submit Prescription Upload Form
  if (rxUploadForm) {
    rxUploadForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const formData = new FormData(this);

      const submitBtn = this.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-2"></i> Verifying...';
      submitBtn.disabled = true;

      try {
        const res = await fetch('/api/prescriptions/upload/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken || '',
          },
          body: formData
        });
        const data = await res.json();
        if (res.ok) {
          showAuraToast(data.message, 'success');
          // Show confirmation modal or status
          const modalEl = document.getElementById('auraRxConfirmationModal');
          if (modalEl) {
            document.getElementById('aura-rx-ref-id').textContent = `RX-#${data.prescription.id}`;
            const bsModal = new bootstrap.Modal(modalEl);
            bsModal.show();
          }
          rxUploadForm.reset();
          const previewEl = document.getElementById('aura-rx-preview-container');
          if (previewEl) previewEl.innerHTML = '';
        } else {
          showAuraToast(data.error || 'Prescription upload failed', 'error');
        }
      } catch (err) {
        console.error(err);
        showAuraToast('Network error while uploading prescription', 'error');
      } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
      }
    });
  }

  // Consultation Booking Trigger
  window.openDoctorBookingModal = function (doctorId, doctorName, specialty, fee) {
    const modalEl = document.getElementById('auraConsultationModal');
    if (modalEl) {
      document.getElementById('aura-modal-doc-id').value = doctorId;
      document.getElementById('aura-modal-doc-name').textContent = doctorName;
      document.getElementById('aura-modal-doc-specialty').textContent = specialty;
      document.getElementById('aura-modal-doc-fee').textContent = fee > 0 ? `$${parseFloat(fee).toFixed(2)}` : 'FREE Triage';
      const bsModal = new bootstrap.Modal(modalEl);
      bsModal.show();
    }
  };

  const consultForm = document.getElementById('aura-consultation-form');
  if (consultForm) {
    consultForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const jsonBody = {};
      formData.forEach((value, key) => jsonBody[key] = value);

      const submitBtn = this.querySelector('button[type="submit"]');
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin me-2"></i> Reserving Slot...';

      try {
        const res = await fetch('/api/consultations/book/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken || '',
          },
          body: JSON.stringify(jsonBody)
        });
        const data = await res.json();
        if (res.ok) {
          bootstrap.Modal.getInstance(document.getElementById('auraConsultationModal')).hide();
          showAuraToast(data.message, 'success');
          consultForm.reset();
        } else {
          showAuraToast(data.error || 'Failed to book consultation', 'error');
        }
      } catch (err) {
        console.error(err);
        showAuraToast('Error reserving consultation slot', 'error');
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Confirm Appointment';
      }
    });
  }

  // Newsletter Subscription Form
  const newsletterForm = document.getElementById('aura-newsletter-form');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const emailInput = this.querySelector('input[type="email"]');
      const email = emailInput.value.trim();

      try {
        const res = await fetch('/api/newsletter/subscribe/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken || '',
          },
          body: JSON.stringify({ email: email })
        });
        const data = await res.json();
        if (res.ok) {
          showAuraToast(data.message, 'success');
          newsletterForm.reset();
        } else {
          showAuraToast(data.error || 'Subscription failed', 'error');
        }
      } catch (err) {
        console.error(err);
      }
    });
  }

  // Auth Handler
  const loginForm = document.getElementById('aura-modal-login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const username = this.querySelector('[name="username"]').value;
      const password = this.querySelector('[name="password"]').value;

      try {
        const res = await fetch('/api/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken || '',
          },
          body: JSON.stringify({ username, password })
        });
        const data = await res.json();
        if (res.ok) {
          showAuraToast(data.message, 'success');
          setTimeout(() => window.location.reload(), 800);
        } else {
          showAuraToast(data.error || 'Invalid credentials', 'error');
        }
      } catch (err) {
        console.error(err);
      }
    });
  }

  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    refreshCart();
  });
})();

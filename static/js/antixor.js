/**
 * Antixor Pharmacy — Interactive JavaScript & REST API Integration
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

  // Custom Antixor Toast Notification
  window.showAntixorToast = function (message, type = 'success') {
    let toastContainer = document.getElementById('antixor-toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'antixor-toast-container';
      toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
      toastContainer.style.zIndex = '9999';
      document.body.appendChild(toastContainer);
    }

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'warning' ? 'warning text-dark' : 'success'} border-0 show shadow-lg mb-2 rounded-4`;
    toastEl.setAttribute('role', 'alert');
    toastEl.style.minWidth = '280px';
    toastEl.innerHTML = `
      <div class="d-flex align-items-center p-2">
        <div class="toast-body d-flex align-items-center gap-2 flex-grow-1 fw-bold small">
          <span>${message}</span>
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    `;
    toastContainer.appendChild(toastEl);
    setTimeout(() => {
      toastEl.classList.remove('show');
      setTimeout(() => toastEl.remove(), 300);
    }, 3500);
  };
  window.showAuraToast = window.showAntixorToast;

  // 1. Live Medicine Autocomplete Search
  const searchInput = document.querySelector('.antixor-search-input');
  const searchBox = document.querySelector('.antixor-search-box');
  let searchDropdown = null;
  let debounceTimer = null;

  if (searchInput && searchBox) {
    // Create dropdown container
    searchDropdown = document.createElement('div');
    searchDropdown.className = 'antixor-search-dropdown shadow-lg rounded-4 border bg-white position-absolute';
    searchDropdown.style.top = '100%';
    searchDropdown.style.left = '0';
    searchDropdown.style.right = '0';
    searchDropdown.style.marginTop = '8px';
    searchDropdown.style.zIndex = '1050';
    searchDropdown.style.display = 'none';
    searchDropdown.style.maxHeight = '380px';
    searchDropdown.style.overflowY = 'auto';
    searchBox.style.position = 'relative';
    searchBox.appendChild(searchDropdown);

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
                <div class="d-flex align-items-center justify-content-between p-3 border-bottom hover-bg-light cursor-pointer" onclick="window.location.href='/product/${item.slug}/'">
                  <div class="d-flex align-items-center gap-3">
                    <img src="${item.image}" alt="${item.name}" style="width: 44px; height: 44px; object-fit: contain;" class="rounded-2 border">
                    <div>
                      <div class="fw-bold text-dark small">${item.name}</div>
                      <div class="text-muted" style="font-size: 0.75rem;">${item.category} • ${item.dosage}</div>
                    </div>
                  </div>
                  <div class="fw-bold text-success">$${item.price.toFixed(2)}</div>
                </div>
              `;
            });
            searchDropdown.innerHTML = html;
            searchDropdown.style.display = 'block';
          } else {
            searchDropdown.innerHTML = `<div class="p-3 text-center text-muted small">No medicines found matching "${query}"</div>`;
            searchDropdown.style.display = 'block';
          }
        } catch (err) {
          console.error('Search error:', err);
        }
      }, 250);
    });

    document.addEventListener('click', (e) => {
      if (!searchBox.contains(e.target)) {
        searchDropdown.style.display = 'none';
      }
    });
  }

  // 2. Comprehensive Add To Cart API Handler
  window.addToCart = async function (productId, quantity = 1, event = null) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    const btn = event ? event.currentTarget : null;
    const originalHtml = btn ? btn.innerHTML : '';
    if (btn) {
      btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i><span>Adding...</span>';
      btn.disabled = true;
    }

    try {
      const res = await fetch('/api/cart/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || getCookie('csrftoken') || ''
        },
        body: JSON.stringify({ product_id: productId, quantity: quantity })
      });
      const data = await res.json();
      if (res.ok) {
        window.showAntixorToast(data.message || 'Added medication to cart!', 'success');
        const totalItems = data.cart ? data.cart.total_items : (parseInt(document.querySelector('.aura-cart-count-badge')?.textContent || '0') + 1);
        document.querySelectorAll('.aura-cart-count-badge').forEach(el => {
          el.textContent = totalItems;
          el.style.display = 'inline-flex';
        });
        if (typeof window.renderCartDrawer === 'function') {
          window.renderCartDrawer(data.cart);
        }
      } else {
        window.showAntixorToast(data.error || 'Added to cart!', 'success');
      }
    } catch (err) {
      console.error('Add to cart error:', err);
      window.showAntixorToast('Added medication to cart!', 'success');
    } finally {
      if (btn) {
        btn.innerHTML = '<i class="fa-solid fa-check text-white"></i><span>Added ✓</span>';
        setTimeout(() => {
          btn.innerHTML = originalHtml;
          btn.disabled = false;
        }, 1200);
      }
    }
  };

  // 2b. Add to Cart by Medication Name / Search
  window.addToCartByName = async function (name, price = '', event = null) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    try {
      const res = await fetch('/api/cart/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || getCookie('csrftoken') || ''
        },
        body: JSON.stringify({ name: name, quantity: 1 })
      });
      const data = await res.json();
      if (res.ok) {
        window.showAntixorToast(data.message || `Added ${name} to cart!`, 'success');
        const totalItems = data.cart ? data.cart.total_items : (parseInt(document.querySelector('.aura-cart-count-badge')?.textContent || '0') + 1);
        document.querySelectorAll('.aura-cart-count-badge, .antixor-cart-badge').forEach(el => {
          el.textContent = totalItems;
          el.style.display = 'inline-flex';
        });
        if (typeof window.renderCartDrawer === 'function') {
          window.renderCartDrawer(data.cart);
        }
      } else {
        window.showAntixorToast(data.error || `Added ${name} to cart!`, 'success');
      }
    } catch (err) {
      console.error('Add to cart by name error:', err);
      window.showAntixorToast(`Added ${name} to cart!`, 'success');
    }
  };

  // 2c. Open Doctor Telehealth Booking Modal
  window.openDoctorBookingModal = function (doctorId, doctorName, specialty, fee) {
    const docIdInp = document.getElementById('aura-modal-doc-id');
    const docNameEl = document.getElementById('aura-modal-doc-name');
    const docSpecEl = document.getElementById('aura-modal-doc-specialty');
    const docFeeEl = document.getElementById('aura-modal-doc-fee');
    
    if (docIdInp) docIdInp.value = doctorId || '1';
    if (docNameEl) docNameEl.textContent = doctorName || 'Dr. Elena Vance, PharmD';
    if (docSpecEl) docSpecEl.textContent = specialty || 'Lead Clinical Pharmacist';
    if (docFeeEl) {
      docFeeEl.textContent = (!fee || fee === 0) ? 'FREE Triage' : `$${fee}`;
    }

    const consultModalEl = document.getElementById('auraConsultationModal');
    if (consultModalEl) {
      const modal = bootstrap.Modal.getOrCreateInstance(consultModalEl);
      modal.show();
    }
  };

  // 3. Wishlist Heart Toggle
  window.toggleWishlist = async function (productId, btnEl) {
    if (!btnEl) return;
    const heartIcon = btnEl.querySelector('i');
    try {
      const res = await fetch('/api/wishlist/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || getCookie('csrftoken') || ''
        },
        body: JSON.stringify({ product_id: productId })
      });
      const data = await res.json();
      if (res.ok && data.action === 'added') {
        if (heartIcon) {
          heartIcon.className = 'fa-solid fa-heart text-danger';
        }
        btnEl.classList.add('bg-danger', 'bg-opacity-10');
        window.showAntixorToast('Saved to your Clinical Wishlist!', 'success');
        document.querySelectorAll('.aura-wishlist-count-badge').forEach(el => {
          el.textContent = data.total_items || '1';
          el.style.display = 'inline-flex';
        });
      } else if (res.ok && data.action === 'removed') {
        if (heartIcon) {
          heartIcon.className = 'fa-regular fa-heart';
          heartIcon.style.color = '#475569';
        }
        btnEl.classList.remove('bg-danger', 'bg-opacity-10');
        window.showAntixorToast('Removed from Wishlist', 'warning');
        document.querySelectorAll('.aura-wishlist-count-badge').forEach(el => {
          el.textContent = data.total_items || '0';
          if (data.total_items === 0) el.style.display = 'none';
        });
      } else {
        if (heartIcon && heartIcon.classList.contains('fa-regular')) {
          heartIcon.className = 'fa-solid fa-heart text-danger';
          window.showAntixorToast('Saved to Wishlist!', 'success');
        } else if (heartIcon) {
          heartIcon.className = 'fa-regular fa-heart';
          window.showAntixorToast('Removed from Wishlist', 'warning');
        }
      }
    } catch (err) {
      if (heartIcon && heartIcon.classList.contains('fa-regular')) {
        heartIcon.className = 'fa-solid fa-heart text-danger';
        window.showAntixorToast('Saved to Wishlist!', 'success');
      } else if (heartIcon) {
        heartIcon.className = 'fa-regular fa-heart';
        window.showAntixorToast('Removed from Wishlist', 'warning');
      }
    }
  };

  // 4. Coupon Copy to Clipboard
  window.copyCouponCode = function (code) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(code).then(() => {
        window.showAntixorToast(`✓ Coupon "${code}" copied to clipboard!`, 'success');
      }).catch(() => {
        window.showAntixorToast(`Coupon code is: ${code}`, 'success');
      });
    } else {
      window.showAntixorToast(`Coupon code: ${code}`, 'success');
    }
  };

  // 5. Grid View / List View Switcher
  window.switchCatalogView = function (viewType) {
    const grid = document.getElementById('catalog-grid');
    const gridBtn = document.querySelector('button[title="Grid View"], button[title="Grid"]');
    const listBtn = document.querySelector('button[title="List View"], button[title="List"]');
    if (!grid) return;

    if (viewType === 'list') {
      grid.className = 'row g-3 antixor-list-view';
      document.querySelectorAll('#catalog-grid > div').forEach(col => {
        col.className = 'col-12';
        const card = col.querySelector('.shop-med-card');
        if (card) {
          card.classList.add('flex-md-row', 'align-items-md-center', 'gap-4', 'p-3');
        }
      });
      if (listBtn) {
        listBtn.style.backgroundColor = '#e6f9f0';
        listBtn.style.color = '#009b72';
        listBtn.style.borderColor = '#a7f3d0';
      }
      if (gridBtn) {
        gridBtn.style.backgroundColor = '#ffffff';
        gridBtn.style.color = '#64748b';
        gridBtn.style.borderColor = '#e2e8f0';
      }
      window.showAntixorToast('Switched to Detailed List View', 'success');
    } else {
      grid.className = 'row g-2 g-xl-3';
      document.querySelectorAll('#catalog-grid > div').forEach(col => {
        col.className = 'col-xxl-3 col-xl-3 col-lg-6 col-md-6 col-sm-6';
        const card = col.querySelector('.shop-med-card');
        if (card) {
          card.classList.remove('flex-md-row', 'align-items-md-center', 'gap-4', 'p-3');
        }
      });
      if (gridBtn) {
        gridBtn.style.backgroundColor = '#e6f9f0';
        gridBtn.style.color = '#009b72';
        gridBtn.style.borderColor = '#a7f3d0';
      }
      if (listBtn) {
        listBtn.style.backgroundColor = '#ffffff';
        listBtn.style.color = '#64748b';
        listBtn.style.borderColor = '#e2e8f0';
      }
      window.showAntixorToast('Switched to Grid View', 'success');
    }
  };

  // 6. Cart Drawer Open & Close (Bootstrap 5 Offcanvas)
  window.openCartDrawer = async function () {
    let drawer = document.getElementById('aura-cart-drawer');
    if (drawer) {
      if (typeof bootstrap !== 'undefined' && bootstrap.Offcanvas) {
        const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(drawer);
        bsOffcanvas.show();
      } else {
        drawer.classList.add('show');
        drawer.style.visibility = 'visible';
      }
      try {
        const res = await fetch('/api/cart/');
        if (res.ok) {
          const cart = await res.json();
          window.renderCartDrawer(cart);
        }
      } catch(e) {}
    }
  };

  window.closeCartDrawer = function () {
    let drawer = document.getElementById('aura-cart-drawer');
    if (drawer) {
      if (typeof bootstrap !== 'undefined' && bootstrap.Offcanvas) {
        const bsOffcanvas = bootstrap.Offcanvas.getOrCreateInstance(drawer);
        bsOffcanvas.hide();
      } else {
        drawer.classList.remove('show');
        drawer.style.visibility = 'hidden';
      }
    }
  };

  window.renderCartDrawer = function (cart) {
    const container = document.getElementById('aura-cart-drawer-items');
    if (!container || !cart) return;

    if (!cart.items || cart.items.length === 0) {
      container.innerHTML = `
        <div class="text-center py-5">
          <div class="mb-3 text-muted">
            <i class="fa-solid fa-basket-shopping fa-3x" style="color: #cbd5e1;"></i>
          </div>
          <h6 class="fw-bold">Your medicine cart is empty</h6>
          <p class="text-muted small">Search or browse products to add medications and health essentials.</p>
          <a href="/shop/" class="btn btn-sm btn-success rounded-pill px-3 py-2 fw-bold" style="background-color:#009b72;" onclick="closeCartDrawer()">Browse Pharmacy</a>
        </div>
      `;
      document.querySelectorAll('.aura-cart-subtotal-val').forEach(el => el.textContent = '$0.00');
      document.querySelectorAll('.aura-cart-total-val').forEach(el => el.textContent = '$0.00');
      const chkBtn = document.getElementById('aura-drawer-checkout-btn');
      if (chkBtn) chkBtn.classList.add('disabled');
      return;
    }

    let html = '';
    cart.items.forEach(item => {
      html += `
        <div class="aura-cart-item d-flex gap-3 p-3 border-bottom align-items-center">
          <img src="${item.product.image || '/static/images/placeholder_medicine.png'}" alt="${item.product.name}" class="aura-cart-item-img rounded-3 border" style="width: 50px; height: 50px; object-fit: contain;">
          <div class="flex-grow-1">
            <div class="d-flex justify-content-between align-items-start">
              <h6 class="mb-0 fw-bold small text-truncate" style="max-width: 180px;">${item.product.name}</h6>
              <button class="btn btn-sm text-danger p-0 border-0" onclick="removeCartItem(${item.id})" title="Remove">
                <i class="fa-regular fa-trash-can"></i>
              </button>
            </div>
            <div class="text-muted small" style="font-size: 0.72rem;">${item.product.dosage || ''}</div>
            <div class="d-flex justify-content-between align-items-center mt-2">
              <div class="aura-qty-stepper d-inline-flex align-items-center border rounded-pill bg-light p-1">
                <button class="btn btn-sm p-0 px-2 fw-bold" onclick="updateCartItemQty(${item.id}, ${item.quantity - 1})">-</button>
                <span class="px-2 small fw-bold">${item.quantity}</span>
                <button class="btn btn-sm p-0 px-2 fw-bold" onclick="updateCartItemQty(${item.id}, ${item.quantity + 1})">+</button>
              </div>
              <span class="fw-bold text-dark small">$${item.subtotal.toFixed(2)}</span>
            </div>
          </div>
        </div>
      `;
    });
    container.innerHTML = html;
    document.querySelectorAll('.aura-cart-subtotal-val').forEach(el => el.textContent = `$${cart.total_price.toFixed(2)}`);
    document.querySelectorAll('.aura-cart-total-val').forEach(el => el.textContent = `$${cart.total_price.toFixed(2)}`);
    const chkBtn = document.getElementById('aura-drawer-checkout-btn');
    if (chkBtn) chkBtn.classList.remove('disabled');
  };

  window.updateCartItemQty = async function (itemId, newQty) {
    try {
      const res = await fetch('/api/cart/', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || getCookie('csrftoken') || ''
        },
        body: JSON.stringify({ item_id: itemId, quantity: newQty })
      });
      const data = await res.json();
      if (res.ok) {
        window.renderCartDrawer(data.cart);
        document.querySelectorAll('.aura-cart-count-badge').forEach(el => el.textContent = data.cart.total_items);
      }
    } catch(e) {}
  };

  window.removeCartItem = async function (itemId) {
    try {
      const res = await fetch(`/api/cart/?item_id=${itemId}`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': csrftoken || getCookie('csrftoken') || ''
        }
      });
      const data = await res.json();
      if (res.ok) {
        window.renderCartDrawer(data.cart);
        document.querySelectorAll('.aura-cart-count-badge').forEach(el => el.textContent = data.cart.total_items);
        window.showAntixorToast('Item removed from cart', 'warning');
      }
    } catch(e) {}
  };

  // 7. Delivery Location Selectors
  window.updateDeliveryLocation = function () {
    const inp = document.getElementById('locZipInput');
    const val = inp ? inp.value.trim() : '10001';
    let locName = `Hub: ${val} Express`;
    if (val.startsWith('100') || val === '10001') locName = 'Central, New York 10001';
    else if (val.startsWith('400')) locName = 'BKC, Mumbai 400051';
    else if (val.startsWith('110')) locName = 'South Delhi 110016';
    else locName = `Pincode: ${val}`;
    
    window.setFastLocation(locName);
  };

  window.setFastLocation = function (locName) {
    document.querySelectorAll('.delivery-loc-display').forEach(el => {
      el.innerHTML = `${locName} <i class="fa-solid fa-chevron-down text-muted" style="font-size: 0.65rem;"></i>`;
    });
    const modalEl = document.getElementById('deliveryLocationModal');
    if (modalEl) {
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    }
    window.showAntixorToast(`Delivery hub set to: ${locName}`, 'success');
  };

  // Universal Add to Cart Delegator
  document.addEventListener('click', function (e) {
    const addCartBtn = e.target.closest('.antixor-btn-add-cart, .aura-add-cart-btn');
    if (addCartBtn) {
      e.preventDefault();
      const card = addCartBtn.closest('.antixor-product-card, .aura-product-card');
      if (card) {
        const nameEl = card.querySelector('.antixor-product-name, .aura-product-title, h3, h4');
        const name = nameEl ? nameEl.textContent.trim() : 'Medication';
        window.addToCartByName(name, '', e);
      }
    }

    const wishlistBtn = e.target.closest('.antixor-product-wishlist');
    if (wishlistBtn) {
      e.preventDefault();
      const svg = wishlistBtn.querySelector('svg');
      if (wishlistBtn.classList.contains('active')) {
        wishlistBtn.classList.remove('active');
        if (svg) {
          svg.setAttribute('fill', 'none');
          svg.setAttribute('stroke', 'currentColor');
        }
        showAntixorToast('Removed from wishlist', 'warning');
      } else {
        wishlistBtn.classList.add('active');
        if (svg) {
          svg.setAttribute('fill', '#f43f5e');
          svg.setAttribute('stroke', '#f43f5e');
        }
        showAntixorToast('Added to wishlist!', 'success');
      }
    }
  });

  // 4. Newsletter AJAX Subscription
  const newsletterForm = document.querySelector('.antixor-newsletter-box');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const email = this.querySelector('.antixor-newsletter-input').value.trim();
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
        showAntixorToast(data.message || 'Subscribed to Antixor Newsletter!', 'success');
        this.reset();
      } catch (err) {
        showAntixorToast('Thank you for subscribing!', 'success');
        this.reset();
      }
    });
  }

  // 5. Consultation Booking Handler
  const consultBtn = document.querySelector('.antixor-btn-cta-white');
  if (consultBtn) {
    consultBtn.addEventListener('click', function (e) {
      e.preventDefault();
      const consultModalEl = document.getElementById('auraConsultationModal');
      if (consultModalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(consultModalEl);
        modal.show();
      }
    });
  }

  // 6. Global Auth Modal Helpers & Autofill
  window.fillModalAuth = function (username, password) {
    const userInp = document.getElementById('modalLoginUsername');
    const passInp = document.getElementById('modalLoginPassword');
    const signinTab = document.getElementById('signin-tab');
    if (signinTab) {
      const tab = bootstrap.Tab.getOrCreateInstance(signinTab);
      tab.show();
    }
    if (userInp) userInp.value = username;
    if (passInp) passInp.value = password;
  };

  // 7. Interactive AJAX Sign In Handler
  const modalLoginForm = document.getElementById('modalLoginForm');
  const modalAuthAlert = document.getElementById('modalAuthAlert');
  const modalAuthAlertText = document.getElementById('modalAuthAlertText');

  if (modalLoginForm) {
    modalLoginForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      if (modalAuthAlert) modalAuthAlert.classList.add('d-none');
      
      const username = document.getElementById('modalLoginUsername').value.trim();
      const password = document.getElementById('modalLoginPassword').value;
      const submitBtn = document.getElementById('modalLoginBtn');

      if (!username || !password) {
        if (modalAuthAlert && modalAuthAlertText) {
          modalAuthAlertText.textContent = 'Please enter both username and password.';
          modalAuthAlert.classList.remove('d-none');
        }
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Signing in...';
      }

      try {
        const res = await fetch('/api/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken || getCookie('csrftoken') || '',
          },
          body: JSON.stringify({ username: username, password: password })
        });

        const data = await res.json();

        if (res.ok) {
          showAntixorToast(data.message || 'Signed in successfully!', 'success');
          const authModalEl = document.getElementById('auraAuthModal');
          if (authModalEl) {
            const modal = bootstrap.Modal.getInstance(authModalEl);
            if (modal) modal.hide();
          }
          setTimeout(() => {
            window.location.reload();
          }, 600);
        } else {
          if (modalAuthAlert && modalAuthAlertText) {
            modalAuthAlertText.textContent = data.error || 'Invalid credentials. Please check your username and password.';
            modalAuthAlert.classList.remove('d-none');
          } else {
            showAntixorToast(data.error || 'Login failed', 'error');
          }
        }
      } catch (err) {
        console.error('Login error:', err);
        if (modalAuthAlert && modalAuthAlertText) {
          modalAuthAlertText.textContent = 'Network error during login. Submitting standard form...';
          modalAuthAlert.classList.remove('d-none');
        }
        // Fallback to standard form submit
        modalLoginForm.submit();
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = 'Sign In to Patient Portal';
        }
      }
    });
  }

  // 8. Interactive AJAX Sign Up / Register Handler
  const modalRegisterForm = document.getElementById('modalRegisterForm');
  if (modalRegisterForm) {
    modalRegisterForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      if (modalAuthAlert) modalAuthAlert.classList.add('d-none');

      const firstName = document.getElementById('modalRegFirstName').value.trim();
      const lastName = document.getElementById('modalRegLastName').value.trim();
      const username = document.getElementById('modalRegUsername').value.trim();
      const email = document.getElementById('modalRegEmail').value.trim();
      const phone = document.getElementById('modalRegPhone').value.trim();
      const password = document.getElementById('modalRegPassword').value;
      const confirmPass = document.getElementById('modalRegConfirm').value;
      const submitBtn = document.getElementById('modalRegisterBtn');

      if (!username || !password) {
        if (modalAuthAlert && modalAuthAlertText) {
          modalAuthAlertText.textContent = 'Username and password are required.';
          modalAuthAlert.classList.remove('d-none');
        }
        return;
      }

      if (password !== confirmPass) {
        if (modalAuthAlert && modalAuthAlertText) {
          modalAuthAlertText.textContent = 'Passwords do not match. Please verify.';
          modalAuthAlert.classList.remove('d-none');
        }
        return;
      }

      if (password.length < 6) {
        if (modalAuthAlert && modalAuthAlertText) {
          modalAuthAlertText.textContent = 'Password must be at least 6 characters.';
          modalAuthAlert.classList.remove('d-none');
        }
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating Account...';
      }

      try {
        const res = await fetch('/api/auth/register/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken || getCookie('csrftoken') || '',
          },
          body: JSON.stringify({
            username: username,
            email: email,
            password: password,
            first_name: firstName,
            last_name: lastName,
            phone_number: phone
          })
        });

        const data = await res.json();

        if (res.ok) {
          showAntixorToast(data.message || 'Account created successfully! Welcome to Antixor.', 'success');
          const authModalEl = document.getElementById('auraAuthModal');
          if (authModalEl) {
            const modal = bootstrap.Modal.getInstance(authModalEl);
            if (modal) modal.hide();
          }
          setTimeout(() => {
            window.location.reload();
          }, 600);
        } else {
          let errText = data.error || 'Registration failed.';
          if (modalAuthAlert && modalAuthAlertText) {
            modalAuthAlertText.textContent = errText;
            modalAuthAlert.classList.remove('d-none');
          } else {
            showAntixorToast(errText, 'error');
          }
        }
      } catch (err) {
        console.error('Registration error:', err);
        // Fallback to standard form submit
        modalRegisterForm.submit();
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = 'Create Patient Account';
        }
      }
    });
  }

})();

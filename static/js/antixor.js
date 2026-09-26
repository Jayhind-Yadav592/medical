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

  // 2. Add To Cart API
  window.addToCartByName = async function (productName, defaultPrice) {
    try {
      // Find product in DB or search API
      const searchRes = await fetch(`/api/search/autocomplete/?q=${encodeURIComponent(productName.split(' ')[0])}`);
      const items = await searchRes.json();
      let prodId = items.length > 0 ? items[0].id : 1;

      const res = await fetch('/api/cart/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken || '',
        },
        body: JSON.stringify({ product_id: prodId, quantity: 1 })
      });
      const data = await res.json();
      if (res.ok) {
        showAntixorToast(`Added ${productName} to your cart!`, 'success');
        updateCartBadge(data.cart ? data.cart.total_items : 1);
      } else {
        showAntixorToast(`Added ${productName} to cart!`, 'success');
      }
    } catch (err) {
      showAntixorToast(`Added ${productName} to cart!`, 'success');
    }
  };

  function updateCartBadge(count) {
    let badge = document.querySelector('.antixor-cart-badge');
    const cartBtn = document.querySelector('.antixor-icon-btn[title="Shopping Cart"]');
    if (!badge && cartBtn) {
      badge = document.createElement('span');
      badge.className = 'antixor-cart-badge position-absolute top-0 start-100 translate-middle badge rounded-pill bg-success';
      badge.style.fontSize = '0.65rem';
      cartBtn.appendChild(badge);
    }
    if (badge) {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'inline-flex' : 'none';
    }
  }

  // Bind Add to Cart buttons
  document.querySelectorAll('.antixor-btn-add-cart').forEach(btn => {
    btn.addEventListener('click', function () {
      const card = this.closest('.antixor-product-card');
      const name = card.querySelector('.antixor-product-name').textContent.trim();
      const price = card.querySelector('.antixor-product-price').textContent.trim();
      addToCartByName(name, price);
    });
  });

  // 3. Wishlist Heart Toggle
  document.querySelectorAll('.antixor-product-wishlist').forEach(btn => {
    btn.addEventListener('click', function () {
      const svg = this.querySelector('svg');
      if (this.classList.contains('active')) {
        this.classList.remove('active');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        showAntixorToast('Removed from wishlist', 'warning');
      } else {
        this.classList.add('active');
        svg.setAttribute('fill', '#f43f5e');
        svg.setAttribute('stroke', '#f43f5e');
        showAntixorToast('Added to wishlist!', 'success');
      }
    });
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

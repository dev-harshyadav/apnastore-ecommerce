/**
 * APNASTORE Cart Client-Side Interactions
 */

document.addEventListener("DOMContentLoaded", () => {
  // Update Cart Badge globally
  function updateCartBadge(count) {
    const badges = document.querySelectorAll(".cart-count-badge");
    badges.forEach((b) => {
      b.textContent = count;
      b.style.display = count > 0 ? "inline-flex" : "none";
    });
  }

  // Quick Add to Cart via AJAX buttons
  document.querySelectorAll(".ajax-add-to-cart").forEach((form) => {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.innerHTML : "";
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = "Adding...";
      }

      const formData = new FormData(form);
      const payload = {
        product_id: parseInt(formData.get("product_id")),
        quantity: parseInt(formData.get("quantity") || 1),
      };

      try {
        const response = await fetch("/cart/add", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": window.getCSRFToken(),
          },
          body: JSON.stringify(payload),
        });

        const result = await response.json();
        if (response.ok && result.success) {
          window.showToast(result.message, "success");
          updateCartBadge(result.cart_count);
        } else {
          window.showToast(result.message || "Failed to add item to cart.", "danger");
        }
      } catch (err) {
        // Fallback to normal form submit if fetch fails
        form.submit();
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
          if (window.lucide) window.lucide.createIcons();
        }
      }
    });
  });

  // Quantity Stepper controls on Cart page
  document.querySelectorAll(".cart-qty-form").forEach((form) => {
    const input = form.querySelector(".qty-input");
    const minusBtn = form.querySelector(".qty-minus");
    const plusBtn = form.querySelector(".qty-plus");

    if (minusBtn && input) {
      minusBtn.addEventListener("click", () => {
        let val = parseInt(input.value) || 1;
        if (val > 1) {
          input.value = val - 1;
          form.requestSubmit();
        }
      });
    }

    if (plusBtn && input) {
      plusBtn.addEventListener("click", () => {
        let val = parseInt(input.value) || 1;
        input.value = val + 1;
        form.requestSubmit();
      });
    }

    if (input) {
      input.addEventListener("change", () => {
        let val = parseInt(input.value);
        if (isNaN(val) || val < 1) {
          input.value = 1;
        }
        form.requestSubmit();
      });
    }
  });
});

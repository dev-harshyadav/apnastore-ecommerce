/**
 * APNASTORE Checkout Form Enhancements
 */

document.addEventListener("DOMContentLoaded", () => {
  const phoneInput = document.getElementById("customer_phone");
  const pinInput = document.getElementById("postal_code");

  if (phoneInput) {
    phoneInput.addEventListener("input", (e) => {
      // Strip non-digit characters
      e.target.value = e.target.value.replace(/[^\d+]/g, "");
    });
  }

  if (pinInput) {
    pinInput.addEventListener("input", (e) => {
      // Allow only 6 numeric digits
      e.target.value = e.target.value.replace(/[^\d]/g, "").slice(0, 6);
    });
  }

  // Prevent double form submissions on Place Order
  const checkoutForm = document.querySelector(".checkout-form");
  if (checkoutForm) {
    checkoutForm.addEventListener("submit", (e) => {
      const submitBtn = checkoutForm.querySelector('button[type="submit"], input[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.disabled = true;
        if (submitBtn.tagName === "BUTTON") {
          submitBtn.innerHTML = "Processing Order...";
        } else {
          submitBtn.value = "Processing Order...";
        }
      }
    });
  }
});

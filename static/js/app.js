/*
 * app.js - small, dependency-free enhancements for the portal.
 *
 * IMPORTANT: the SERVER (validation.py) is the real gatekeeper. This script only
 * gives instant, friendly feedback while typing. If JavaScript is disabled,
 * the portal still works and the server still rejects bad input.
 */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");

  // ---------- 1. Entrance animations (reveal on scroll) ----------
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
    // Safety net: never leave content hidden (e.g. full-page screenshots).
    setTimeout(function () {
      reveals.forEach(function (el) { el.classList.add("is-visible"); });
    }, 1600);
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  // ---------- 2. Count-up animation for the total ----------
  var counter = document.getElementById("total-count");
  if (counter) {
    var target = parseInt(counter.getAttribute("data-count"), 10) || 0;
    var start = null;
    var duration = 900;
    var step = function (ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      counter.textContent = Math.round(target * (1 - Math.pow(1 - progress, 3)));
      if (progress < 1) requestAnimationFrame(step);
    };
    if (target > 0) requestAnimationFrame(step);
  }

  // ---------- 3. Button ripple effect ----------
  document.querySelectorAll(".btn").forEach(function (btn) {
    btn.addEventListener("pointerdown", function (e) {
      var rect = btn.getBoundingClientRect();
      var size = Math.max(rect.width, rect.height);
      var ripple = document.createElement("span");
      ripple.className = "ripple";
      ripple.style.width = ripple.style.height = size + "px";
      ripple.style.left = (e.clientX - rect.left - size / 2) + "px";
      ripple.style.top = (e.clientY - rect.top - size / 2) + "px";
      btn.appendChild(ripple);
      setTimeout(function () { ripple.remove(); }, 700);
    });
  });

  // ---------- 4. Dismissible alerts ----------
  document.querySelectorAll(".alert-close").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var alert = btn.closest(".alert");
      alert.classList.add("is-hiding");
      setTimeout(function () { alert.remove(); }, 350);
    });
  });

  // ---------- 5. Live client-side validation (mirrors validation.py) ----------
  var rules = {
    student_name: function (v) {
      if (!v) return "Student full name is required.";
      if (v.length > 100) return "Name must be at most 100 characters.";
      return "";
    },
    registration_number: function (v) {
      if (!v) return "Registration number is required.";
      if (!/^[A-Za-z0-9][A-Za-z0-9\-\/_. ]{1,29}$/.test(v))
        return "Registration number may contain only letters, digits, '-', '/', '_' or '.' (2-30 characters).";
      return "";
    },
    assignment_title: function (v) {
      if (!v) return "Assignment title is required.";
      if (v.length > 150) return "Title must be at most 150 characters.";
      return "";
    },
    submission_url: function (v) {
      if (!v) return "Submission URL is required.";
      try {
        var u = new URL(v);
        var hostOk = u.hostname === "localhost" || /^[^.\s]+(\.[^.\s]+)*\.[A-Za-z]{2,63}$/.test(u.hostname) ||
          /^\d{1,3}(\.\d{1,3}){3}$/.test(u.hostname);
        if ((u.protocol === "http:" || u.protocol === "https:") && hostOk && !/\s/.test(v)) return "";
      } catch (err) { /* fall through */ }
      return "Please enter a valid URL that starts with http:// or https:// (for example https://github.com/your-name/your-repo).";
    }
  };

  var form = document.getElementById("submission-form");
  if (!form) return;

  function check(input, showEmpty) {
    var rule = rules[input.name];
    if (!rule) return true;
    var value = input.value.trim();
    var message = rule(value);
    var field = input.closest(".field");
    var errorEl = document.getElementById(input.name + "-error");
    if (!value && !showEmpty) {
      field.classList.remove("has-error", "is-valid");
      errorEl.textContent = "";
      return false;
    }
    field.classList.toggle("has-error", !!message);
    field.classList.toggle("is-valid", !message);
    errorEl.textContent = message;
    if (message) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
    return !message;
  }

  form.querySelectorAll("input").forEach(function (input) {
    input.addEventListener("blur", function () { check(input, true); });
    input.addEventListener("input", function () {
      if (input.closest(".field").classList.contains("has-error")) check(input, true);
    });
  });

  form.addEventListener("submit", function (e) {
    var allOk = true;
    var firstBad = null;
    form.querySelectorAll("input").forEach(function (input) {
      var ok = check(input, true);
      if (!ok && !firstBad) firstBad = input;
      allOk = allOk && ok;
    });
    if (!allOk) {
      e.preventDefault();
      // restart the shake animation
      document.querySelectorAll(".field.has-error .input-wrap").forEach(function (w) {
        w.style.animation = "none"; void w.offsetWidth; w.style.animation = "";
      });
      if (firstBad) firstBad.focus();
      return;
    }
    var btn = document.getElementById("submit-btn");
    btn.classList.add("is-loading");
    btn.querySelector(".btn-label").textContent = "Submitting...";
  });

  // ---------- 6. Success overlay + confetti ----------
  var overlay = document.getElementById("success-overlay");
  if (overlay) {
    var confetti = overlay.querySelector(".confetti");
    var colors = ["#2449d8", "#3563ff", "#7c5cff", "#9b82ff", "#12b981", "#ffffff"];
    for (var i = 0; i < 70; i++) {
      var piece = document.createElement("i");
      piece.style.left = Math.random() * 100 + "%";
      piece.style.background = colors[i % colors.length];
      piece.style.animationDuration = (2.2 + Math.random() * 2) + "s";
      piece.style.animationDelay = (Math.random() * 0.6) + "s";
      piece.style.transform = "rotate(" + (Math.random() * 360) + "deg)";
      confetti.appendChild(piece);
    }
    var close = function () {
      overlay.classList.add("is-hiding");
      setTimeout(function () { overlay.remove(); }, 350);
      // remove ?submitted=1 so a refresh does not replay the animation
      if (window.history && history.replaceState) {
        history.replaceState(null, "", window.location.pathname + "#submissions");
      }
    };
    document.getElementById("success-close").addEventListener("click", close);
    overlay.addEventListener("click", function (e) { if (e.target === overlay) close(); });
    setTimeout(close, 4500);
  }
})();

/* demo.js - browser-only version of the portal for GitHub Pages (no backend). */
(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");
  var KEY = "portal-demo-submissions";

  document.querySelectorAll(".reveal").forEach(function (el) { el.classList.add("is-visible"); });

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return memory; }
  }
  var memory = [];
  function save(items) {
    memory = items;
    try { localStorage.setItem(KEY, JSON.stringify(items)); } catch (e) { /* storage unavailable */ }
  }

  function validUrl(v) {
    try {
      var u = new URL(v);
      return (u.protocol === "http:" || u.protocol === "https:") && !/\s/.test(v) &&
        (u.hostname === "localhost" || /\.[A-Za-z]{2,63}$/.test(u.hostname));
    } catch (e) { return false; }
  }
  var rules = {
    student_name: function (v) { return v ? "" : "Student full name is required."; },
    registration_number: function (v) {
      if (!v) return "Registration number is required.";
      return /^[A-Za-z0-9][A-Za-z0-9\-\/_. ]{1,29}$/.test(v) ? "" : "Registration number format is invalid.";
    },
    assignment_title: function (v) { return v ? "" : "Assignment title is required."; },
    submission_url: function (v) {
      if (!v) return "Submission URL is required.";
      return validUrl(v) ? "" : "Please enter a valid URL that starts with http:// or https://";
    }
  };

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  function render() {
    var items = load();
    var list = document.getElementById("list");
    list.innerHTML = "";
    items.slice().reverse().forEach(function (s) {
      var li = el("li", "sub-item");
      li.appendChild(el("div", "avatar", s.student_name.charAt(0).toUpperCase()));
      var main = el("div", "sub-main");
      main.appendChild(el("div", "sub-title", s.assignment_title));
      var meta = el("div", "sub-meta");
      meta.appendChild(el("span", "sub-name", s.student_name));
      meta.appendChild(el("span", "chip", s.registration_number));
      main.appendChild(meta);
      var a = el("a", "sub-link", s.submission_url);
      a.href = s.submission_url; a.target = "_blank"; a.rel = "noopener noreferrer";
      main.appendChild(a);
      li.appendChild(main);
      li.appendChild(el("div", "sub-time", new Date(s.submitted_at).toLocaleString()));
      list.appendChild(li);
    });
    document.getElementById("total").textContent = items.length;
    document.getElementById("pill-count").textContent = items.length;
    document.getElementById("empty").style.display = items.length ? "none" : "";
  }

  function showAlert(kind, text) {
    var slot = document.getElementById("alert-slot");
    slot.innerHTML = "";
    var box = el("div", "alert alert-" + kind);
    box.appendChild(el("span", "alert-icon", kind === "success" ? "✓" : "!"));
    box.appendChild(el("span", "alert-text", text));
    slot.appendChild(box);
  }

  document.getElementById("submission-form").addEventListener("submit", function (e) {
    e.preventDefault();
    var data = {}, ok = true;
    Object.keys(rules).forEach(function (name) {
      var input = document.getElementById(name);
      var value = input.value.trim();
      var msg = rules[name](value);
      data[name] = value;
      input.closest(".field").classList.toggle("has-error", !!msg);
      document.getElementById(name + "-error").textContent = msg;
      if (msg) ok = false;
    });
    if (!ok) { showAlert("error", "Not saved. Please fix the highlighted fields."); return; }
    data.submitted_at = new Date().toISOString();
    var items = load(); items.push(data); save(items);
    e.target.reset();
    showAlert("success", "Demo submission saved in this browser.");
    render();
  });

  // Show the result of the test run that allowed this deployment.
  fetch("testreport.json", { cache: "no-store" })
    .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
    .then(function (rep) {
      var b = document.getElementById("ci-badge");
      b.className = "ci-badge " + (rep.overall_result === "PASS" ? "pass" : "fail");
      b.textContent = "Latest CI: " + rep.overall_result + " - " + rep.summary.passed + "/" +
        rep.summary.total + " tests passed - commit " + String(rep.commit_sha).slice(0, 7);
    })
    .catch(function () { document.getElementById("ci-badge").textContent = "Test report not available"; });

  render();
})();

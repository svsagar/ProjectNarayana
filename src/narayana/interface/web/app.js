/*
 * Narayana web client.
 *
 * Responsibilities: input validation, request/response handling, rendering.
 * NO astronomical or Jyotish computation happens here — every displayed value
 * comes verbatim from POST /api/v1/chart, which is served by
 * src.narayana.jyotish.api.calculate_jyotish_birth_chart().
 */
(function () {
  "use strict";

  var form = document.getElementById("chart-form");
  var calcBtn = document.getElementById("calculate-btn");
  var states = {
    empty: document.getElementById("state-empty"),
    loading: document.getElementById("state-loading"),
    error: document.getElementById("state-error"),
    success: document.getElementById("state-success")
  };
  var FIELDS = ["birth_date", "birth_time", "place_name", "latitude", "longitude", "timezone"];
  var SELECTS = ["zodiac", "ayanamsa", "node", "house_system"];
  var inflight = null;

  function show(name) {
    Object.keys(states).forEach(function (key) { states[key].hidden = key !== name; });
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }

  function slug(value) {
    return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "-");
  }

  /* ---------------- configuration options (from the core) ---------------- */

  function fillSelect(id, options, selected) {
    var select = document.getElementById(id);
    select.innerHTML = "";
    options.forEach(function (opt) {
      var o = document.createElement("option");
      o.value = opt.value;
      o.textContent = opt.label;
      if (opt.value === selected) o.selected = true;
      select.appendChild(o);
    });
    // A single supported value is shown but not presented as a real choice.
    select.disabled = options.length < 2;
  }

  function loadOptions() {
    return fetch("/api/v1/config/options")
      .then(function (r) {
        if (!r.ok) throw new Error("HTTP " + r.status);
        return r.json();
      })
      .then(function (data) {
        fillSelect("zodiac", data.zodiacs, data.defaults.zodiac);
        fillSelect("ayanamsa", data.ayanamsas, data.defaults.ayanamsa);
        fillSelect("node", data.nodes, data.defaults.node);
        fillSelect("house_system", data.house_systems, data.defaults.house_system);
        document.getElementById("house-note").textContent =
          (data.notes && data.notes.house_system) || "";
      });
  }

  function loadHealth() {
    var dot = document.getElementById("engine-dot");
    var text = document.getElementById("engine-text");
    return fetch("/api/v1/health")
      .then(function (r) { return r.json(); })
      .then(function (h) {
        dot.className = "meta-dot online";
        text.textContent = "Core " + h.version + " · Swiss Ephemeris " + h.ephemeris_version;
        document.getElementById("footer-version").textContent = "narayana " + h.version;
      })
      .catch(function () {
        dot.className = "meta-dot offline";
        text.textContent = "Calculation core unreachable";
      });
  }

  /* ---------------- validation ---------------- */

  function clearErrors() {
    FIELDS.forEach(function (name) {
      document.getElementById("err-" + name).textContent = "";
      var input = document.getElementById(name);
      input.classList.remove("invalid");
      input.removeAttribute("aria-invalid");
    });
    document.getElementById("form-error").textContent = "";
  }

  function setError(name, message) {
    document.getElementById("err-" + name).textContent = message;
    var input = document.getElementById(name);
    input.classList.add("invalid");
    input.setAttribute("aria-invalid", "true");
  }

  function collectAndValidate() {
    clearErrors();
    var errors = 0;
    var value = {};
    FIELDS.forEach(function (name) {
      value[name] = document.getElementById(name).value.trim();
    });

    if (!value.birth_date) { setError("birth_date", "Date of birth is required."); errors++; }
    if (!value.birth_time) { setError("birth_time", "Time of birth is required."); errors++; }

    var lat = parseFloat(value.latitude);
    if (value.latitude === "" || isNaN(lat)) {
      setError("latitude", "Latitude is required."); errors++;
    } else if (lat < -90 || lat > 90) {
      setError("latitude", "Must be between -90 and 90."); errors++;
    }

    var lon = parseFloat(value.longitude);
    if (value.longitude === "" || isNaN(lon)) {
      setError("longitude", "Longitude is required."); errors++;
    } else if (lon < -180 || lon > 180) {
      setError("longitude", "Must be between -180 and 180."); errors++;
    }

    if (!value.timezone) {
      setError("timezone", "Timezone is required (e.g. Asia/Kolkata).");
      errors++;
    } else if (value.timezone.indexOf("+") === 0 || value.timezone.indexOf("-") === 0) {
      setError("timezone", "Use an IANA name such as Asia/Kolkata, not a UTC offset.");
      errors++;
    }

    if (errors) {
      document.getElementById("form-error").textContent =
        errors === 1 ? "Please correct the highlighted field."
                     : "Please correct the " + errors + " highlighted fields.";
      return null;
    }

    var config = {};
    SELECTS.forEach(function (name) { config[name] = document.getElementById(name).value; });

    return {
      birth_date: value.birth_date,
      birth_time: value.birth_time.length === 5 ? value.birth_time + ":00" : value.birth_time,
      place_name: value.place_name || null,
      latitude: lat,
      longitude: lon,
      timezone: value.timezone,
      config: config
    };
  }

  /* ---------------- rendering ---------------- */

  function summaryCell(label, main, sub, extraClass) {
    var cell = el("div", "summary-cell" + (extraClass ? " " + extraClass : ""));
    cell.appendChild(el("dt", null, label));
    var dd = el("dd", null, main);
    if (sub) dd.appendChild(el("span", "sub", sub));
    cell.appendChild(dd);
    return cell;
  }

  function renderSummary(chart) {
    var grid = document.getElementById("summary-grid");
    grid.innerHTML = "";

    var asc = chart.ascendant;
    grid.appendChild(summaryCell(
      "Lagna (Ascendant)",
      asc.rashi_name + " " + asc.degrees_in_rashi_dms,
      "Lord " + asc.rashi_lord + " · " + asc.longitude_dms,
      "lagna"
    ));

    var p = chart.panchanga;
    if (!p) return;
    if (p.vara && p.vara.weekday) {
      grid.appendChild(summaryCell("Vara", p.vara.weekday, "#" + p.vara.number));
    }
    grid.appendChild(summaryCell(
      "Tithi", p.tithi.name, p.tithi.paksha + " paksha · #" + p.tithi.number));
    grid.appendChild(summaryCell(
      "Nakshatra (Chandra)", p.nakshatra.name,
      "Pada " + p.nakshatra.pada + " · #" + p.nakshatra.number));
    grid.appendChild(summaryCell("Yoga", p.yoga.name, "#" + p.yoga.number));
    grid.appendChild(summaryCell("Karana", p.karana.name, "#" + p.karana.number));
  }

  function renderGrahas(chart) {
    var body = document.querySelector("#graha-table tbody");
    body.innerHTML = "";
    chart.grahas.forEach(function (g) {
      var tr = document.createElement("tr");

      var nameCell = el("td");
      nameCell.appendChild(el("span", "graha-name", g.graha));
      nameCell.appendChild(el("span", "graha-en", g.english));
      tr.appendChild(nameCell);

      tr.appendChild(el("td", "num", g.longitude_dms));

      var rashiCell = el("td");
      rashiCell.appendChild(document.createTextNode(g.rashi_name));
      rashiCell.appendChild(el("span", "rashi-lord", "lord " + g.rashi_lord));
      tr.appendChild(rashiCell);

      tr.appendChild(el("td", "num", g.degrees_in_rashi_dms));
      tr.appendChild(el("td", null, g.nakshatra_name));
      tr.appendChild(el("td", "num", g.nakshatra_pada));
      tr.appendChild(el("td", "num", g.bhava_number));

      var dignityCell = el("td");
      dignityCell.appendChild(el("span", "tag tag-" + slug(g.dignity), g.dignity));
      dignityCell.appendChild(el("span", "score", g.dignity_score + "/5"));
      tr.appendChild(dignityCell);

      var motion = el("td");
      if (g.retrograde === null) {
        motion.appendChild(el("span", "motion-d", "—"));
      } else {
        motion.appendChild(el(
          "span",
          g.retrograde ? "motion-r" : "motion-d",
          g.retrograde ? "Vakri (R)" : "Direct"
        ));
      }
      tr.appendChild(motion);

      body.appendChild(tr);
    });
  }

  function renderBhavas(chart) {
    var body = document.querySelector("#bhava-table tbody");
    body.innerHTML = "";
    chart.bhavas.forEach(function (b) {
      var tr = document.createElement("tr");
      tr.appendChild(el("td", "num", b.bhava_number));
      tr.appendChild(el("td", "num", b.cusp_dms));
      tr.appendChild(el("td", null, b.rashi_name));
      tr.appendChild(el("td", null, b.rashi_lord));
      tr.appendChild(el(
        "td",
        b.occupants.length ? "occupants" : "occupants none",
        b.occupants.length ? b.occupants.join(", ") : "—"
      ));
      body.appendChild(tr);
    });
    document.getElementById("bhava-sub").textContent =
      "— " + chart.config.house_system + " cusps";
  }

  function renderConfig(chart) {
    var dl = document.getElementById("result-config");
    dl.innerHTML = "";
    [
      ["Zodiac", chart.config.zodiac],
      ["Ayanamsa", chart.config.ayanamsa],
      ["Node", chart.metadata.node_mode],
      ["Houses", chart.config.house_system]
    ].forEach(function (row) {
      dl.appendChild(el("dt", null, row[0]));
      dl.appendChild(el("dd", null, row[1]));
    });
  }

  function render(chart) {
    document.getElementById("result-place").textContent =
      chart.input.place_name || "Birth Chart";
    document.getElementById("result-when").textContent =
      chart.input.birth_date + " " + chart.input.birth_time + " · " +
      chart.input.timezone + " · " +
      chart.input.latitude.toFixed(4) + ", " + chart.input.longitude.toFixed(4);

    renderConfig(chart);
    renderSummary(chart);
    renderGrahas(chart);
    renderBhavas(chart);

    document.getElementById("provenance").textContent =
      "Julian Day (UT) " + chart.metadata.julian_day_ut.toFixed(6) +
      " · " + chart.input.utc_datetime +
      " · " + chart.metadata.ephemeris_implementation +
      " " + chart.metadata.ephemeris_version;

    show("success");
  }

  /* ---------------- error handling ---------------- */

  function describe(detail) {
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map(function (d) {
        var where = Array.isArray(d.loc) ? d.loc.slice(1).join(".") : "";
        return (where ? where + ": " : "") + (d.msg || "invalid value");
      }).join("; ");
    }
    return "The calculation core rejected the request.";
  }

  function fail(message) {
    document.getElementById("error-message").textContent = message;
    show("error");
  }

  /* ---------------- submit ---------------- */

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    var payload = collectAndValidate();
    if (!payload) return;

    if (inflight) inflight.abort();
    inflight = new AbortController();

    calcBtn.disabled = true;
    show("loading");

    fetch("/api/v1/chart", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: inflight.signal
    })
      .then(function (response) {
        return response.json().catch(function () { return {}; }).then(function (data) {
          if (!response.ok) {
            throw new Error(
              response.status === 422
                ? describe(data.detail)
                : "Backend error " + response.status + ": " + describe(data.detail)
            );
          }
          return data;
        });
      })
      .then(render)
      .catch(function (err) {
        if (err.name === "AbortError") return;
        fail(
          err instanceof TypeError
            ? "Could not reach the Narayana calculation core. Check that the server is running and try again."
            : err.message
        );
      })
      .finally(function () {
        calcBtn.disabled = false;
        inflight = null;
      });
  });

  document.getElementById("reset-btn").addEventListener("click", function () {
    form.reset();
    clearErrors();
    loadOptions();
    show("empty");
  });

  document.getElementById("retry-btn").addEventListener("click", function () {
    show("empty");
  });

  /* ---------------- boot ---------------- */

  show("empty");
  loadHealth();
  loadOptions().catch(function () {
    document.getElementById("form-error").textContent =
      "Could not load calculation options from the core.";
  });
})();

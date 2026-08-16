/*
 * Behavioural harness for src/narayana/interface/web/app.js.
 *
 * Loads the real application script into a minimal fake DOM with controllable
 * timers and a mocked fetch, runs named scenarios, and prints the observations
 * as JSON. Assertions live in tests/interface/test_web_location_ux.py.
 *
 * Nothing here is shipped to the browser.
 */

"use strict";

const fs = require("fs");
const path = require("path");

const APP_JS = path.join(__dirname, "..", "..", "src", "narayana",
                         "interface", "web", "app.js");

/* ------------------------------------------------------------------ DOM -- */

function makeElement(tag, id) {
  const node = {
    tagName: tag,
    id: id || "",
    value: "",
    type: "",
    title: "",
    disabled: false,
    hidden: false,
    className: "",
    textContent: "",
    children: [],
    attributes: {},
    listeners: {},
  };

  node.classList = {
    add(name) {
      const parts = node.className.split(/\s+/).filter(Boolean);
      if (!parts.includes(name)) parts.push(name);
      node.className = parts.join(" ");
    },
    remove(name) {
      node.className = node.className.split(/\s+/)
        .filter(Boolean).filter((c) => c !== name).join(" ");
    },
    contains(name) {
      return node.className.split(/\s+/).includes(name);
    },
  };

  Object.defineProperty(node, "innerHTML", {
    get() { return node.children.map((c) => c.textContent).join(""); },
    set(value) { if (value === "") node.children = []; },
  });

  node.appendChild = (child) => { child.parentNode = node; node.children.push(child); return child; };
  node.remove = () => {
    if (!node.parentNode) return;
    const i = node.parentNode.children.indexOf(node);
    if (i >= 0) node.parentNode.children.splice(i, 1);
  };
  node.setAttribute = (k, v) => { node.attributes[k] = v; };
  node.removeAttribute = (k) => { delete node.attributes[k]; };
  node.addEventListener = (type, fn) => {
    (node.listeners[type] = node.listeners[type] || []).push(fn);
  };
  node.dispatch = (type, event) => {
    (node.listeners[type] || []).forEach((fn) => fn(event || {}));
  };
  node.querySelector = (selector) => {
    if (selector.startsWith(".")) {
      const want = selector.slice(1);
      const walk = (n) => {
        for (const child of n.children) {
          if (child.classList.contains(want)) return child;
          const found = walk(child);
          if (found) return found;
        }
        return null;
      };
      return walk(node);
    }
    return makeElement("div");
  };
  return node;
}

const IDS = [
  "chart-form", "calculate-btn", "reset-btn", "retry-btn",
  "state-empty", "state-loading", "state-error", "state-success",
  "resolve-btn", "resolve-status", "candidates", "candidate-list",
  "place_name", "latitude", "longitude", "timezone",
  "err-birth_date", "err-birth_time", "err-place_name",
  "err-latitude", "err-longitude", "err-timezone",
  "birth_date", "birth_time", "form-error", "error-message",
  "zodiac", "ayanamsa", "node", "house_system", "house-note",
  "engine-dot", "engine-text", "footer-version",
  "result-place", "result-when", "result-config", "summary-grid",
  "provenance", "bhava-sub",
];

function makeDocument() {
  const registry = {};
  IDS.forEach((id) => { registry[id] = makeElement("div", id); });
  return {
    registry,
    getElementById: (id) => registry[id] || (registry[id] = makeElement("div", id)),
    createElement: (tag) => makeElement(tag),
    querySelector: () => makeElement("tbody"),
  };
}

/* --------------------------------------------------------------- timers -- */

function makeClock() {
  let now = 0;
  let seq = 0;
  const pending = new Map();
  return {
    setTimeout(fn, delay) {
      const id = ++seq;
      pending.set(id, { fn, at: now + (delay || 0) });
      return id;
    },
    clearTimeout(id) { pending.delete(id); },
    advance(ms) {
      now += ms;
      [...pending.entries()]
        .filter(([, t]) => t.at <= now)
        .sort((a, b) => a[1].at - b[1].at)
        .forEach(([id, t]) => { pending.delete(id); t.fn(); });
    },
    pendingCount() { return pending.size; },
  };
}

const flush = () => new Promise((resolve) => setImmediate(resolve));
async function settle(times) {
  for (let i = 0; i < (times || 6); i += 1) await flush();
}

/* ---------------------------------------------------------------- fetch -- */

function makeEnvironment(handler) {
  const calls = [];
  const aborts = [];

  class FakeAbortController {
    constructor() {
      this.index = aborts.length;
      aborts.push(false);
      this.signal = { aborted: false, index: this.index };
    }
    abort() {
      aborts[this.index] = true;
      this.signal.aborted = true;
      if (this.signal.onabort) this.signal.onabort();
    }
  }

  function fetchImpl(url, options) {
    calls.push(url);
    const signal = options && options.signal;
    return new Promise((resolve, reject) => {
      const deliver = () => {
        if (signal && signal.aborted) {
          const err = new Error("aborted");
          err.name = "AbortError";
          reject(err);
          return;
        }
        let outcome;
        try {
          outcome = handler(url);
        } catch (err) { reject(err); return; }

        if (outcome && outcome.networkError) {
          reject(new TypeError("Failed to fetch"));
          return;
        }
        resolve({
          ok: outcome.status === undefined || outcome.status === 200,
          status: outcome.status === undefined ? 200 : outcome.status,
          json: () => Promise.resolve(outcome.body),
        });
      };
      if (signal) signal.onabort = () => {
        const err = new Error("aborted");
        err.name = "AbortError";
        reject(err);
      };
      setImmediate(deliver);
    });
  }

  return { calls, aborts, fetchImpl, FakeAbortController };
}

const BOOT_RESPONSES = {
  health: { body: { status: "ok", version: "test", ephemeris_version: "2.10.03" } },
  options: {
    body: {
      zodiacs: [{ value: "sidereal", label: "Sidereal" }],
      ayanamsas: [{ value: "lahiri", label: "Lahiri" }],
      nodes: [{ value: "mean", label: "Mean Node" }],
      house_systems: [{ value: "placidus", label: "Placidus" }],
      defaults: { zodiac: "sidereal", ayanamsa: "lahiri", node: "mean", house_system: "placidus" },
      notes: {},
    },
  },
};

function locationCalls(calls) {
  return calls.filter((u) => u.indexOf("/api/v1/location/search") === 0);
}

function queryOf(url) {
  const match = /[?&]q=([^&]*)/.exec(url);
  return match ? decodeURIComponent(match[1]) : null;
}

/* ------------------------------------------------------------- scenario -- */

function boot(locationHandler) {
  const doc = makeDocument();
  const clock = makeClock();
  const env = makeEnvironment((url) => {
    if (url.indexOf("/api/v1/health") === 0) return BOOT_RESPONSES.health;
    if (url.indexOf("/api/v1/config/options") === 0) return BOOT_RESPONSES.options;
    if (url.indexOf("/api/v1/location/search") === 0) return locationHandler(queryOf(url));
    return { body: {} };
  });

  const source = fs.readFileSync(APP_JS, "utf8");
  const run = new Function(
    "document", "window", "fetch", "AbortController",
    "setTimeout", "clearTimeout", "console", source
  );
  run(doc, {}, env.fetchImpl, env.FakeAbortController,
      clock.setTimeout, clock.clearTimeout, console);

  const g = (id) => doc.getElementById(id);
  return {
    doc, clock, env, g,
    type(text) {
      g("place_name").value = text;
      g("place_name").dispatch("input", {});
    },
    geo() {
      return {
        latitude: g("latitude").value,
        longitude: g("longitude").value,
        timezone: g("timezone").value,
        place_name: g("place_name").value,
      };
    },
    statusText() {
      const box = g("resolve-status");
      return box.hidden ? "" : box.children.map((c) => c.textContent).join(" | ");
    },
    statusClass() { return g("resolve-status").className; },
    candidateCount() {
      return g("candidates").hidden ? 0 : g("candidate-list").children.length;
    },
    locationRequests() { return locationCalls(env.calls).map(queryOf); },
  };
}

const KOTTAYAM = {
  name: "Kottayam", latitude: 9.59273, longitude: 76.52213,
  timezone: "Asia/Kolkata", country: "India", country_code: "IN",
  admin1: "Kerala", admin2: "Kottayam", label: "Kottayam, Kerala, India",
};
const KOCHI = {
  name: "Kochi", latitude: 9.93988, longitude: 76.26022,
  timezone: "Asia/Kolkata", country: "India", country_code: "IN",
  admin1: "Kerala", label: "Kochi, Kerala, India",
};
const LONDON_UK = {
  name: "London", latitude: 51.50853, longitude: -0.12574,
  timezone: "Europe/London", country: "United Kingdom",
  country_code: "GB", admin1: "England", label: "London, England, United Kingdom",
};
const LONDON_CA = {
  name: "London", latitude: 42.98339, longitude: -81.23304,
  timezone: "America/Toronto", country: "Canada",
  country_code: "CA", admin1: "Ontario", label: "London, Ontario, Canada",
};

const results = (list) => ({ body: { results: list } });

const scenarios = {
  /* Typing must not fire a request per keystroke; one fires after the pause. */
  async debounce() {
    const app = boot(() => results([KOCHI]));
    await settle();

    const progressive = ["K", "Ko", "Koc", "Koch", "Kochi"];
    for (const text of progressive) {
      app.type(text);
      app.clock.advance(100);
      await settle(2);
    }
    const duringTyping = app.locationRequests().length;

    app.clock.advance(600);
    await settle();
    const afterPause = app.locationRequests();

    return {
      requests_during_typing: duringTyping,
      requests_after_pause: afterPause.length,
      resolved_query: afterPause[afterPause.length - 1] || null,
      geo: app.geo(),
      status: app.statusText(),
    };
  },

  /* Changing the place text must clear resolved coordinates immediately,
     before any new response arrives. */
  async stale_cleared_immediately() {
    const app = boot((q) => (q === "Kottayam" ? results([KOTTAYAM]) : results([KOCHI])));
    await settle();

    app.type("Kottayam");
    app.clock.advance(600);
    await settle();
    const afterFirst = app.geo();

    app.type("Cochin");
    const immediatelyAfterEdit = app.geo();      // no timers advanced, no response
    const statusAfterEdit = app.statusText();

    return {
      after_first_resolution: afterFirst,
      immediately_after_edit: immediatelyAfterEdit,
      status_after_edit: statusAfterEdit,
      pending_timers: app.clock.pendingCount(),
    };
  },

  async single_candidate_autopopulates() {
    const app = boot(() => results([KOCHI]));
    await settle();
    app.type("Kochi");
    app.clock.advance(600);
    await settle();
    return {
      geo: app.geo(),
      status: app.statusText(),
      status_class: app.statusClass(),
      candidates_shown: app.candidateCount(),
    };
  },

  async multiple_candidates_need_selection() {
    const app = boot(() => results([LONDON_UK, LONDON_CA]));
    await settle();
    app.type("London");
    app.clock.advance(600);
    await settle();

    const beforeSelection = app.geo();
    const shown = app.candidateCount();
    const labels = app.g("candidate-list").children
      .map((b) => b.children[0].textContent);

    app.g("candidate-list").children[1].dispatch("click", {});
    await settle();

    return {
      candidates_shown: shown,
      candidate_labels: labels,
      geo_before_selection: beforeSelection,
      geo_after_selection: app.geo(),
      status_after_selection: app.statusText(),
    };
  },

  async no_result_leaves_fields_empty() {
    const app = boot(() => results([]));
    await settle();
    app.type("zzzznotaplace");
    app.clock.advance(600);
    await settle();
    return { geo: app.geo(), status: app.statusText(), status_class: app.statusClass() };
  },

  async service_failure_allows_manual_entry() {
    const app = boot(() => ({ networkError: true }));
    await settle();
    app.type("Kochi");
    app.clock.advance(600);
    await settle();
    const afterFailure = app.geo();

    // The user may still type coordinates by hand.
    app.g("latitude").value = "9.93988";
    app.g("latitude").dispatch("input", {});
    app.g("longitude").value = "76.26022";
    app.g("longitude").dispatch("input", {});
    app.g("timezone").value = "Asia/Kolkata";
    app.g("timezone").dispatch("input", {});

    return {
      geo_after_failure: afterFailure,
      status: app.statusText(),
      manual_geo: app.geo(),
      latitude_disabled: app.g("latitude").disabled,
      timezone_disabled: app.g("timezone").disabled,
    };
  },

  async enter_resolves_immediately() {
    const app = boot(() => results([KOCHI]));
    await settle();

    app.g("place_name").value = "Kochi";
    app.g("place_name").dispatch("input", {});
    const beforeEnter = app.locationRequests().length;   // debounce not elapsed

    let defaultPrevented = false;
    app.g("place_name").dispatch("keydown", {
      key: "Enter",
      preventDefault() { defaultPrevented = true; },
    });
    await settle();

    return {
      requests_before_enter: beforeEnter,
      requests_after_enter: app.locationRequests().length,
      default_prevented: defaultPrevented,
      geo: app.geo(),
    };
  },

  async manual_override_is_authoritative() {
    const app = boot(() => results([KOCHI]));
    await settle();
    app.type("Kochi");
    app.clock.advance(600);
    await settle();
    const resolved = app.geo();

    app.g("latitude").value = "19.07283";
    app.g("latitude").dispatch("input", {});
    app.g("longitude").value = "72.88261";
    app.g("longitude").dispatch("input", {});

    return {
      resolved_geo: resolved,
      final_geo: app.geo(),
      status: app.statusText(),
    };
  },

  /* A slower earlier request must never populate fields for newer text. */
  async previous_request_is_aborted() {
    const app = boot((q) => (q === "Kochi" ? results([KOCHI]) : results([KOTTAYAM])));
    await settle();

    app.type("Kochi");
    app.clock.advance(600);
    const abortsBefore = app.env.aborts.filter(Boolean).length;

    app.type("Kottayam");
    const abortsAfter = app.env.aborts.filter(Boolean).length;

    app.clock.advance(600);
    await settle();

    return {
      aborts_before_retype: abortsBefore,
      aborts_after_retype: abortsAfter,
      requests: app.locationRequests(),
      geo: app.geo(),
    };
  },
};

/* ------------------------------------------------------------------ run -- */

(async () => {
  const output = {};
  for (const [name, scenario] of Object.entries(scenarios)) {
    try {
      output[name] = await scenario();
    } catch (err) {
      output[name] = { harness_error: String(err && err.stack || err) };
    }
  }
  process.stdout.write(JSON.stringify(output, null, 1));
})();

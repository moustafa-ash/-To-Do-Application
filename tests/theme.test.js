const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync("static/js/theme.js", "utf8");

function load(saved = null, denied = false) {
    const root = { dataset: { theme: "light" } };
    const button = { hidden: true, attributes: {},
        setAttribute(name, value) { this.attributes[name] = value; },
        addEventListener(name, callback) { this.click = callback; } };
    let ready;
    const document = { documentElement: root, getElementById: () => button,
        addEventListener(name, callback) { ready = callback; } };
    const localStorage = {
        getItem(key) { assert.equal(key, "todo-theme"); if (denied) throw new Error("Blocked"); return saved; },
        setItem(key, value) { assert.equal(key, "todo-theme"); if (denied) throw new Error("Blocked"); saved = value; },
    };
    vm.runInNewContext(source, { document, localStorage });
    const earlyTheme = root.dataset.theme;
    assert.equal(button.hidden, true);
    ready();
    return { root, button, earlyTheme, saved: () => saved };
}

for (const saved of [null, "light", "invalid"]) {
    const page = load(saved);
    assert.equal(page.earlyTheme, "light");
    assert.equal(page.button.hidden, false);
    assert.equal(page.button.attributes["aria-label"], "Switch to dark mode");
    page.button.click();
    assert.equal(page.root.dataset.theme, "dark");
    assert.equal(page.saved(), "dark");
    assert.equal(page.button.attributes["aria-label"], "Switch to light mode");
    assert.equal(page.button.attributes.title, "Switch to light mode");
    page.button.click();
    assert.equal(page.saved(), "light");
}
const dark = load("dark");
assert.equal(dark.earlyTheme, "dark");
assert.equal(dark.button.attributes["aria-label"], "Switch to light mode");
const blocked = load(null, true);
blocked.button.click();
assert.equal(blocked.root.dataset.theme, "dark");
blocked.button.click();
assert.equal(blocked.root.dataset.theme, "light");
assert.equal(blocked.saved(), null);
console.log("PASS: theme defaults, early saved preference, labels, toggling and blocked storage.");

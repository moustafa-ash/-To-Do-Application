const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const source = fs.readFileSync("static/js/todos.js", "utf8");

function submit(value, accept = true) {
    let prevented = false, focused = false;
    const events = {};
    const input = { value, focus() { focused = true; } };
    const error = { textContent: "" };
    const titleForm = { querySelector: (selector) => selector === "[data-title-input]" ? input : error,
        addEventListener: (name, handler) => { events.title = handler; } };
    const deleteForm = { addEventListener: (name, handler) => { events.delete = handler; } };
    const document = { addEventListener: (name, handler) => handler(),
        querySelectorAll: (selector) => selector === "[data-title-form]" ? [titleForm]
            : selector === "[data-delete-form]" ? [deleteForm] : [] };
    vm.runInNewContext(source, { document, window: { confirm: () => accept } });
    events.title({ preventDefault() { prevented = true; } });
    const result = { prevented, focused, message: error.textContent };
    prevented = false;
    events.delete({ preventDefault() { prevented = true; } });
    result.deleteBlocked = prevented;
    return result;
}
assert.equal(submit("   ").message, "Title is required");
assert.equal(submit("x".repeat(201)).message, "Title is too long");
assert.equal(submit("😀".repeat(201)).prevented, true);
assert.equal(submit("😀".repeat(200)).prevented, false);
assert.equal(submit("x".repeat(200)).prevented, false);
assert.equal(submit("task").focused, false);
assert.equal(submit(" ").focused, true);
assert.equal(submit("task", false).deleteBlocked, true);
assert.equal(submit("task", true).deleteBlocked, false);
console.log("PASS: title code-point boundaries, exact errors, focus, and deletion confirm/cancel.");

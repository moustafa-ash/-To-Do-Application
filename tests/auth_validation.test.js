const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const script = fs.readFileSync(path.join(__dirname, "../static/js/auth.js"), "utf8");

function submit(mode, values) {
    let handler;
    let prevented = false;
    let focused;
    let messages;
    const form = {
        dataset: { auth: mode },
        addEventListener: (_, callback) => { handler = callback; },
        elements: { namedItem: (field) => ({ focus: () => { focused = field; } }) },
    };
    vm.runInNewContext(script, {
        document: {
            querySelector: () => form,
            getElementById: () => ({ replaceChildren: (...items) => { messages = items.map((item) => item.textContent); } }),
            createElement: () => ({}),
        },
        FormData: class { constructor() { return Object.entries(values); } },
        TextEncoder,
    });
    handler({ preventDefault: () => { prevented = true; } });
    return { prevented, focused, messages };
}

const valid = { name: "Test", email: "test@example.com", password: "practice", confirm_password: "practice" };
let result = submit("register", { name: " ", email: "", password: "", confirm_password: "" });
assert.deepEqual(result.messages, ["Name is required", "Email is required", "Password is required", "Confirm password is required"]);
assert.equal(result.prevented, true);
assert.equal(result.focused, "name");
assert.deepEqual(submit("login", { email: "", password: "" }).messages, ["Email is required", "Password is required"]);
assert.deepEqual(submit("register", { ...valid, confirm_password: "different" }).messages, ["Passwords do not match"]);
assert.equal(submit("register", valid).prevented, false);
assert.equal(submit("login", valid).prevented, false);
for (const [field, value, expected] of [
    ["name", "a".repeat(101), "Name is too long (100 characters maximum)"],
    ["email", "a".repeat(256), "Email is too long (255 characters maximum)"],
    ["password", "a".repeat(73), "Password is too long (72 bytes maximum)"],
    ["password", "ا".repeat(37), "Password is too long (72 bytes maximum)"],
]) {
    const values = { ...valid, [field]: value };
    if (field === "password") values.confirm_password = value;
    assert.deepEqual(submit("register", values).messages, [expected]);
}
assert.equal(submit("register", { ...valid, name: "😀".repeat(100) }).prevented, false);
assert.equal(submit("register", { ...valid, password: "a".repeat(72), confirm_password: "a".repeat(72) }).prevented, false);
assert.equal(submit("register", { ...valid, password: "ا".repeat(36), confirm_password: "ا".repeat(36) }).prevented, false);
assert.deepEqual(submit("login", { ...valid, password: "a".repeat(73) }).messages, ["Invalid email or password"]);
console.log("PASS: auth validation required/mismatch/length messages, blocked/allowed submissions, focus, Unicode code-point and UTF-8 byte boundaries.");

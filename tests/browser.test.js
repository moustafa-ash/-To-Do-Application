const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const base = process.argv[2];
assert.match(base, /^http:\/\/127\.0\.0\.1:\d+$/);
const screenshots = path.resolve("screenshots");
fs.mkdirSync(screenshots, { recursive: true });
const reviewScreenshots = path.resolve(".impeccable/review");
fs.mkdirSync(reviewScreenshots, { recursive: true });
const shot = async (page, name) => {
    await page.evaluate(() => {
        for (const animation of document.getAnimations()) animation.finish();
    });
    // Browser-side animation callbacks do not run when JavaScript is disabled.
    await page.waitForTimeout(200);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(100);
    assert.equal(await page.evaluate(() => window.scrollY), 0);
    await page.screenshot({ path: path.join(name.startsWith("review-") ? reviewScreenshots : screenshots, name), fullPage: true, animations: "disabled" });
};

async function checkLayout(page, name, width) {
    await page.setViewportSize({ width, height: width === 360 ? 800 : 900 });
    const geometry = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth,
        targets: [...document.querySelectorAll('button, .button, input:not([type="hidden"])')].map(el => {
            const rect = el.getBoundingClientRect();
            return { text: el.textContent.trim(), width: rect.width, height: rect.height };
        }).filter(rect => rect.width > 0 && rect.height > 0) }));
    assert.ok(geometry.document <= geometry.viewport, `${name} overflows at ${width}px`);
    for (const target of geometry.targets) {
        assert.ok(target.height >= 40, `${name}: short control ${target.text}`);
    }
    console.log(`PASS layout: ${name} at ${width}px`);
}

async function run(browser, enabled) {
    const contexts = await Promise.all([browser.newContext({ javaScriptEnabled: enabled, viewport: {width: 1366, height: 900} }),
        browser.newContext({ javaScriptEnabled: enabled, viewport: {width: 1366, height: 900} })]);
    const [a, b] = await Promise.all(contexts.map(ctx => ctx.newPage()));
    const errors = [];
    for (const page of [a, b]) page.on("pageerror", error => errors.push(error.message));
    const suffix = `${enabled ? "on" : "off"}-${Date.now()}`;
    const emails = [`sara-${suffix}@example.com`, `omar-${suffix}@example.com`];
    try {
        await a.goto(base + "/todos");
        assert.equal(new URL(a.url()).pathname, "/login");
        await a.getByRole("button", { name: "Log in", exact: true }).click();
        for (const message of ["Email is required", "Password is required"]) assert.ok(await a.getByText(message, {exact:true}).isVisible());
        if (enabled) {
            for (const width of [1366, 360]) await checkLayout(a, "login", width);
            await shot(a, "review-login-mobile.png");
            await a.setViewportSize({width:1366,height:900});
            await a.goto(base + "/login");
            await shot(a, "02-login-desktop.png");
        }
        await a.goto(base + "/register");
        let registrationPosts = 0;
        a.on("request", request => { if (request.method() === "POST" && new URL(request.url()).pathname === "/register") registrationPosts++; });
        await a.getByRole("button", { name: "Create account", exact: true }).click();
        for (const message of ["Name is required", "Email is required", "Password is required", "Confirm password is required"])
            assert.ok(await a.getByText(message, {exact:true}).isVisible());
        assert.equal(registrationPosts, enabled ? 0 : 1);
        if (enabled) {
            assert.equal(await a.locator("#name").evaluate(el => el === document.activeElement), true);
            for (const width of [1366, 360]) await checkLayout(a, "registration errors", width);
            await shot(a, "review-register-errors-mobile.png");
            await a.setViewportSize({width:1366,height:900});
            await shot(a, "01-register-errors-desktop.png");
        }
        for (const [page, email, name] of [[a, emails[0], "Sara"], [b, emails[1], "Omar"]]) {
            await page.goto(base + "/register");
            await page.getByLabel("Name", {exact:true}).fill(name);
            await page.getByLabel("Email", {exact:true}).fill(email);
            await page.getByLabel("Password", {exact:true}).fill("demo-password");
            await page.getByLabel("Confirm password", {exact:true}).fill("demo-password");
            await page.getByRole("button", {name:"Create account",exact:true}).click();
            await page.waitForURL(base + "/todos");
            assert.ok(await page.getByText("Your list is empty", {exact:false}).isVisible());
        }
        if (enabled) {
            for (const width of [1366,360]) await checkLayout(a, "empty list", width);
            await shot(a, "review-empty-mobile.png");
        }
        await a.setViewportSize({width:1366,height:900});
        const add = a.locator('form[data-title-form]').first();
        await add.getByRole("button", {name:"Add to-do",exact:true}).click();
        assert.ok(await a.getByText("Title is required", {exact:true}).isVisible());
        for (const title of ["Buy oat milk", "Finish the database lab", "Review lecture notes"]) {
            await a.locator("#new-title").fill(title);
            await a.getByRole("button", {name:"Add to-do",exact:true}).click();
            await a.waitForLoadState("load");
        }
        assert.equal(await a.locator(".todo-item").count(), 3);
        assert.equal(await b.locator(".todo-item").count(), 0);
        await b.locator("#new-title").fill("Buy oat milk");
        await b.getByRole("button", {name:"Add to-do",exact:true}).click();
        await b.waitForLoadState("load");
        assert.equal(await b.locator(".todo-item").count(), 1);
        await a.locator("#new-title").fill("Buy oat milk");
        await a.getByRole("button", {name:"Add to-do",exact:true}).click();
        assert.ok(await a.getByText("A to-do with this title already exists", {exact:true}).isVisible());
        assert.equal(await a.locator(".todo-item").count(), 3);

        const lecture = a.locator(".todo-item").filter({hasText:"Review lecture notes"});
        const stolen = await lecture.locator("[data-edit-link]").getAttribute("data-edit-link");
        await b.goto(base + `/todos?edit=${stolen}`);
        assert.ok(await b.getByRole("heading", {name:"This page or to-do isn't available"}).isVisible());
        await b.goto(base + "/todos");
        const bToken = await b.locator('input[name="csrf_token"]').first().inputValue();
        for (const [action, form] of [["edit", {title:"Stolen"}], ["done", {status:"done"}], ["delete", {}]]) {
            const response = await b.request.post(base + `/todos/${stolen}/${action}`, {form:{...form, csrf_token:bToken}});
            assert.equal(response.status(), 200);
            assert.match(await response.text(), /To-do not found/);
        }
        await lecture.getByRole("link", {name:"Edit",exact:true}).click();
        if (enabled) {
            for (const width of [1366,360]) await checkLayout(a, "inline editing", width);
            await shot(a, "review-edit-mobile.png");
            await a.setViewportSize({width:1366,height:900});
        }
        await a.getByLabel("Edit title", {exact:true}).fill("Review SQL joins");
        await a.getByRole("button", {name:"Save changes",exact:true}).click();
        await a.waitForLoadState("load");
        assert.ok(await a.locator(".todo-title").filter({hasText:"Review SQL joins"}).isVisible());
        const lab = a.locator(".todo-item").filter({hasText:"Finish the database lab"});
        await lab.getByRole("button", {name:"Mark done",exact:true}).click();
        await a.waitForLoadState("load");
        assert.equal(await a.locator(".todo-item.is-done").count(), 1);
        if (enabled) {
            for (const width of [1366,360]) await checkLayout(a, "populated list", width);
            await shot(a, "04-todos-mobile-360.png");
            await a.setViewportSize({width:1366,height:900});
            await shot(a, "03-todos-desktop.png");
        }
        await lab.getByRole("button", {name:"Mark open",exact:true}).click();
        await a.waitForLoadState("load");
        assert.equal(await a.locator(".todo-item.is-done").count(), 0);

        await a.locator("#new-title").fill("😀".repeat(201));
        await a.getByRole("button", {name:"Add to-do",exact:true}).click();
        assert.ok(await a.getByText("Title is too long", {exact:true}).isVisible());
        assert.equal(await a.locator(".todo-item").count(), 3);
        await a.locator("#new-title").fill("😀".repeat(200));
        await a.getByRole("button", {name:"Add to-do",exact:true}).click();
        await a.waitForLoadState("load");
        assert.equal(await a.locator(".todo-item").count(), 4);
        if (enabled) for (const width of [1366,360]) await checkLayout(a, "long Unicode title", width);
        const longRow = a.locator(".todo-item").filter({hasText:"😀".repeat(200)});
        if (enabled) {
            a.once("dialog", dialog => dialog.dismiss());
            await longRow.getByRole("button", {name:"Delete",exact:true}).click();
            assert.equal(await a.locator(".todo-item").count(), 4);
            a.once("dialog", dialog => dialog.accept());
        }
        if (enabled) {
            await longRow.getByRole("button", {name:"Delete",exact:true}).click();
        } else {
            await longRow.getByRole("link", {name:"Delete",exact:true}).click();
            assert.ok(await a.getByRole("heading", {name:"Delete this to-do?",exact:true}).isVisible());
            await a.getByRole("link", {name:"Cancel",exact:true}).click();
            assert.equal(await a.locator(".todo-item").count(), 4);
            await longRow.getByRole("link", {name:"Delete",exact:true}).click();
            for (const width of [1366,360]) await checkLayout(a, "no-JS delete confirmation", width);
            await shot(a, "review-delete-confirmation-mobile.png");
            await a.getByRole("button", {name:"Delete to-do",exact:true}).click();
        }
        await a.waitForLoadState("load");
        assert.equal(await a.locator(".todo-item").count(), 3);

        const bad = await a.request.post(base + "/todos", {form:{title:"No token"}});
        assert.equal(bad.status(), 400);
        assert.match(await bad.text(), /Please reopen the form/);
        await a.goto(base + "/todos?edit=" + "9".repeat(5000));
        assert.ok(await a.getByRole("heading", {name:"This page or to-do isn't available"}).isVisible());
        if (enabled) {
            for (const width of [1366,360]) await checkLayout(a, "friendly 404", width);
            await shot(a, "review-error-mobile.png");
            await a.goto(base + "/todos");
            await a.locator('form[data-title-form] input[name="csrf_token"]').first().evaluate(el => el.remove());
            await a.locator("#new-title").fill("Missing token check");
            await a.getByRole("button", {name:"Add to-do",exact:true}).click();
            await a.waitForLoadState("load");
            for (const width of [1366,360]) await checkLayout(a, "CSRF recovery", width);
            await shot(a, "review-csrf-mobile.png");
        }
        await a.goto(base + "/todos");
        const stale = await a.locator('input[name="csrf_token"]').first().inputValue();
        await a.getByRole("button", {name:"Log out",exact:true}).click();
        await a.waitForURL(base + "/login");
        const staleResponse = await a.request.post(base + "/todos", {form:{title:"Stale",csrf_token:stale}});
        assert.equal(staleResponse.status(), 400);
        await a.goto(base + "/login");
        await a.getByLabel("Email", {exact:true}).fill(emails[0]);
        await a.getByLabel("Password", {exact:true}).fill("wrong");
        await a.getByRole("button", {name:"Log in",exact:true}).click();
        assert.ok(await a.getByText("Invalid email or password", {exact:true}).isVisible());
        await a.getByLabel("Email", {exact:true}).fill(emails[0]);
        await a.getByLabel("Password", {exact:true}).fill("demo-password");
        await a.getByRole("button", {name:"Log in",exact:true}).click();
        await a.waitForURL(base + "/todos");
        await a.goto(base + "/");
        await a.waitForURL(base + "/todos");
        assert.deepEqual(errors, []);
        console.log(`PASS real browser: JS ${enabled ? "enabled" : "disabled"}; registration/login/logout, privacy, CRUD, duplicate titles, Unicode, CSRF and errors.`);
    } finally { await Promise.all(contexts.map(context => context.close())); }
}

(async () => {
    const browser = await chromium.launch({channel:"chrome",headless:true});
    try { await run(browser,true); await run(browser,false); }
    finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode=1; });

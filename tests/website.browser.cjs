const { chromium } = require(
  process.env.AUTODEV_PLAYWRIGHT_MODULE || "playwright",
);
const fs = require("fs");
const launch = {
  headless: true,
  ...(process.env.AUTODEV_BROWSER_PATH
    ? { executablePath: process.env.AUTODEV_BROWSER_PATH }
    : {}),
};
const site = process.env.AUTODEV_SITE_URL || "http://127.0.0.1:4191/";
(async () => {
  const browser = await chromium.launch(launch);
  const context = await browser.newContext({
    viewport: { width: 1440, height: 960 },
    permissions: ["clipboard-read", "clipboard-write"],
  });
  const page = await context.newPage();
  const errors = [],
    bad = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("response", (r) => {
    if (r.status() >= 400) bad.push(`${r.status()} ${r.url()}`);
  });
  let checks = [];
  const assert = (ok, label) => {
    if (!ok) throw Error(label);
    checks.push(label);
  };
  const settle = async () => {
    await page.waitForTimeout(35);
    await page.waitForFunction(
      () => document.querySelector(".story-stage")?.dataset.settled === "true",
    );
  };
  const jump = async (i) => {
    await page.locator(`[data-chapter='${i}']`).click();
    await settle();
  };
  await page.goto(site);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(200);
  for (const lang of ["en", "zh"]) {
    if (lang === "zh") {
      await page.setViewportSize({ width: 1440, height: 960 });
      await page.waitForTimeout(180);
      await page.locator("[data-lang=zh]").click();
      await page.waitForTimeout(150);
    }
    for (const [width, height] of [
      [1440, 960],
      [1440, 768],
      [1024, 768],
      [800, 700],
      [667, 700],
      [390, 844],
      [320, 740],
    ]) {
      await page.setViewportSize({ width, height });
      await page.waitForTimeout(180);
      for (let i = 0; i < 5; i++) {
        await jump(i);
        const d = await page
          .locator(`.story-panel[data-scene='${i}']`)
          .evaluate((e) => {
            const r = e.querySelector("section").getBoundingClientRect();
            return {
              overflow: document.documentElement.scrollWidth > innerWidth,
              top: r.top,
              header: document.querySelector("header").getBoundingClientRect()
                .bottom,
              particles:
                +document.querySelector(".story-particles").dataset.particles,
              read: +e.dataset.read,
              start: +e.dataset.start,
              bottom: r.bottom,
            };
          });
        assert(
          !d.overflow,
          `${lang} ${width}x${height} scene ${i}: no horizontal overflow`,
        );
        assert(
          d.top >= d.header - 1,
          `${lang} ${width}x${height} scene ${i}: header clear`,
        );
        assert(
          d.particles > 0,
          `${lang} ${width}x${height} scene ${i}: living particles`,
        );
        if (d.read > 0) {
          await page.evaluate((y) => scrollTo(0, y), d.start + d.read);
          await settle();
          const bottom = await page
            .locator(`.story-panel[data-scene='${i}'] section`)
            .evaluate((e) => e.getBoundingClientRect().bottom);
          assert(
            bottom <= height - 75,
            `${lang} ${width}x${height} scene ${i}: full reading distance (${bottom})`,
          );
        }
      }
    }
  }
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.waitForTimeout(200);
  await jump(1);
  for (let i = 0; i < 3; i++) {
    await page.locator(`[data-stage='${i}']`).click();
    assert(
      (await page.locator(".view-stage").textContent()) ===
        ["Clarify", "Loop", "Handoff"][i],
      `workflow stage ${i}`,
    );
    assert(
      (await page.locator(".stage-copy:not([hidden])").count()) === 1,
      "one stage explanation",
    );
  }
  await page.locator('[data-stage="0"]').focus();
  await page.keyboard.press("ArrowRight");
  assert(
    (await page.locator('[data-stage="1"]').getAttribute("aria-pressed")) ===
      "true",
    "stage keyboard starts at focused button",
  );
  await jump(2);
  for (let i = 0; i < 3; i++) {
    await page.locator(`[data-task='${i}']`).click();
    assert(
      await page.locator(`[data-task-panel='${i}']`).isVisible(),
      `task ${i} visible`,
    );
    assert(
      await page.locator(`[data-artifact-shape='${i}']`).first().isVisible(),
      `task ${i} artifact matches`,
    );
    assert(
      (
        await page
          .locator(`[data-task-panel='${i}'] .diagram-link`)
          .getAttribute("href")
      ).includes(".zh.html"),
      `task ${i} Chinese diagram link`,
    );
  }
  await jump(3);
  for (let i = 0; i < 2; i++) {
    await page.locator(`[data-case='${i}']`).click();
    assert(
      await page.locator(`[data-case-panel='${i}']`).isVisible(),
      `case ${i} visible`,
    );
  }
  await jump(4);
  await page.locator(".copy-button").click();
  assert(
    (await page.evaluate(() => navigator.clipboard.readText())) ===
      "npx skills add Momoyeyu/autodev -g",
    "exact clipboard command",
  );
  // Scroll-distance plateaus remain exact; the camera rests while localized particles breathe.
  for (let i = 0; i < 4; i++) {
    await jump(i);
    const start = await page
      .locator(`[data-scene='${i}']`)
      .evaluate((e) => +e.dataset.transitionStart);
    const distance = 960 * 1.45;
    for (const [p, morph] of [
      [0.08, "0.0000"],
      [0.18, "0.0000"],
      [0.82, "1.0000"],
      [0.92, "1.0000"],
    ]) {
      await page.evaluate((y) => scrollTo(0, y), start + p * distance);
      await settle();
      assert(
        (await page.locator(".story-stage").getAttribute("data-morph")) ===
          morph,
        `handover ${i} plateau ${p}`,
      );
    }
    await page.evaluate((y) => scrollTo(0, y), start + 0.5 * distance);
    await settle();
    const mid = +(await page
      .locator(".story-stage")
      .getAttribute("data-morph"));
    assert(mid > 0.45 && mid < 0.55, `handover ${i} mid-morph`);
    await page.evaluate((y) => scrollTo(0, y), start + 0.08 * distance);
    await settle();
    assert(
      (await page.locator(".story-stage").getAttribute("data-morph")) ===
        "0.0000",
      `handover ${i} reverse returns to source`,
    );
  }
  await jump(0);
  const paints = await page.locator(".story-stage").getAttribute("data-paints");
  const frames = +(await page
    .locator(".story-particles")
    .getAttribute("data-frames"));
  await page.waitForTimeout(180);
  assert(
    (await page.locator(".story-stage").getAttribute("data-paints")) === paints,
    "resting composition unchanged over time",
  );
  assert(
    +(await page.locator(".story-particles").getAttribute("data-frames")) >
      frames,
    "local particles remain animated",
  );
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(200);
  await jump(0);
  await page.locator(".menu-toggle").click();
  await page.locator("[data-lang=en]").focus();
  await page.keyboard.press("Enter");
  assert(
    await page
      .locator(".menu-toggle")
      .evaluate((e) => e === document.activeElement),
    "mobile language focus visible",
  );
  assert(
    !(await page.locator("#navigation").isVisible()),
    "language closes mobile menu",
  );
  await page.locator(".menu-toggle").click();
  await page.keyboard.press("Escape");
  assert(
    !(await page.locator("#navigation").isVisible()),
    "Escape closes mobile menu",
  );
  await page.locator(".menu-toggle").click();
  await page.locator('#navigation a[href="#evidence"]').click();
  assert(
    await page
      .locator("#evidence")
      .evaluate((e) => e === document.activeElement),
    "navigation focuses destination",
  );
  await page.waitForTimeout(200);
  assert(
    (await page.locator('[data-chapter="3"]').getAttribute("aria-current")) ===
      "step",
    "deep link opens correct chapter",
  );
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.waitForTimeout(150);
  assert(
    !(await page.locator("html").getAttribute("class")).includes("story-mode"),
    "reduced motion uses reading layout",
  );
  assert(
    await page.locator(".story-particles").isHidden(),
    "reduced motion hides canvas",
  );
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.waitForTimeout(150);
  assert(
    (await page.locator("html").getAttribute("class")).includes("story-mode"),
    "motion can be reenabled",
  );
  await page.setViewportSize({ width: 800, height: 480 });
  await page.waitForTimeout(150);
  assert(
    !(await page.locator("html").getAttribute("class")).includes("story-mode"),
    "short landscape uses reading layout",
  );
  await page.setViewportSize({ width: 1440, height: 960 });
  await page.reload();
  await page.waitForTimeout(200);
  assert(
    (await page.locator("html").getAttribute("lang")) === "en",
    "language preference persists",
  );
  assert(errors.length === 0, `no JS errors ${errors}`);
  assert(bad.length === 0, `no failed resources ${bad}`);
  // Reading fallbacks remain useful without storage, clipboard, JavaScript, or a motion budget.
  const denied = await browser.newContext({
    viewport: { width: 390, height: 844 },
  });
  await denied.addInitScript(() => {
    Object.defineProperty(window, "localStorage", {
      get() {
        throw Error("denied");
      },
    });
    Object.defineProperty(navigator, "clipboard", {
      value: {
        writeText: async () => {
          throw Error("denied");
        },
      },
    });
  });
  const p = await denied.newPage();
  await p.goto(new URL("#start", site).href);
  await p.waitForTimeout(250);
  assert(
    await p.locator("h2#start-title").isVisible(),
    "storage denied still renders target",
  );
  await p.locator(".copy-button").click();
  assert(
    (await p.locator(".copy-status").textContent()).includes("manually"),
    "clipboard denial gives manual instructions",
  );
  await denied.close();
  const nojs = await browser.newContext({
    javaScriptEnabled: false,
    viewport: { width: 390, height: 844 },
  });
  const n = await nojs.newPage();
  await n.goto(site);
  assert(
    await n.locator("#navigation").isVisible(),
    "no JS mobile navigation available",
  );
  assert(
    (await n.locator(".task-panel").count()) === 3,
    "no JS all task content present",
  );
  assert(
    (await n.locator(".case-panel").count()) === 2,
    "no JS both cases present",
  );
  assert(
    (await n.locator(".install-command code").textContent()) ===
      "npx skills add Momoyeyu/autodev -g",
    "no JS installation readable",
  );
  assert(
    await n.evaluate(() => document.documentElement.scrollWidth === innerWidth),
    "no JS no horizontal overflow",
  );
  await nojs.close();
  const data = await browser.newContext({
    viewport: { width: 390, height: 844 },
  });
  await data.addInitScript(() =>
    Object.defineProperty(navigator, "connection", {
      value: { saveData: true, addEventListener() {} },
    }),
  );
  const d = await data.newPage();
  await d.goto(site);
  assert(
    !(await d.locator("html").getAttribute("class")).includes("story-mode"),
    "data saver uses reading layout",
  );
  await data.close();
  console.log(
    JSON.stringify(
      { passed: checks.length, errors, failedResources: bad },
      null,
      2,
    ),
  );
  if (process.env.AUTODEV_RESULTS_FILE)
    fs.writeFileSync(
      process.env.AUTODEV_RESULTS_FILE,
      JSON.stringify({ passed: checks.length, checks, errors, bad }, null, 2),
    );
  await browser.close();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

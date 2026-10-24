import { createStory } from "./story.js";
const root = document.documentElement;
const menu = document.querySelector(".menu-toggle");
const nav = document.querySelector("#navigation");
const copy = document.querySelector(".copy-button");
const status = document.querySelector(".copy-status");
const command = "npx skills add Momoyeyu/autodev -g";
let language = "en";
let stage = 0;
let statusTimer;
const notes = {
  en: [
    "Agree on the API → queue → ledger path and the checks that can support it.",
    "API implemented. Queue work in progress. Ledger integration is still unverified.",
    "Compare the delivered path, checks, and remaining integration gaps before approval.",
  ],
  zh: [
    "对齐 API → 队列 → 账本的路径，以及支撑它的验证方式。",
    "API 已实现，队列仍在开发，账本集成尚未验证。",
    "批准前，对照交付路径、检查结果，以及尚未验证的集成缺口。",
  ],
};
function changed() {
  document.dispatchEvent(new Event("autodev:content-change"));
}
function closeMenu(returnFocus = false) {
  const focusHidden =
    matchMedia("(max-width:600px)").matches &&
    nav.contains(document.activeElement);
  menu.setAttribute("aria-expanded", "false");
  nav.dataset.open = "false";
  menu.textContent = language === "zh" ? "菜单" : "Menu";
  if (returnFocus || focusHidden) menu.focus();
}
function renderStage() {
  document.querySelectorAll("[data-stage]").forEach((button) => {
    const active = Number(button.dataset.stage) === stage;
    button.setAttribute("aria-pressed", String(active));
    button.nextElementSibling.hidden = !active;
    button.setAttribute("aria-expanded", String(active));
  });
  document.querySelector(".system-view").dataset.step = String(stage);
  document.querySelector(".view-stage").textContent = [
    "Clarify",
    "Loop",
    "Handoff",
  ][stage];
  document.querySelector(".view-note").textContent = notes[language][stage];
}
function applyLanguage(next) {
  language = next === "zh" ? "zh" : "en";
  root.lang = language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-en][data-zh]").forEach((element) => {
    element.textContent = element.dataset[language];
  });
  document
    .querySelectorAll("[data-lang]")
    .forEach((button) =>
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.lang === language),
      ),
    );
  document.querySelectorAll("[data-diagram]").forEach((link) => {
    link.href = `diagrams/autodev-${link.dataset.diagram}${language === "zh" ? ".zh" : ""}.html?theme=dark`;
  });
  copy.setAttribute(
    "aria-label",
    language === "zh" ? "复制安装命令" : "Copy installation command",
  );
  nav.setAttribute(
    "aria-label",
    language === "zh" ? "主导航" : "Main navigation",
  );
  document
    .querySelector(".language-switch")
    .setAttribute("aria-label", language === "zh" ? "语言" : "Language");
  document
    .querySelector(".stage-list")
    .setAttribute(
      "aria-label",
      language === "zh" ? "工作阶段" : "Workflow stages",
    );
  document
    .querySelector(".task-tabs")
    .setAttribute("aria-label", language === "zh" ? "任务类型" : "Task type");
  document
    .querySelector(".case-tabs")
    .setAttribute(
      "aria-label",
      language === "zh" ? "实测案例" : "Recorded case",
    );
  const title =
    language === "zh"
      ? "autodev — 让复杂变更始终清晰"
      : "autodev — Clarity for consequential changes";
  const description =
    language === "zh"
      ? "面向复杂变更的 Agent Skill：对齐意图、看见真实进展、交付可审视的证据。"
      : "An Agent Skill for complex changes. Clarify the intent, inspect the work as it develops, and hand over evidence you can examine.";
  document.title = title;
  document.querySelector("meta[name=description]").content = description;
  document.querySelector('meta[property="og:title"]').content = title;
  document.querySelector('meta[property="og:description"]').content =
    description;
  document
    .querySelectorAll(".chart-link")
    .forEach((link) =>
      link.setAttribute(
        "aria-label",
        language === "zh" ? "打开原尺寸图表" : "Open full-size chart",
      ),
    );
  const chartAlts =
    language === "zh"
      ? [
          "BLEU 实测轨迹：基线 24.97，31 次尝试，4 次保留改进，最终验证 30.91。",
          "6 轮、16 次累计尝试，使用同一固定参考尺度；4 轮达成各自目标，最终验证服务不可用。",
        ]
      : [
          "Recorded BLEU trajectory: baseline 24.97, 31 attempts, four retained improvements, final verification 30.91.",
          "Six rounds, 16 cumulative attempts on one fixed-reference scale; four rounds met their targets; final verification unavailable.",
        ];
  document
    .querySelectorAll(".case-chart")
    .forEach((chart, i) => (chart.alt = chartAlts[i]));
  clearTimeout(statusTimer);
  status.textContent = "";
  renderStage();
  closeMenu();
  try {
    localStorage.setItem("autodev-lang", language);
  } catch {}
  changed();
}
function bindChoices(attribute, panelAttribute) {
  const buttons = [...document.querySelectorAll(`[${attribute}]`)];
  function choose(index) {
    buttons.forEach((button, i) =>
      button.setAttribute("aria-pressed", String(i === index)),
    );
    document
      .querySelectorAll(`[${panelAttribute}]`)
      .forEach((panel, i) => (panel.hidden = i !== index));
    if (attribute === "data-task")
      document
        .querySelectorAll("[data-artifact-shape]")
        .forEach(
          (shape) =>
            (shape.style.display =
              Number(shape.dataset.artifactShape) === index ? "" : "none"),
        );
    changed();
  }
  buttons.forEach((button, index) => {
    const panel = document.querySelector(`[${panelAttribute}='${index}']`);
    button.id = `${attribute}-button-${index}`;
    panel.id = `${attribute}-panel-${index}`;
    button.setAttribute("aria-controls", panel.id);
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-labelledby", button.id);
    button.addEventListener("click", () => choose(index));
  });
  choose(0);
}
function bindArrowKeys(selector) {
  const buttons = [...document.querySelectorAll(selector)];
  buttons.forEach((button, index) =>
    button.addEventListener("keydown", (event) => {
      let next;
      if (event.key === "ArrowRight" || event.key === "ArrowDown")
        next = (index + 1) % buttons.length;
      if (event.key === "ArrowLeft" || event.key === "ArrowUp")
        next = (index + buttons.length - 1) % buttons.length;
      if (event.key === "Home") next = 0;
      if (event.key === "End") next = buttons.length - 1;
      if (next === undefined) return;
      event.preventDefault();
      buttons[next].focus();
      buttons[next].click();
    }),
  );
}
document.querySelectorAll("[data-stage]").forEach((button, i) => {
  const panel = button.nextElementSibling;
  panel.id = `stage-copy-${i}`;
  button.setAttribute("aria-controls", panel.id);
  button.addEventListener("click", () => {
    stage = i;
    renderStage();
    changed();
  });
});
document
  .querySelectorAll("[data-lang]")
  .forEach((button) =>
    button.addEventListener("click", () => applyLanguage(button.dataset.lang)),
  );
menu.addEventListener("click", () => {
  const open = menu.getAttribute("aria-expanded") !== "true";
  menu.setAttribute("aria-expanded", String(open));
  nav.dataset.open = String(open);
  menu.textContent =
    language === "zh" ? (open ? "关闭" : "菜单") : open ? "Close" : "Menu";
});
nav.addEventListener("click", (event) => {
  const link = event.target.closest("a");
  if (!link) return;
  closeMenu();
  if (
    link.hash &&
    link.origin === location.origin &&
    link.pathname === location.pathname
  )
    document.getElementById(link.hash.slice(1))?.focus({ preventScroll: true });
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && menu.getAttribute("aria-expanded") === "true")
    closeMenu(true);
});
copy.addEventListener("click", async () => {
  clearTimeout(statusTimer);
  try {
    await navigator.clipboard.writeText(command);
    status.textContent =
      language === "zh" ? "安装命令已复制。" : "Installation command copied.";
  } catch {
    status.textContent =
      language === "zh"
        ? "请选中上方命令，手动复制。"
        : "Select the command above and copy it manually.";
  }
  statusTimer = setTimeout(() => {
    status.textContent = "";
  }, 5000);
});
root.classList.add("interactive-ready");
bindChoices("data-task", "data-task-panel");
bindChoices("data-case", "data-case-panel");
for (const selector of ["[data-stage]", "[data-task]", "[data-case]"])
  bindArrowKeys(selector);
try {
  language = localStorage.getItem("autodev-lang") === "zh" ? "zh" : "en";
} catch {}
applyLanguage(language);
createStory();

import { fileURLToPath } from "node:url";

const port = "9224";
const downloadPath = fileURLToPath(new URL("./output/judge-demo-export-sterile/", import.meta.url));
const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const page = targets.find((target) => target.type === "page" && target.url.startsWith("http://127.0.0.1:8112/"));
if (!page) throw new Error("Military SLICES page target not found");

const socket = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});
let nextId = 1;
const pending = new Map();
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  const waiter = pending.get(message.id);
  if (!waiter) return;
  pending.delete(message.id);
  if (message.error) waiter.reject(new Error(JSON.stringify(message.error)));
  else waiter.resolve(message.result);
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = nextId++;
  pending.set(id, { resolve, reject });
  socket.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression) => {
  const result = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || "Evaluation failed");
  return result.result?.value;
};
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const waitFor = async (expression, label, timeoutMs = 30000) => {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    if (await evaluate(`Boolean(${expression})`)) return;
    await sleep(250);
  }
  throw new Error(`Timed out waiting for ${label}`);
};
const clickText = async (text) => {
  await evaluate(`(() => { const e=[...document.querySelectorAll("button")].find(x=>x.offsetParent!==null&&x.innerText.trim()===${JSON.stringify(text)}); if(!e) throw new Error("Missing button: ${text}"); e.scrollIntoView({block:"center"}); e.click(); return true; })()`);
};
const clickId = async (id) => {
  await evaluate(`(() => { const e=document.querySelector(${JSON.stringify(`#${id}`)}); if(!e) throw new Error("Missing id: ${id}"); e.scrollIntoView({block:"center"}); e.click(); return true; })()`);
};
const setValue = async (selector, value) => {
  await evaluate(`(() => { const e=document.querySelector(${JSON.stringify(selector)}); if(!e) throw new Error("Missing field: ${selector}"); e.value=${JSON.stringify(value)}; e.dispatchEvent(new Event("input",{bubbles:true})); e.dispatchEvent(new Event("change",{bubbles:true})); e.focus(); e.scrollIntoView({block:"center"}); return true; })()`);
};
const ledger = [];
const mark = (event) => { ledger.push({ event, epoch_ms: Date.now() }); };
const hold = async (event, ms = 1800) => { mark(event); await sleep(ms); };

await send("Browser.setDownloadBehavior", { behavior: "allow", downloadPath, eventsEnabled: true });
await send("Page.navigate", { url: "http://127.0.0.1:8112/?journey=judge-clean-final-sterile" });
await waitFor(`document.querySelector("#starting-timeline")`, "landing");
await hold("landing_visible", 2000);

await evaluate(`(() => { const set=(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}));e.dispatchEvent(new Event("change",{bubbles:true}))}; document.querySelector('input[name="operating-role"][value="veteran_service_member"]').click(); set(document.querySelector("#starting-timeline"),"leaving_within_12_months"); set(document.querySelector("#starting-month"),"2027-05"); set(document.querySelector("#starting-service"),"navy"); set(document.querySelector("#starting-component"),"active_duty"); document.querySelector("button[type=submit]").scrollIntoView({block:"center"}); return true; })()`);
await hold("starting_vector_complete");
await clickText("Continue");
await waitFor(`document.body.innerText.includes("You don’t need the whole plan yet.")`, "front door");
await hold("front_door_visible", 1500);
await clickText("Tell me what’s going on");
await waitFor(`document.querySelector("#cold-input-text")`, "cold input");
await setValue("#cold-input-text", "I'm 23 and leaving the Navy on May 15, 2027. I led a five-person logistics team and managed schedules and supplies. My wife starts nursing school in Tacoma on February 1, 2027, so we need to stay nearby. I want steady, meaningful work with some remote flexibility, and I am curious about building better transition tools for veterans.");
await hold("initial_objective_entered", 2200);
await clickText("See what matters first");
await waitFor(`document.body.innerText.includes("Check this before it shapes your plan.")`, "objective review");
await hold("first_governed_response_visible", 2200);
await clickId("confirm-review");
await waitFor(`document.body.innerText.includes("Which direction is worth testing first?")`, "direction prompt");
await hold("approved_objective_saved", 1800);
await setValue("#gate-value", "Logistics Analyst");
await hold("direction_answer_entered", 1400);
await clickText("Turn this into directions");
await waitFor(`document.querySelector("#confirm-review")`, "direction review");
await hold("direction_review_visible", 1400);
await clickId("confirm-review");
await waitFor(`document.querySelector("#choose-current-direction")`, "directions");
await hold("directions_visible", 2200);
await clickId("choose-current-direction");
await waitFor(`document.querySelector("#bundle-answer-2")`, "bundled questions");
await hold("bundled_questions_visible", 1600);
await setValue("#bundle-answer-0", "I can analyze a public shipment-delay example without using protected information.");
await setValue("#bundle-answer-1", "A one-page analysis showing the delay, cause, and recommended fix would show how I think.");
await setValue("#bundle-answer-2", "By September 22, 2026, I will turn one Navy supply problem into a public, civilian-style analysis and ask a logistics analyst to review it.");
await hold("bundled_answers_entered", 2400);
await clickText("Use these decisions");
await waitFor(`document.querySelector("#add-direction-learning")`, "working direction");
await hold("real_world_experiment_visible", 2600);
await clickId("add-direction-learning");
await waitFor(`document.querySelector("#input-text")`, "test result input");
await setValue("#input-text", "On October 6, 2026, a logistics analyst reviewed my work sample. I liked finding the delay and explaining it clearly. I want to keep this direction and test it against a real job posting next.");
await hold("test_result_entered", 2000);
await clickText("Review update");
await waitFor(`document.querySelector("#confirm-review")`, "test result review");
await hold("test_result_review_visible", 2000);
await clickId("confirm-review");
await waitFor(`document.querySelector("#gate-value")`, "reconsidered evidence gate");
await hold("updated_consequence_visible", 1700);
await setValue("#gate-value", "I can analyze a public shipment-delay example without using protected information.");
await clickText("Use this decision");
await waitFor(`document.body.innerText.includes("What work sample would show a civilian team how you think?")`, "work sample gate");
await setValue("#gate-value", "A one-page analysis showing the delay, cause, and recommended fix would show how I think.");
await clickText("Use this decision");
await waitFor(`document.body.innerText.includes("Build one small analysis from public information")`, "test plan gate");
await setValue("#gate-value", "By September 22, 2026, I will turn one Navy supply problem into a public, civilian-style analysis and ask a logistics analyst to review it.");
await clickText("Use this decision");
await waitFor(`document.querySelector("#plan-next-direction-test")`, "post-result choice");
await hold("post_result_choice_visible", 2000);
await clickId("plan-next-direction-test");
await waitFor(`document.querySelector("#input-text")`, "next test input");
await setValue("#input-text", "By October 20, 2026, I will compare one Tacoma-area logistics analyst posting with my Navy logistics experience and mark the resume gaps.");
await hold("next_experiment_entered", 1800);
await clickText("Review update");
await waitFor(`document.querySelector("#confirm-review")`, "next test review");
await hold("next_experiment_review_visible", 1600);
await clickId("confirm-review");
await waitFor(`document.querySelector("#open-transition-plan")`, "plan button");
await sleep(1800);
await clickId("open-transition-plan");
await waitFor(`document.querySelector("#add-plan-dates")`, "plan modal");
await hold("plan_opened_for_timeline", 2200);
await clickId("add-plan-dates");
await waitFor(`document.querySelector("#input-text")`, "timeline input");
await setValue("#input-text", "My TAP counseling appointment is September 15, 2026. My resume draft is due November 15, 2026. I will review it with my counselor on November 22, 2026. I plan to start applications on January 15, 2027. We will decide our Tacoma commute or move by February 15, 2027. My separation date is May 15, 2027. I want a post-separation check-in on June 15, 2027.");
await hold("timeline_entered", 2400);
await clickText("Review update");
await waitFor(`document.querySelector("#confirm-review")`, "timeline review");
await hold("timeline_review_visible", 2200);
await clickId("confirm-review");
await waitFor(`document.querySelector("#open-transition-plan")`, "plan after timeline");
await sleep(2000);
await clickId("open-transition-plan");
await waitFor(`document.body.innerText.includes("Jun 15, 2027")`, "complete timeline", 45000);
await evaluate(`document.querySelector("#export-transition-plan").scrollIntoView({block:"start"})`);
await hold("complete_plan_visible", 3500);
await evaluate(`document.querySelector("#export-transition-plan").click()`);
await hold("export_activated", 3000);
mark("export_complete");

console.log(JSON.stringify({ ledger, final_url: await evaluate("location.href"), june_visible: await evaluate(`document.body.innerText.includes("Jun 15, 2027")`) }));
socket.close();

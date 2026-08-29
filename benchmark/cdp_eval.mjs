const port = process.argv[2] || "9223";
const source = process.argv[3] === "--file"
  ? await (await import("node:fs/promises")).readFile(process.argv[4], "utf8")
  : Buffer.from(process.argv[3] || "", "base64").toString("utf8");
const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const page = targets.find((target) => target.type === "page" && target.url.startsWith("http://127.0.0.1:8112/"));
if (!page) throw new Error("Military SLICES page target not found");
const socket = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});
const id = 1;
socket.send(JSON.stringify({ id, method: "Runtime.evaluate", params: { expression: source, awaitPromise: true, returnByValue: true } }));
const response = await new Promise((resolve, reject) => {
  const timeout = setTimeout(() => reject(new Error("CDP evaluation timed out")), 30000);
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id !== id) return;
    clearTimeout(timeout);
    resolve(message);
  });
});
socket.close();
if (response.error) throw new Error(JSON.stringify(response.error));
if (response.result?.exceptionDetails) throw new Error(response.result.exceptionDetails.text || "Evaluation failed");
console.log(JSON.stringify(response.result?.result?.value ?? null));

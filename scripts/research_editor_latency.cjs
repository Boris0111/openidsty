// Typing latency of the /admin draft editor in the restore drill (headless Chromium, drill owner login).
//
//   node scripts/research_editor_latency.cjs --draft <id> --path <file> --mode raw|form --label <name> [--trace]
//
// Each key's latency is the Event Timing duration (the same definition as INP): the longest entry of the key's
// interaction, from the key press to the next frame. Entries under 16 ms are not reported by the browser and are
// recorded as "<16" (counted as 16 in the statistics). A key that does not finish within --timeout (default
// 180 s) is a failure; the run continues. With --trace, the whole typing run is traced and main-thread tasks over
// 50 ms are summarised by script, style/layout, paint, GC and other. The drill owner password comes from the
// drill env file in INDUSTRYFLOW_DRILL_HOME and is never printed or written to the report.
// Writes .work/research-editor-latency/<label>.json (and <label>.trace.json with --trace).
'use strict';
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {execFileSync} = require('node:child_process');

const ROOT = path.resolve(__dirname, '..');
const REPORTS = path.join(ROOT, '.work', 'research-editor-latency');
const THRESHOLD = 16; // the smallest durationThreshold the Event Timing API accepts
const LONG_TASK_US = 50000;
const OPTIONS = {
  draft: {help: 'draft id (research_draft_bench.py reports draft_id)'},
  path: {help: 'research file, e.g. industry-map/research-relations.yaml'},
  mode: {help: 'raw (Markdown/YAML text) or form (research body textarea)', default: 'raw'},
  keys: {help: 'characters to type (default 30)', default: '30'},
  interval: {help: 'pause between keys in ms (default 150)', default: '150'},
  timeout: {help: 'longest wait per key in ms (default 180000)', default: '180000'},
  label: {help: 'report name, e.g. before-scaled-relations'},
  origin: {help: 'drill web origin (default http://127.0.0.1:3016)', default: 'http://127.0.0.1:3016'},
  'env-file': {help: 'drill env file (default INDUSTRYFLOW_DRILL_HOME/.env.research-drill)'},
  trace: {help: 'record a performance trace and summarise long main-thread tasks', flag: true},
};

function usage() {
  return ['usage: node scripts/research_editor_latency.cjs --draft <id> --path <file> --mode raw|form --label <name> [--trace]', '',
    ...Object.entries(OPTIONS).map(([name, option]) => `  --${name.padEnd(10)} ${option.help}`)].join('\n');
}

function parseArgs(argv) {
  const args = {};
  for (const [name, option] of Object.entries(OPTIONS)) if (option.default !== undefined) args[name] = option.default;
  for (let index = 0; index < argv.length; index++) {
    const token = argv[index];
    if (token === '--help' || token === '-h') return {help: true};
    const name = token.replace(/^--/, '');
    if (!token.startsWith('--') || !OPTIONS[name]) throw new Error('unknown argument ' + token);
    if (OPTIONS[name].flag) args[name] = true;
    else if (index + 1 < argv.length) args[name] = argv[++index];
    else throw new Error('missing value for ' + token);
  }
  for (const name of ['draft', 'path', 'label']) if (!args[name]) throw new Error('--' + name + ' is required');
  if (!['raw', 'form'].includes(args.mode)) throw new Error('--mode must be raw or form');
  if (!/^[\w.-]+$/.test(args.label)) throw new Error('--label may contain letters, digits, dot, dash and underscore only');
  for (const name of ['keys', 'interval', 'timeout']) {
    args[name] = Number(args[name]);
    if (!Number.isInteger(args[name]) || args[name] < (name === 'keys' ? 1 : 0)) throw new Error('--' + name + ' must be a whole number');
  }
  return args;
}

/** Nearest-rank percentile, the same rule as research_draft_bench.py; null for an empty sample. */
function percentile(values, q) {
  if (!values.length) return null;
  const ordered = [...values].sort((a, b) => a - b);
  return ordered[Math.max(0, Math.ceil(q / 100 * ordered.length) - 1)];
}

/**
 * Assign Event Timing entries to keys. Key i owns the interactions that started in [starts[i], next start);
 * an interaction's latency is the longest duration among its entries (keydown, keypress, keyup). A key whose
 * start is null was never pressed and gets null.
 */
function keyLatencies(starts, entries) {
  const interactions = new Map();
  for (const entry of entries) {
    if (!entry.interactionId) continue;
    const current = interactions.get(entry.interactionId) || {start: entry.startTime, duration: 0};
    current.start = Math.min(current.start, entry.startTime);
    current.duration = Math.max(current.duration, entry.duration);
    interactions.set(entry.interactionId, current);
  }
  return starts.map((start, index) => {
    if (start === null) return null;
    const end = starts.slice(index + 1).find(value => value !== null) ?? Infinity;
    let longest = null;
    for (const interaction of interactions.values()) {
      if (interaction.start >= start && interaction.start < end) longest = Math.max(longest ?? 0, interaction.duration);
    }
    return longest;
  });
}

/** Per-key results and statistics; "<16" counts as 16 and a timeout as at least the timeout. */
function summarize(keys, timeoutMs) {
  const values = keys.map(key => {
    if (key.timed_out) return Math.max(key.latency_ms ?? 0, timeoutMs);
    return key.latency_ms ?? THRESHOLD;
  });
  return {
    count: keys.length,
    p50_ms: percentile(values, 50),
    p95_ms: percentile(values, 95),
    max_ms: values.length ? Math.max(...values) : null,
    below_threshold: keys.filter(key => !key.timed_out && key.latency_ms === null).length,
    timeouts: keys.filter(key => key.timed_out).length,
    values: keys.map(key => key.timed_out ? 'timeout' : key.latency_ms === null ? '<16' : key.latency_ms),
  };
}

const CATEGORIES = [
  ['gc', name => /^(MinorGC|MajorGC|V8\.GC|BlinkGC\.|CppGC|GCEvent|ThreadState::)/.test(name)],
  ['script', name => /^(FunctionCall|EvaluateScript|TimerFire|FireAnimationFrame|FireIdleCallback|RunMicrotasks|XHRReadyStateChange|v8\.|V8\.Execute|V8\.Compile|V8\.ScriptCompiler)/.test(name)],
  ['style_layout', name => /^(UpdateLayoutTree|RecalculateStyles|Layout|UpdateLayerTree|HitTest|ScheduleStyleRecalculation|InvalidateLayout|LayoutShift)$/.test(name)],
  ['paint', name => /^(Paint|PaintImage|PrePaint|Layerize|CompositeLayers|Commit|RasterTask|UpdateLayer|PaintSetup|Decode Image)$/.test(name)],
];

function category(name) {
  for (const [label, test] of CATEGORIES) if (test(name)) return label;
  return 'other';
}

/** Complete events per thread from X events and B/E pairs. */
function completeEvents(traceEvents) {
  const out = [];
  const open = new Map();
  for (const event of traceEvents) {
    if (event.ph === 'X' && typeof event.dur === 'number') out.push({name: event.name, pid: event.pid, tid: event.tid, ts: event.ts, dur: event.dur});
    else if (event.ph === 'B') {
      const key = event.pid + ':' + event.tid;
      if (!open.has(key)) open.set(key, []);
      open.get(key).push(event);
    } else if (event.ph === 'E') {
      const begin = (open.get(event.pid + ':' + event.tid) || []).pop();
      if (begin) out.push({name: begin.name, pid: begin.pid, tid: begin.tid, ts: begin.ts, dur: event.ts - begin.ts});
    }
  }
  return out;
}

/**
 * Long main-thread tasks (RunTask over 50 ms on the renderer main thread with the most task time), each split
 * by self time into script, style/layout, paint, GC and other; "other" also lists its largest event names.
 */
function traceSummary(traceEvents, top = 10) {
  const mains = new Set(traceEvents.filter(event => event.ph === 'M' && event.name === 'thread_name' && event.args?.name === 'CrRendererMain')
    .map(event => event.pid + ':' + event.tid));
  const events = completeEvents(traceEvents);
  const taskTime = new Map();
  for (const event of events) {
    const key = event.pid + ':' + event.tid;
    if (event.name === 'RunTask' && mains.has(key)) taskTime.set(key, (taskTime.get(key) || 0) + event.dur);
  }
  const main = [...taskTime.entries()].sort((a, b) => b[1] - a[1])[0]?.[0];
  if (!main) return {main_thread: null, long_tasks: 0, total_ms: 0, by_category_ms: {}, other_top: [], longest: []};
  const thread = events.filter(event => event.pid + ':' + event.tid === main).sort((a, b) => a.ts - b.ts || b.dur - a.dur);
  const tasks = thread.filter(event => event.name === 'RunTask' && event.dur > LONG_TASK_US);
  const ms = us => Math.round(us / 100) / 10;
  const totals = {script: 0, style_layout: 0, paint: 0, gc: 0, other: 0};
  const otherNames = new Map();
  const longest = [];
  for (const task of tasks) {
    const end = task.ts + task.dur;
    const inside = thread.filter(event => event !== task && event.ts >= task.ts && event.ts + event.dur <= end);
    // Self time: each event minus its direct children, found with a stack over start-ordered events.
    const self = new Map([[task, task.dur]]);
    const stack = [task];
    for (const event of inside) {
      while (stack.length > 1 && event.ts >= stack[stack.length - 1].ts + stack[stack.length - 1].dur) stack.pop();
      const parent = stack[stack.length - 1];
      self.set(parent, self.get(parent) - event.dur);
      self.set(event, event.dur);
      stack.push(event);
    }
    const split = {script: 0, style_layout: 0, paint: 0, gc: 0, other: 0};
    for (const [event, value] of self) {
      const label = category(event.name);
      split[label] += Math.max(0, value);
      if (label === 'other') otherNames.set(event.name, (otherNames.get(event.name) || 0) + Math.max(0, value));
    }
    for (const key of Object.keys(totals)) totals[key] += split[key];
    longest.push({start_ms: ms(task.ts), duration_ms: ms(task.dur), by_category_ms: Object.fromEntries(Object.entries(split).map(([key, value]) => [key, ms(value)]))});
  }
  longest.sort((a, b) => b.duration_ms - a.duration_ms);
  return {
    main_thread: main,
    long_tasks: tasks.length,
    total_ms: ms(tasks.reduce((sum, task) => sum + task.dur, 0)),
    by_category_ms: Object.fromEntries(Object.entries(totals).map(([key, value]) => [key, ms(value)])),
    other_top: [...otherNames.entries()].sort((a, b) => b[1] - a[1]).slice(0, top).map(([name, value]) => ({name, ms: ms(value)})),
    longest: longest.slice(0, top),
  };
}

function envFile(given) {
  if (given) return given;
  const home = process.env.INDUSTRYFLOW_DRILL_HOME || path.join(os.homedir(), 'industryflow-drill');
  return path.join(home, '.env.research-drill');
}

/** DRILL_OWNER_PASSWORD from the drill env file; the value never reaches output or the report. */
function drillPassword(file) {
  const text = fs.readFileSync(file, 'utf8');
  for (const line of text.split(/\r?\n/)) if (line.startsWith('DRILL_OWNER_PASSWORD=')) return line.slice('DRILL_OWNER_PASSWORD='.length);
  throw new Error('drill env file has no DRILL_OWNER_PASSWORD; run research_drill.py setup and owner first');
}

function within(promise, ms) {
  let timer;
  return Promise.race([promise.then(value => ({value})), new Promise(resolve => { timer = setTimeout(() => resolve({timedOut: true}), ms); })])
    .finally(() => clearTimeout(timer));
}

function quiet(command, args) {
  try { return execFileSync(command, args, {encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore']}).trim(); } catch { return null; }
}

async function measure(args) {
  const {chromium} = require('../frontend/node_modules/@playwright/test');
  const password = drillPassword(envFile(args['env-file']));
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message.slice(0, 300)));
  try {
    await page.goto(args.origin + '/admin');
    await page.getByLabel('密碼').fill(password);
    await page.getByRole('button', {name: '登入', exact: true}).click();
    const drafts = page.getByLabel('工作草稿');
    await drafts.locator(`option[value="${args.draft}"]`).waitFor({state: 'attached', timeout: 60000});
    await drafts.selectOption(args.draft);
    const files = page.getByLabel('研究檔案');
    await files.waitFor({timeout: 120000});
    if (await files.inputValue() !== args.path) {
      await files.selectOption(args.path);
    }
    const idle = async () => { await page.waitForFunction(() => document.querySelector('[role=status]')?.textContent !== '處理中…', null, {timeout: 300000}); };
    // The file select is controlled by the loaded document, so it shows the path once that document arrived.
    await page.waitForFunction(path => [...document.querySelectorAll('select')].some(select => select.value === path), args.path, {timeout: 300000});
    await idle();
    if (args.mode === 'raw') {
      const toggle = page.getByRole('button', {name: '切換 Markdown', exact: true});
      if (await toggle.count()) { await toggle.click(); await idle(); }
    }
    const box = args.mode === 'raw' ? page.getByLabel('Markdown／YAML') : page.getByLabel('研究內文（Markdown）');
    await box.waitFor({timeout: 300000});
    const chars = await box.evaluate(element => element.value.length);
    const supported = await page.evaluate(() => PerformanceObserver.supportedEntryTypes.includes('event'));
    if (!supported) throw new Error('this Chromium does not support the Event Timing API');
    await page.evaluate(threshold => {
      window.__latency = [];
      new PerformanceObserver(list => {
        for (const entry of list.getEntries()) window.__latency.push({name: entry.name, interactionId: entry.interactionId, startTime: entry.startTime, duration: entry.duration});
      }).observe({type: 'event', durationThreshold: threshold, buffered: true});
    }, THRESHOLD);
    await box.evaluate(element => { element.focus(); const middle = Math.floor(element.value.length / 2); element.setSelectionRange(middle, middle); });
    if (args.trace) await browser.startTracing(page, {categories: ['devtools.timeline', 'disabled-by-default-devtools.timeline', 'v8', 'v8.execute', 'blink', 'toplevel', 'disabled-by-default-v8.gc']});
    const starts = [];
    const keys = [];
    const letters = 'abcdefghijklmnopqrstuvwxyz';
    for (let index = 0; index < args.keys; index++) {
      const now = await within(page.evaluate(() => performance.now()), args.timeout);
      // A page still frozen by the previous key: this key is not pressed and has no window of its own.
      if (now.timedOut) { keys.push({key: index, timed_out: true, press_ms: null}); starts.push(null); continue; }
      starts.push(now.value);
      const began = Date.now();
      const pressed = await within(page.keyboard.press(letters[index % letters.length]), args.timeout);
      keys.push({key: index, timed_out: Boolean(pressed.timedOut), press_ms: Date.now() - began});
      await new Promise(resolve => setTimeout(resolve, args.interval));
    }
    // Event Timing entries arrive after the frame that ends them; wait for the page to settle first.
    await within(page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => setTimeout(resolve, 1000)))), args.timeout);
    let trace = null;
    if (args.trace) {
      const buffer = await browser.stopTracing();
      fs.mkdirSync(REPORTS, {recursive: true});
      fs.writeFileSync(path.join(REPORTS, args.label + '.trace.json'), buffer);
      trace = traceSummary(JSON.parse(buffer.toString('utf8')).traceEvents || []);
    }
    const entries = (await within(page.evaluate(() => window.__latency), args.timeout)).value || [];
    const latencies = keyLatencies(starts, entries);
    keys.forEach((key, index) => { key.latency_ms = latencies[index] ?? null; });
    return {chars, keys, trace, errors, chromium: browser.version()};
  } finally {
    await browser.close();
  }
}

async function main(argv = process.argv.slice(2)) {
  let args;
  try { args = parseArgs(argv); } catch (error) { console.error(error.message + '\n\n' + usage()); process.exitCode = 2; return; }
  if (args.help) { console.log(usage()); return; }
  const measured = await measure(args);
  const report = {
    label: args.label, draft_id: args.draft, path: args.path, mode: args.mode, chars: measured.chars,
    keys_typed: args.keys, interval_ms: args.interval, timeout_ms: args.timeout,
    latency: summarize(measured.keys, args.timeout), keys: measured.keys,
    method: 'Event Timing: longest entry duration per interaction (key press to next frame); entries under 16 ms are not reported and count as 16',
    trace: measured.trace, page_errors: measured.errors,
    environment: {origin: args.origin, chromium: measured.chromium, headless: true, viewport: '1280x720', node: process.version,
      platform: process.platform + ' ' + os.release(), checkout_commit: quiet('git', ['-C', ROOT, 'rev-parse', '--short', 'HEAD']),
      web_image: quiet('docker', ['inspect', '--format', '{{.Image}}', 'industryflow-research-drill-web-1']),
      api_image: quiet('docker', ['inspect', '--format', '{{.Image}}', 'industryflow-research-drill-api-1'])},
    measured_at: new Date().toISOString(),
  };
  fs.mkdirSync(REPORTS, {recursive: true});
  fs.writeFileSync(path.join(REPORTS, args.label + '.json'), JSON.stringify(report, null, 2));
  const {values, ...stats} = report.latency;
  console.log(JSON.stringify({label: report.label, chars: report.chars, ...stats, trace: report.trace && {long_tasks: report.trace.long_tasks, total_ms: report.trace.total_ms, by_category_ms: report.trace.by_category_ms}}, null, 2));
}

module.exports = {percentile, keyLatencies, summarize, traceSummary, category, completeEvents, parseArgs, drillPassword, envFile, THRESHOLD};

if (require.main === module) main().catch(error => { console.error(error.stack || String(error)); process.exit(1); });

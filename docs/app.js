async function load() {
  const el = document.getElementById("app");
  try {
    const res = await fetch("./data/usage.json?ts=" + Date.now(), { cache: "no-store" });
    if (!res.ok) throw new Error("Kon usage.json nie laai nie");
    const data = await res.json();
    render(data);
  } catch (e) {
    el.innerHTML = `<div class="empty">Geen data nog.<br>${e.message}</div>`;
  }
}

function fmtPct(v) {
  if (v === null || v === undefined) return "—";
  return `${Number(v).toFixed(0)}%`;
}

function statusLabel(s) {
  return ({
    voor: "voor skedule",
    agter: "agter skedule",
    reg: "op skedule",
    wag_vir_lesing: "wag vir % uit Settings",
  })[s] || s;
}

function render(data) {
  const meta = document.getElementById("meta");
  meta.textContent = `Week ${data.week_start} → ${data.week_end} · Vandag ${data.today} · ${data.days_left_in_week} dag(e) oor · Weekdag ${data.daily_budget_pct_of_week.weekdag}% / naweek ${data.daily_budget_pct_of_week.naweek}% van week`;

  const order = ["claude", "chatgpt", "grok"];
  const cards = order.map((key) => {
    const p = data.providers[key];
    if (!p) return "";
    const day = p.day_remaining_pct;
    const week = p.week_remaining_pct;
    return `
      <article class="card" data-p="${key}">
        <h2>${p.label} <span class="badge">${p.day_type}</span></h2>
        <div class="row">
          <span class="label">Oor vandag (pacing)</span>
          <span class="pct">${fmtPct(day)}</span>
        </div>
        <div class="bar"><i style="width:${day ?? 0}%"></i></div>
        <div class="row">
          <span class="label">Oor hierdie week</span>
          <span class="pct">${fmtPct(week)}</span>
        </div>
        <div class="bar"><i style="width:${week ?? 0}%"></i></div>
        <p class="hint">
          <span class="status-${p.pace_status}">${statusLabel(p.pace_status)}</span>
          · ${p.note || ""}
          ${p.week_pct_used != null ? ` · Usage wys ${p.week_pct_used}% gebruik` : ""}
        </p>
      </article>`;
  }).join("");

  document.getElementById("app").innerHTML = `<div class="cards">${cards}</div>`;
  document.getElementById("updated").textContent = `Laas bereken: ${data.updated_at}`;
}

load();
setInterval(load, 60_000);

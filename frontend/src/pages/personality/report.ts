/**
 * Builds a polished, self-contained HTML report for a Big Five result and opens
 * it in a new window ready to print / save as PDF. No external dependencies —
 * everything (styles + SVG bars) is inlined so the saved file is fully portable.
 */
import type { AssessmentResult } from './types';
import { TRAIT_ORDER, TRAIT_TINT } from './types';

const FORM_LABEL: Record<string, string> = {
  bfi44: 'BFI-44 · Quick Assessment',
  ipip120: 'IPIP-NEO-120 · Comprehensive Assessment',
  legacy: 'Big Five Short Form',
};

const LEVEL_BG: Record<string, string> = {
  Low: '#eef2f7',
  Moderate: '#e0edff',
  High: '#dcfce7',
};
const LEVEL_FG: Record<string, string> = {
  Low: '#64748b',
  Moderate: '#2563eb',
  High: '#16a34a',
};

const esc = (s: unknown): string =>
  String(s ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

function traitRows(result: AssessmentResult): string {
  return TRAIT_ORDER.map((t) => {
    const s = result.scores[t];
    if (!s) return '';
    const tint = TRAIT_TINT[t] || '#6366f1';
    return `
      <div class="trait">
        <div class="trait-head">
          <span class="trait-name"><span class="dot" style="background:${tint}"></span>${esc(s.label)}</span>
          <span class="trait-right">
            <span class="level" style="background:${LEVEL_BG[s.level]};color:${LEVEL_FG[s.level]}">${esc(s.level)}</span>
            <b>${esc(s.percentage)}%</b>
          </span>
        </div>
        <div class="bar"><div class="fill" style="width:${s.percentage}%;background:${tint}"></div></div>
        <div class="raw">Raw ${esc(s.raw_score)} · range ${esc(s.min_score)}–${esc(s.max_score)}</div>
      </div>`;
  }).join('');
}

function listItems(items?: string[]): string {
  if (!items || !items.length) return '<li class="muted">None flagged.</li>';
  return items.map((i) => `<li>${esc(i)}</li>`).join('');
}

export function buildReportHtml(result: AssessmentResult, candidateName?: string): string {
  const meta = result.assessment_metadata;
  const insights = result.workplace_behavioral_insights || {};
  const flagged = result.compliance?.status === 'Flagged';
  const timeLabel =
    meta.completion_time_seconds != null
      ? `${Math.floor(meta.completion_time_seconds / 60)}m ${meta.completion_time_seconds % 60}s`
      : '—';
  const dateLabel = result.completed_at
    ? new Date(result.completed_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })
    : new Date().toLocaleDateString();

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Big Five Personality Report</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #0f172a; margin: 0; background: #f1f5f9; }
  .page { max-width: 800px; margin: 24px auto; background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(2,6,23,0.08); }
  .head { padding: 32px 40px; background: linear-gradient(135deg, #6d28d9, #db2777); color: #fff; }
  .brand { display: flex; align-items: center; gap: 12px; }
  .brand .logo { width: 42px; height: 42px; border-radius: 11px; background: rgba(255,255,255,0.18); display: flex; align-items: center; justify-content: center; font-size: 22px; }
  .brand h1 { margin: 0; font-size: 22px; }
  .brand p { margin: 2px 0 0; font-size: 13px; opacity: 0.9; }
  .meta { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 20px; font-size: 13px; }
  .meta div span { opacity: 0.8; display: block; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; }
  .meta div b { font-size: 14px; }
  .body { padding: 32px 40px; }
  .section-title { font-size: 15px; font-weight: 700; margin: 0 0 14px; color: #1e293b; }
  .section-title.sp { margin-top: 30px; }
  .trait { padding: 12px 0; border-bottom: 1px solid #eef2f7; }
  .trait:last-child { border-bottom: none; }
  .trait-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 7px; }
  .trait-name { display: flex; align-items: center; gap: 9px; font-weight: 600; font-size: 14px; }
  .dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
  .trait-right { display: flex; align-items: center; gap: 12px; font-size: 14px; }
  .level { font-size: 11px; font-weight: 700; padding: 2px 9px; border-radius: 999px; }
  .bar { height: 10px; border-radius: 6px; background: #eef2f7; overflow: hidden; }
  .fill { height: 100%; border-radius: 6px; }
  .raw { font-size: 11px; color: #94a3b8; margin-top: 5px; }
  .cards { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .card { padding: 16px 18px; border-radius: 12px; border: 1px solid #e2e8f0; }
  .card.good { background: #f0fdf4; border-color: #bbf7d0; }
  .card.warn { background: #fffbeb; border-color: #fde68a; }
  .card h3 { margin: 0 0 10px; font-size: 13px; }
  .card ul { margin: 0; padding-left: 18px; }
  .card li { font-size: 13px; margin-bottom: 7px; line-height: 1.5; }
  .muted { color: #94a3b8; }
  .team { margin-top: 16px; padding: 16px 18px; border-radius: 12px; background: #eef2ff; border: 1px solid #c7d2fe; font-size: 13px; line-height: 1.55; }
  .compliance { display: inline-flex; align-items: center; gap: 6px; padding: 5px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; }
  .compliance.pass { background: #dcfce7; color: #16a34a; }
  .compliance.flag { background: #fee2e2; color: #dc2626; }
  .flag-note { margin-top: 12px; padding: 12px 16px; border-left: 3px solid #ef4444; background: #fef2f2; font-size: 12.5px; color: #7f1d1d; border-radius: 0 8px 8px 0; }
  .foot { padding: 18px 40px 30px; font-size: 11px; color: #94a3b8; border-top: 1px solid #eef2f7; }
  .print-hint { max-width: 800px; margin: 12px auto; text-align: center; }
  .print-hint button { background: #6d28d9; color: #fff; border: none; padding: 10px 22px; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; }
  @media print {
    body { background: #fff; }
    .page { box-shadow: none; margin: 0; max-width: none; border-radius: 0; }
    .print-hint { display: none; }
    .head { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    .fill, .level, .card, .team, .compliance { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>
</head>
<body>
  <div class="print-hint">
    <button onclick="window.print()">Save as PDF / Print</button>
  </div>

  <div class="page">
    <div class="head">
      <div class="brand">
        <div class="logo">🧠</div>
        <div>
          <h1>Big Five Personality Report</h1>
          <p>OCEAN framework · workplace behavioural profile</p>
        </div>
      </div>
      <div class="meta">
        ${candidateName ? `<div><span>Candidate</span><b>${esc(candidateName)}</b></div>` : ''}
        <div><span>Assessment</span><b>${esc(FORM_LABEL[meta.form] || meta.form)}</b></div>
        <div><span>Questions</span><b>${esc(meta.completed_questions)}/${esc(meta.total_questions)}</b></div>
        <div><span>Time taken</span><b>${esc(timeLabel)}</b></div>
        <div><span>Date</span><b>${esc(dateLabel)}</b></div>
      </div>
    </div>

    <div class="body">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
        <p class="section-title" style="margin:0">Trait scores</p>
        <span class="compliance ${flagged ? 'flag' : 'pass'}">${flagged ? '⚠ Compliance: Flagged' : '✓ Compliance: Passed'}</span>
      </div>
      ${flagged ? `<div class="flag-note">${esc(result.compliance?.notes || 'Response pattern flagged — results may be less reliable.')}</div>` : ''}

      <div style="margin-top:14px">${traitRows(result)}</div>

      <p class="section-title sp">Workplace behavioural insights</p>
      <div class="cards">
        <div class="card good">
          <h3>✓ Key strengths</h3>
          <ul>${listItems(insights.key_strengths)}</ul>
        </div>
        <div class="card warn">
          <h3>⚠ Potential challenges</h3>
          <ul>${listItems(insights.potential_challenges)}</ul>
        </div>
      </div>

      ${insights.team_collaboration_style
        ? `<div class="team"><b>Team collaboration style</b><br/>${esc(insights.team_collaboration_style)}</div>`
        : ''}
    </div>

    <div class="foot">
      Scores are computed deterministically from the standard psychometric key (reverse-keyed items included).
      Levels: Low &lt; 35%, Moderate 35–65%, High &gt; 65%. This report describes workplace-relevant tendencies and
      is not a clinical or diagnostic instrument.
    </div>
  </div>
</body>
</html>`;
}

/** Open the report in a new tab, ready to print / save as PDF. */
export function openReport(result: AssessmentResult, candidateName?: string): void {
  const html = buildReportHtml(result, candidateName);
  const win = window.open('', '_blank');
  if (win) {
    win.document.open();
    win.document.write(html);
    win.document.close();
    return;
  }
  // Popup blocked — fall back to downloading the HTML file.
  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `big-five-report-${result.assessment_metadata.form}.html`;
  a.click();
  URL.revokeObjectURL(url);
}

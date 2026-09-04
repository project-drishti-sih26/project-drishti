import { readFileSync } from 'fs';
import { normalizeAlertData } from './gis/utils/dataNormalizer.js';

const raw = JSON.parse(readFileSync('./sample_alert_payload.json', 'utf-8'));
const a = normalizeAlertData(raw);

let fails = 0;
const ck = (name, ok, detail = '') => {
  if (!ok) fails++;
  console.log(`  [${ok ? 'PASS' : 'FAIL'}] ${name}${detail ? `  -> ${detail}` : ''}`);
};

console.log('\n=== GIS NORMALIZER vs REAL ML PAYLOAD ===');
ck('5 targets normalized', a.targets.length === 5, `${a.targets.length}`);

const pcts = a.targets.map(t => t.scorePercent);
ck('Scores are NOT the old hardcoded 75 for all', new Set(pcts).size > 1, `${pcts.join(', ')}`);
ck('Rank-1 score matches engine probability_pct',
   Math.round(raw.top_5_atms[0].probability_pct) === pcts[0],
   `engine ${raw.top_5_atms[0].probability_pct}% vs ui ${pcts[0]}%`);
ck('Scores descend by rank', pcts.every((p, i) => i === 0 || pcts[i-1] >= p), `${pcts.join(' >= ')}`);

const tiers = a.targets.map(t => t.riskTier);
ck('Tiers carried from engine', tiers[0] === 'CRITICAL' && new Set(tiers).size > 1, tiers.join(', '));

const etas = a.targets.map(t => t.travelTime);
ck('Every target has a travel ETA', etas.every(e => e && /\d+ mins/.test(e)), etas.join(', '));

ck('Origin = mule last known location (not the 28.6289 default)',
   a.originLat === raw.mule_last_latitude && a.originLng === raw.mule_last_longitude,
   `${a.originLat},${a.originLng} vs engine ${raw.mule_last_latitude},${raw.mule_last_longitude}`);
ck('Origin flagged as known', a.originKnown === true);

ck('Explanations are the real SHAP text, not the 3 invented strings',
   a.explanation.length === 5 && a.explanation.every(e => e.startsWith('Rank #')),
   `${a.explanation.length} reasons; first="${(a.explanation[0]||'').slice(0,60)}..."`);
ck('No fabricated "High proximity to recent mule account activity"',
   !a.explanation.some(e => e.includes('High proximity to recent mule account activity')));

ck('Window shown in IST, from the survival model',
   /IST/.test(a.withdrawalWindow || ''), a.withdrawalWindow);
ck('Window source recorded', a.windowSource === 'CoxProportionalHazards', a.windowSource);

ck('Alert risk = top target probability (not the 0.92 default)',
   Math.abs(a.riskScore - raw.top_5_atms[0].confidence_score) < 1e-9,
   `${a.riskScore} vs ${raw.top_5_atms[0].confidence_score}`);
ck('degraded flag propagated', a.degraded === false);
ck('Scorecard reaches the UI', !!a.modelScorecard?.top5_hit_rate,
   `Top-5 ${a.modelScorecard?.top5_hit_rate}`);
ck('Candidate pool size reaches the UI', a.totalCandidatesEvaluated === raw.total_candidates_evaluated,
   `${a.totalCandidatesEvaluated}`);

// H3 hexagons: riskCells is empty, so MapRadar must fall through to targets.
ck('riskCells empty => hex layer must use targets', a.riskCells.length === 0,
   `riskCells=${a.riskCells.length}`);
ck('All targets carry a usable h3Index for the hex layer',
   a.targets.every(t => typeof t.h3Index === 'string' && t.h3Index.length === 15),
   a.targets.map(t => t.h3Index).join(', '));

console.log(`\n  ${fails === 0 ? 'ALL PASS' : fails + ' FAILED'}\n`);
process.exit(fails === 0 ? 0 : 1);

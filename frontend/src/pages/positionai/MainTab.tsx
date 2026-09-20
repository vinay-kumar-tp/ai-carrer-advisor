import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Plus, Save, Target, TrendingUp, X } from 'lucide-react';
import api from '../../services/api';
import { errorMessage } from '../profile/useProfileData';
import { JdSelect } from './JdSelect';
import type { Analysis, JdOption, SkillsResponse } from './types';

type Props = {
  notify: (message: string, tone?: 'success' | 'error') => void;
  onAnalysisSaved: (analysisId: string | null) => void;
};

const MAX_JDS = 3;

export const MainTab: React.FC<Props> = ({ notify, onAnalysisSaved }) => {
  const [options, setOptions] = useState<JdOption[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [jdText, setJdText] = useState('');

  const [skills, setSkills] = useState<string[]>([]);
  const [savedSkills, setSavedSkills] = useState<string[]>([]);
  const [skillDraft, setSkillDraft] = useState('');
  const [savingSkills, setSavingSkills] = useState(false);

  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(true);

  const skillsRef = useRef<HTMLInputElement>(null);

  // ── Initial load: JD options + the candidate's saved skills ──
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [jdRes, skillRes] = await Promise.all([
          api.get<JdOption[]>('/position-ai/jobs'),
          api.get<SkillsResponse>('/candidate/skills'),
        ]);
        if (!alive) return;
        setOptions(jdRes.data);
        setSkills(skillRes.data.skills);
        setSavedSkills(skillRes.data.skills);
      } catch (error) {
        if (alive) notify(errorMessage(error, 'Could not load Position AI data.'), 'error');
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, [notify]);

  const dirty = useMemo(() => {
    if (skills.length !== savedSkills.length) return true;
    const a = [...skills].sort();
    const b = [...savedSkills].sort();
    return a.some((s, i) => s !== b[i]);
  }, [skills, savedSkills]);

  // ── Live gap analysis (preview only — not written to History) ──
  const runAnalysis = useCallback(
    async (save: boolean) => {
      if (selectedIds.length === 0 && !jdText.trim()) {
        setAnalysis(null);
        return;
      }
      setAnalyzing(true);
      try {
        const { data } = await api.post<Analysis>('/position-ai/analyze', {
          job_ids: selectedIds,
          jd_text: jdText.trim(),
          save,
        });
        setAnalysis(data);
        if (save) {
          onAnalysisSaved(data.id);
          notify('Gap analysis saved to History');
        }
      } catch (error) {
        notify(errorMessage(error, 'Could not run the gap analysis.'), 'error');
      } finally {
        setAnalyzing(false);
      }
    },
    [selectedIds, jdText, notify, onAnalysisSaved],
  );

  // Re-run the preview whenever the JD selection changes (the design shows
  // missing skills appearing as soon as JDs are picked).
  useEffect(() => {
    if (loading) return;
    if (selectedIds.length === 0) {
      if (!jdText.trim()) setAnalysis(null);
      return;
    }
    runAnalysis(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedIds, loading]);

  const toggleJd = (id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= MAX_JDS) {
        notify(`You can compare up to ${MAX_JDS} job descriptions at a time.`, 'error');
        return prev;
      }
      return [...prev, id];
    });
  };

  // ── Skill chip management ──
  const addSkill = (raw: string) => {
    const name = raw.trim();
    if (!name) return;
    if (skills.some((s) => s.toLowerCase() === name.toLowerCase())) {
      notify(`"${name}" is already in your skills.`, 'error');
      return;
    }
    setSkills((prev) => [...prev, name]);
    setSkillDraft('');
  };

  const removeSkill = (name: string) => setSkills((prev) => prev.filter((s) => s !== name));

  const saveSkills = async () => {
    setSavingSkills(true);
    try {
      const { data } = await api.put<SkillsResponse>('/candidate/skills', { skills });
      setSkills(data.skills);
      setSavedSkills(data.skills);
      notify('Skills saved');
      // Recompute against the freshly saved skill set.
      if (selectedIds.length > 0 || jdText.trim()) runAnalysis(false);
    } catch (error) {
      notify(errorMessage(error, 'Could not save your skills.'), 'error');
    } finally {
      setSavingSkills(false);
    }
  };

  // Scope panel: prefer the analyzed scope, else derive from the picked options
  // so the panel fills in immediately on selection.
  const scope = useMemo(() => {
    if (analysis?.scope?.length) return analysis.scope;
    return selectedIds
      .map((id) => options.find((o) => o.id === id))
      .filter((o): o is JdOption => Boolean(o))
      .map((o) => ({
        id: o.id,
        title: o.title,
        company: o.company,
        location: o.location,
        source: 'job' as const,
        sample_skills: o.required_skills.slice(0, 4),
        extra_count: Math.max(0, o.required_skills.length - 4),
      }));
  }, [analysis, selectedIds, options]);

  if (loading) return <div className="pai-loading">Loading your skills and job descriptions…</div>;

  return (
    <div className="pai-cols">
      {/* ── Left column ─────────────────────────────────── */}
      <div className="pai-col">
        <section className="pai-card">
          <h2 className="pai-card-title" style={{ marginBottom: '0.9rem' }}>
            Your Skills
          </h2>

          <span className="pai-label">Target Job Descriptions</span>
          <JdSelect options={options} selectedIds={selectedIds} max={MAX_JDS} onToggle={toggleJd} />

          <div className="pai-hint">
            <span>Rank your profile only against the job descriptions you pick here.</span>
            <button type="button" className="pai-hint-link" onClick={() => skillsRef.current?.focus()}>
              Manage your skills
            </button>
          </div>

          <div className="pai-chips">
            {skills.map((skill) => (
              <span key={skill} className="pai-chip">
                {skill}
                <button
                  type="button"
                  className="pai-chip-x"
                  onClick={() => removeSkill(skill)}
                  aria-label={`Remove ${skill}`}
                >
                  <X size={9} />
                </button>
              </span>
            ))}
            {skills.length === 0 && <span className="pai-empty-text">No skills yet — add a few below.</span>}
          </div>

          <div className="pai-total">
            Total <b>{skills.length}</b> skills
          </div>

          <div className="pai-row">
            <input
              ref={skillsRef}
              className="pai-input"
              placeholder="Type a skill and press Enter"
              value={skillDraft}
              onChange={(e) => setSkillDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addSkill(skillDraft);
                }
              }}
            />
            <button type="button" className="pai-btn pai-btn-outline" onClick={() => addSkill(skillDraft)}>
              <Plus size={14} /> Add
            </button>
          </div>

          <div className="pai-actions">
            <button
              type="button"
              className="pai-btn pai-btn-primary"
              onClick={saveSkills}
              disabled={savingSkills || !dirty}
            >
              <Save size={14} /> {savingSkills ? 'Saving…' : 'Save Changes'}
            </button>
          </div>
        </section>

        {/* Paste a raw JD instead of (or alongside) picking saved ones. */}
        <section className="pai-card">
          <div className="pai-card-head">
            <h2 className="pai-card-title">Paste a Job Description</h2>
          </div>
          <textarea
            className="pai-textarea"
            placeholder="Paste Job Description here…"
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
          <div className="pai-actions">
            <button
              type="button"
              className="pai-btn pai-btn-primary"
              onClick={() => runAnalysis(true)}
              disabled={analyzing || (selectedIds.length === 0 && !jdText.trim())}
            >
              <Target size={14} /> {analyzing ? 'Analyzing…' : 'Analyze Job Fit'}
            </button>
          </div>
        </section>

        <section className="pai-card">
          <div className="pai-card-head">
            <h2 className="pai-card-title">Gap Analysis Scope</h2>
            <span className="pai-pill">
              {selectedIds.length}/{MAX_JDS} selected
            </span>
          </div>

          {scope.length === 0 ? (
            <div className="pai-empty-box">
              <div className="pai-empty-title">No job descriptions selected</div>
              <div className="pai-empty-text">Select up to {MAX_JDS} JDs to see missing skills.</div>
            </div>
          ) : (
            <div>
              {scope.map((jd) => (
                <div key={jd.id} className="pai-scope-item">
                  <div className="pai-scope-top">
                    <div style={{ minWidth: 0 }}>
                      <div className="pai-scope-title">{jd.title}</div>
                      <div className="pai-scope-meta">
                        {[jd.company, jd.location].filter(Boolean).join(' - ')}
                      </div>
                    </div>
                    <span className={`pai-pill${jd.source === 'text' ? ' is-info' : ''}`}>
                      {jd.source === 'text' ? 'Skills + JD text' : 'Structured skills'}
                    </span>
                  </div>
                  <div className="pai-chips">
                    {jd.sample_skills.map((s) => (
                      <span key={s} className="pai-chip is-plain">
                        {s}
                      </span>
                    ))}
                  </div>
                  {jd.extra_count > 0 && <div className="pai-more">+{jd.extra_count} more</div>}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>

      {/* ── Right column ────────────────────────────────── */}
      <div className="pai-col">
        {analysis && (
          <section className="pai-card">
            <div className="pai-score">
              <div>
                <div className="pai-score-label">Readiness Match</div>
                <div className="pai-score-value">{analysis.matchPercentage}% Match</div>
              </div>
              <span className="pai-pill">
                {analysis.matchedSkills.length} matched · {analysis.missingSkills.length} missing
              </span>
            </div>
            <div className="pai-score-bar">
              <div className="pai-score-fill" style={{ width: `${analysis.matchPercentage}%` }} />
            </div>

            {analysis.matchedSkills.length > 0 && (
              <>
                <div className="pai-total" style={{ marginBottom: '0.4rem' }}>
                  Matched skills
                </div>
                <div className="pai-chips">
                  {analysis.matchedSkills.map((s) => (
                    <span key={s} className="pai-chip is-matched">
                      {s}
                    </span>
                  ))}
                </div>
              </>
            )}
          </section>
        )}

        <section className="pai-card">
          <div>
            <h2 className="pai-card-title">
              <TrendingUp size={16} color="#f59e0b" /> Missing Skills
            </h2>
            <div className="pai-missing-sub">
              {analysis?.selectedJdCount ?? selectedIds.length} selected JDs · {skills.length} profile skills
            </div>
          </div>
          <div className="pai-missing-divider" />

          {!analysis || analysis.missingSkills.length === 0 ? (
            <div className="pai-missing-empty">
              {analysis
                ? 'No gaps found — your profile covers every skill in the selected JDs.'
                : 'Select job descriptions to see missing skills.'}
            </div>
          ) : (
            <div>
              {analysis.missingSkills.map((item) => {
                const pct = item.total_jds > 0 ? (item.jd_count / item.total_jds) * 100 : 0;
                const already = skills.some((s) => s.toLowerCase() === item.skill.toLowerCase());
                return (
                  <div key={item.skill} className="pai-missing-item">
                    <div className="pai-missing-top">
                      <div className="pai-missing-left">
                        <span className="pai-chip">{item.skill}</span>
                        <button
                          type="button"
                          className="pai-add-btn"
                          onClick={() => addSkill(item.skill)}
                          disabled={already}
                          aria-label={`Add ${item.skill} to your skills`}
                          title={already ? 'Already in your skills' : `Add ${item.skill}`}
                        >
                          <Plus size={14} />
                        </button>
                      </div>
                      <span className="pai-missing-count">
                        {item.jd_count}/{item.total_jds} JDs
                      </span>
                    </div>
                    <div className="pai-missing-bar">
                      <div className="pai-missing-fill" style={{ width: `${pct}%` }} />
                    </div>
                    <div className="pai-missing-jd">{item.top_jd_title}</div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

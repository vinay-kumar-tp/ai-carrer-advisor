import React, { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Pencil, Trash2 } from 'lucide-react';
import api from '../../services/api';
import {
  Card,
  ConfirmDialog,
  EMPTY,
  EmptyState,
  Loading,
  Modal,
  Pill,
  StatTile,
} from '../../components/profile/ui';
import { FormGrid, NumberField, SelectField, TextAreaField, TextField } from '../../components/profile/forms';
import { errorMessage } from './useProfileData';
import type { Scorecard, ScorecardEntryRow } from './types';

type Props = { notify: (message: string, tone?: 'success' | 'error') => void };

type EntryDraft = {
  id: string;
  category: 'other' | 'custom_event';
  title: string;
  score: number | null;
  max_score: number | null;
  scored_on: string;
  notes: string;
};

const emptyEntry = (category: 'other' | 'custom_event'): EntryDraft => ({
  id: '',
  category,
  title: '',
  score: null,
  max_score: null,
  scored_on: '',
  notes: '',
});

const PERSONALITY_LABELS: Record<string, string> = {
  openness: 'Openness',
  conscientiousness: 'Conscientiousness',
  extraversion: 'Extraversion',
  agreeableness: 'Agreeableness',
  neuroticism: 'Neuroticism',
};

export const ScorecardTab: React.FC<Props> = ({ notify }) => {
  const [data, setData] = useState<Scorecard | null>(null);
  const [loading, setLoading] = useState(true);
  const [assessType, setAssessType] = useState<'all' | 'assignment' | 'practice'>('all');

  const [editing, setEditing] = useState<EntryDraft | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingDelete, setPendingDelete] = useState<ScorecardEntryRow | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  const load = useCallback(
    async (type: typeof assessType) => {
      setLoading(true);
      try {
        const { data: payload } = await api.get<Scorecard>('/profile/scorecard', {
          params: { assess_type: type },
        });
        setData(payload);
      } catch (err) {
        notify(errorMessage(err, 'Could not load your scorecard.'), 'error');
      } finally {
        setLoading(false);
      }
    },
    [notify],
  );

  useEffect(() => {
    load(assessType);
  }, [load, assessType]);

  const saveEntry = async () => {
    if (!editing) return;
    setBusy(true);
    setError(null);
    const body = {
      category: editing.category,
      title: editing.title.trim(),
      score: editing.score ?? 0,
      max_score: editing.max_score,
      scored_on: editing.scored_on,
      notes: editing.notes,
    };
    try {
      if (editing.id) await api.put(`/profile/scorecard/entries/${editing.id}`, body);
      else await api.post('/profile/scorecard/entries', body);
      setEditing(null);
      notify(editing.id ? 'Score updated' : 'Score added');
      await load(assessType);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const removeEntry = async () => {
    if (!pendingDelete) return;
    setDeleteBusy(true);
    try {
      await api.delete(`/profile/scorecard/entries/${pendingDelete.id}`);
      notify('Score removed');
      await load(assessType);
    } catch (err) {
      notify(errorMessage(err), 'error');
    } finally {
      setDeleteBusy(false);
      setPendingDelete(null);
    }
  };

  if (loading && !data) return <Loading label="Loading your scorecard..." />;
  if (!data) return null;

  const { stats } = data;

  const entryList = (rows: ScorecardEntryRow[], category: 'other' | 'custom_event', emptyText: string) => (
    <>
      {rows.length === 0 ? (
        <EmptyState
          title={category === 'other' ? 'No custom scores have been added yet' : 'No custom event scores have been added yet'}
          text={emptyText}
          actionLabel="Add score"
          onAction={() => {
            setEditing(emptyEntry(category));
            setError(null);
          }}
        />
      ) : (
        <div className="mp-table-wrap">
          <table className="mp-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Score</th>
                <th>Date</th>
                <th>Notes</th>
                <th style={{ width: 80 }} />
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id}>
                  <td style={{ fontWeight: 700, color: '#1f2937' }}>{row.title}</td>
                  <td className="mp-num">
                    {row.score}
                    {row.max_score ? `/${row.max_score}` : ''}
                  </td>
                  <td>{row.scored_on || EMPTY}</td>
                  <td>{row.notes || EMPTY}</td>
                  <td>
                    <div style={{ display: 'flex', gap: '0.25rem' }}>
                      <button
                        className="mp-iconbtn is-plain"
                        aria-label={`Edit ${row.title}`}
                        onClick={() => {
                          setEditing({
                            id: row.id,
                            category: row.category as 'other' | 'custom_event',
                            title: row.title,
                            score: row.score,
                            max_score: row.max_score,
                            scored_on: row.scored_on,
                            notes: row.notes,
                          });
                          setError(null);
                        }}
                      >
                        <Pencil size={13} />
                      </button>
                      <button
                        className="mp-iconbtn is-danger"
                        aria-label={`Delete ${row.title}`}
                        onClick={() => setPendingDelete(row)}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );

  return (
    <div className="mp-col">
      {/* Assessments */}
      <Card
        title="Assessments"
        subtitle={`Total assessments taken: ${stats.total_attempted}/${stats.total_available}`}
        actions={
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <label className="mp-field-label" style={{ margin: 0 }} htmlFor="mp-assess-type">
              Assess. type
            </label>
            <select
              id="mp-assess-type"
              className="mp-select"
              style={{ width: 130 }}
              value={assessType}
              onChange={(e) => setAssessType(e.target.value as typeof assessType)}
            >
              <option value="all">All</option>
              <option value="assignment">Assignment</option>
              <option value="practice">Practice</option>
            </select>
          </div>
        }
      >
        <div className="mp-stats">
          <StatTile
            label="Attempt rate"
            value={`${stats.attempt_rate.toFixed(2)} %`}
            note={`${stats.total_attempted}/${stats.total_available}`}
            tone="violet"
          />
          <StatTile label="Avg score" value={`${stats.avg_score.toFixed(2)} %`} tone="blue" />
          <StatTile label="Highest score" value={`${stats.highest_score.toFixed(2)} %`} tone="green" />
          <StatTile label="Lowest score" value={`${stats.lowest_score.toFixed(2)} %`} tone="red" />
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
          <div className="mp-field-label" style={{ margin: 0 }}>
            Score
          </div>
          <Link to="/assessments" className="mp-btn-link">
            View all in Assessments page
          </Link>
        </div>

        {data.assessments.length === 0 ? (
          <EmptyState title="No assessments available yet" text="Assessments appear here once they're published." />
        ) : (
          <div className="mp-table-wrap">
            <table className="mp-table">
              <thead>
                <tr>
                  <th>Assessment name</th>
                  <th style={{ width: 120 }}>Type</th>
                  <th style={{ width: 110 }}>Attempts</th>
                  <th style={{ width: 120 }}>Score</th>
                </tr>
              </thead>
              <tbody>
                {data.assessments.map((row) => (
                  <tr key={`${row.type}-${row.name}`}>
                    <td style={{ fontWeight: 600, color: '#1f2937' }}>{row.name}</td>
                    <td>
                      <Pill tone="info">{row.type}</Pill>
                    </td>
                    <td>{row.attempts || 0}</td>
                    <td className="mp-num">
                      {row.score}/{row.max_score}
                      {row.percentage !== null && (
                        <span className="mp-inline-note"> ({row.percentage.toFixed(0)}%)</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* AI mock interviews */}
      <Card title="AI Mock Interviews" subtitle={`Total sessions: ${data.mock_interviews.length}`}>
        {data.mock_interviews.length === 0 ? (
          <EmptyState
            title="You have not attempted any Mock Interviews yet"
            text="Start attempting mock interviews to display your scores here."
          />
        ) : (
          <div className="mp-table-wrap">
            <table className="mp-table">
              <thead>
                <tr>
                  <th>Context</th>
                  <th style={{ width: 120 }}>Mode</th>
                  <th style={{ width: 120 }}>Overall</th>
                  <th style={{ width: 120 }}>Status</th>
                  <th style={{ width: 130 }}>Date</th>
                </tr>
              </thead>
              <tbody>
                {data.mock_interviews.map((row) => (
                  <tr key={row.id}>
                    <td style={{ fontWeight: 600, color: '#1f2937' }}>{row.job_context}</td>
                    <td>{row.mode}</td>
                    <td className="mp-num">{row.overall_score === null ? EMPTY : row.overall_score}</td>
                    <td>
                      <Pill tone={row.is_completed ? 'ready' : 'draft'}>{row.is_completed ? 'Completed' : 'In progress'}</Pill>
                    </td>
                    <td>{row.created_at ? new Date(row.created_at).toLocaleDateString('en-GB') : EMPTY}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Personality */}
      {data.personality && (
        <Card title="Personality Profile" subtitle="From your completed personality test">
          <div className="mp-stats">
            {Object.entries(data.personality).map(([trait, value]) => (
              <StatTile
                key={trait}
                label={PERSONALITY_LABELS[trait] || trait}
                value={`${Number(value).toFixed(1)}`}
                tone="amber"
              />
            ))}
          </div>
        </Card>
      )}

      {/* Other scores */}
      <Card
        title="Other Scores"
        subtitle={`Total scores: ${data.other_scores.length}`}
        onAdd={() => {
          setEditing(emptyEntry('other'));
          setError(null);
        }}
        addLabel="Add other score"
      >
        {entryList(data.other_scores, 'other', 'Track scores from external tests or platforms.')}
      </Card>

      {/* Custom event scores */}
      <Card
        title="Custom Event Score"
        subtitle={`Total scores: ${data.custom_event_scores.length}`}
        onAdd={() => {
          setEditing(emptyEntry('custom_event'));
          setError(null);
        }}
        addLabel="Add event score"
      >
        {entryList(data.custom_event_scores, 'custom_event', 'Record hackathons, contests and campus events.')}
      </Card>

      {editing && (
        <Modal
          title={editing.id ? 'Edit Score' : 'Add Score'}
          onClose={() => setEditing(null)}
          onSubmit={saveEntry}
          busy={busy}
          error={error}
        >
          <FormGrid>
            <TextField
              label="Title"
              value={editing.title}
              onChange={(v) => setEditing((d) => (d ? { ...d, title: v } : d))}
              required
              span
              placeholder="e.g. National Coding Contest"
            />
            <SelectField
              label="Category"
              value={editing.category}
              onChange={(v) => setEditing((d) => (d ? { ...d, category: v as 'other' | 'custom_event' } : d))}
              options={[
                { value: 'other', label: 'Other score' },
                { value: 'custom_event', label: 'Custom event score' },
              ]}
              allowBlank={false}
            />
            <TextField
              label="Date"
              type="date"
              value={editing.scored_on}
              onChange={(v) => setEditing((d) => (d ? { ...d, scored_on: v } : d))}
            />
            <NumberField
              label="Score"
              value={editing.score}
              onChange={(v) => setEditing((d) => (d ? { ...d, score: v } : d))}
              step={0.01}
            />
            <NumberField
              label="Out of"
              value={editing.max_score}
              onChange={(v) => setEditing((d) => (d ? { ...d, max_score: v } : d))}
              step={0.01}
            />
            <TextAreaField
              label="Notes"
              value={editing.notes}
              onChange={(v) => setEditing((d) => (d ? { ...d, notes: v } : d))}
              rows={3}
            />
          </FormGrid>
        </Modal>
      )}

      {pendingDelete && (
        <ConfirmDialog
          title="Delete score"
          message={`Remove "${pendingDelete.title}" from your scorecard?`}
          busy={deleteBusy}
          onConfirm={removeEntry}
          onClose={() => setPendingDelete(null)}
        />
      )}
    </div>
  );
};

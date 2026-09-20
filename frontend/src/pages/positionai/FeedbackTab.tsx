import React, { useState } from 'react';
import { Send } from 'lucide-react';
import api from '../../services/api';
import { errorMessage } from '../profile/useProfileData';

type Props = {
  notify: (message: string, tone?: 'success' | 'error') => void;
  analysisId: string | null;
};

type Answers = {
  score_satisfaction: boolean;
  skill_breakdown_accuracy: boolean;
  relevance_weighting_ok: boolean;
  missing_skill_accuracy: boolean;
};

const Toggle: React.FC<{ value: boolean; onChange: (v: boolean) => void; label: string }> = ({
  value,
  onChange,
  label,
}) => (
  <span className="pai-fb-toggle">
    <span className={`pai-fb-toggle-label${value ? ' is-yes' : ''}`}>{value ? 'Yes' : 'No'}</span>
    <button
      type="button"
      role="switch"
      aria-checked={value}
      aria-label={label}
      className={`pai-switch${value ? ' is-on' : ''}`}
      onClick={() => onChange(!value)}
    />
  </span>
);

export const FeedbackTab: React.FC<Props> = ({ notify, analysisId }) => {
  const [answers, setAnswers] = useState<Answers>({
    score_satisfaction: false,
    skill_breakdown_accuracy: false,
    relevance_weighting_ok: false,
    missing_skill_accuracy: false,
  });
  const [relevanceComment, setRelevanceComment] = useState('');
  const [missingComment, setMissingComment] = useState('');
  const [comments, setComments] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const set = (key: keyof Answers) => (value: boolean) => setAnswers((prev) => ({ ...prev, [key]: value }));

  const submit = async () => {
    setSubmitting(true);
    try {
      await api.post('/position-ai/feedback', {
        analysis_id: analysisId,
        ...answers,
        relevance_comment: relevanceComment,
        missing_skill_comment: missingComment,
        comments,
      });
      notify('Thanks — your feedback was submitted');
      setRelevanceComment('');
      setMissingComment('');
      setComments('');
      setAnswers({
        score_satisfaction: false,
        skill_breakdown_accuracy: false,
        relevance_weighting_ok: false,
        missing_skill_accuracy: false,
      });
    } catch (error) {
      notify(errorMessage(error, 'Could not submit your feedback.'), 'error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="pai-fb-head">
        <h3>Share Your Feedback</h3>
        <p>Help us improve Position AI by sharing your experience with the matching algorithm.</p>
      </div>

      <div className="pai-fb-card">
        <div className="pai-fb-row">
          <div className="pai-fb-q">
            <span className="pai-fb-q-text">Are you happy with the current score for the given match?</span>
            <Toggle
              value={answers.score_satisfaction}
              onChange={set('score_satisfaction')}
              label="Are you happy with the current score for the given match?"
            />
          </div>
        </div>

        <div className="pai-fb-row">
          <div className="pai-fb-q">
            <span className="pai-fb-q-text">Are you happy with the skill distribution?</span>
            <Toggle
              value={answers.skill_breakdown_accuracy}
              onChange={set('skill_breakdown_accuracy')}
              label="Are you happy with the skill distribution?"
            />
          </div>
        </div>

        <div className="pai-fb-row">
          <div className="pai-fb-q">
            <span className="pai-fb-q-text">Do you think some skills are incorrectly assigned higher relevance?</span>
            <Toggle
              value={answers.relevance_weighting_ok}
              onChange={set('relevance_weighting_ok')}
              label="Do you think some skills are incorrectly assigned higher relevance?"
            />
          </div>
          {answers.relevance_weighting_ok && (
            <div className="pai-fb-followup">
              <textarea
                className="pai-textarea"
                placeholder="Please specify which skills and why…"
                value={relevanceComment}
                onChange={(e) => setRelevanceComment(e.target.value)}
              />
            </div>
          )}
        </div>

        <div className="pai-fb-row">
          <div className="pai-fb-q">
            <span className="pai-fb-q-text">Do you think some skills are missing?</span>
            <Toggle
              value={answers.missing_skill_accuracy}
              onChange={set('missing_skill_accuracy')}
              label="Do you think some skills are missing?"
            />
          </div>
          {answers.missing_skill_accuracy && (
            <div className="pai-fb-followup">
              <textarea
                className="pai-textarea"
                placeholder="Please specify which skills are missing…"
                value={missingComment}
                onChange={(e) => setMissingComment(e.target.value)}
              />
            </div>
          )}
        </div>

        <div className="pai-fb-row">
          <label className="pai-label" htmlFor="pai-extra-feedback">
            Additional comments
          </label>
          <textarea
            id="pai-extra-feedback"
            className="pai-textarea"
            placeholder="Anything else we should know about the match quality?"
            value={comments}
            onChange={(e) => setComments(e.target.value)}
          />
        </div>

        <div className="pai-fb-foot">
          <button type="button" className="pai-btn pai-btn-primary" onClick={submit} disabled={submitting}>
            <Send size={14} /> {submitting ? 'Submitting…' : 'Submit Feedback'}
          </button>
        </div>
      </div>
    </div>
  );
};

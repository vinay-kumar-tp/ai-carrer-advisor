import React, { useEffect, useState } from 'react';
import { CheckCircle2, ListChecks, Clock } from 'lucide-react';
import api from '../../services/api';
import { Loading } from '../../components/codequest/ui';
import type { FormMeta } from './types';

interface Props {
  onStart: (formKey: string) => void;
}

export const VersionChooser: React.FC<Props> = ({ onStart }) => {
  const [forms, setForms] = useState<FormMeta[] | null>(null);

  useEffect(() => {
    api.get<FormMeta[]>('/personality/forms').then(({ data }) => setForms(data)).catch(() => setForms([]));
  }, []);

  if (!forms) return <Loading label="Loading assessments…" />;

  const quick = forms.find((f) => f.key === 'bfi44');
  const comp = forms.find((f) => f.key === 'ipip120');

  return (
    <div className="glass-card pt-choose">
      <h3>Start Your Assessment</h3>
      <p className="sub">Select how deep you want to go. You can retake either version at any time.</p>

      <div className="pt-versions">
        {quick && (
          <div className="pt-vcard quick">
            <div className="pt-vcard-title"><CheckCircle2 size={16} /> {quick.short_name}</div>
            <h4>{quick.total_questions} questions, ~{quick.est_minutes} min</h4>
            <div className="pt-vcard-desc">{quick.description}</div>
            <div className="pt-pills">
              <span className="pt-pill"><ListChecks size={12} /> {quick.total_questions} questions</span>
              <span className="pt-pill"><Clock size={12} /> ~{quick.est_minutes} min</span>
            </div>
            <button className="pt-start-btn quick" onClick={() => onStart(quick.key)}>
              Start {quick.short_name}
            </button>
          </div>
        )}

        {comp && (
          <div className="pt-vcard comp">
            <div className="pt-vcard-title"><CheckCircle2 size={16} /> {comp.short_name}</div>
            <h4>{comp.total_questions} questions, ~{comp.est_minutes} min</h4>
            <div className="pt-vcard-desc">{comp.description}</div>
            <div className="pt-pills">
              <span className="pt-pill"><ListChecks size={12} /> {comp.total_questions} questions</span>
              <span className="pt-pill"><Clock size={12} /> ~{comp.est_minutes} min</span>
            </div>
            <button className="pt-start-btn comp" onClick={() => onStart(comp.key)}>
              Start {comp.short_name}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

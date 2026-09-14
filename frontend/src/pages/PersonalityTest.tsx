import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Brain } from 'lucide-react';
import api from '../services/api';
import '../styles/personality.css';
import { ToastHost, useToasts } from '../components/codequest/ui';
import { VersionChooser } from './personality/VersionChooser';
import { AssessmentRunner } from './personality/AssessmentRunner';
import { ResultView } from './personality/ResultView';
import type { AssessmentResult } from './personality/types';

type Stage = 'choose' | 'run' | 'result';

export const PersonalityTestPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const formKey = searchParams.get('form');
  const [stage, setStage] = useState<Stage>('choose');
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const { toasts, push, dismiss } = useToasts();

  // On mount: if a result already exists, offer it; otherwise start at chooser.
  useEffect(() => {
    if (formKey) {
      setStage('run');
      return;
    }
    api
      .get<AssessmentResult>('/personality/my-result')
      .then(({ data }) => {
        if (data?.assessment_metadata?.form && data.assessment_metadata.form !== 'legacy') {
          setResult(data);
          setStage('result');
        }
      })
      .catch(() => { /* none yet */ });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setForm = (key: string | null) => {
    const next = new URLSearchParams(searchParams);
    if (key) next.set('form', key);
    else next.delete('form');
    setSearchParams(next, { replace: true });
  };

  const startForm = (key: string) => {
    setResult(null);
    setForm(key);
    setStage('run');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleDone = (r: AssessmentResult) => {
    setResult(r);
    setForm(null);
    setStage('result');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    push('Assessment scored — profile ready.', 'success');
  };

  const retake = () => {
    setResult(null);
    setForm(null);
    setStage('choose');
  };

  return (
    <div className="pt">
      <div className="pt-hero">
        <span className="pt-hero-badge"><Brain size={22} /></span>
        <div>
          <h1>The Big Five</h1>
          <p>Analyze your personality across the OCEAN framework.</p>
        </div>
      </div>

      {stage === 'choose' && <VersionChooser onStart={startForm} />}

      {stage === 'run' && formKey && (
        <AssessmentRunner
          formKey={formKey}
          onDone={handleDone}
          onExit={retake}
          notify={push}
        />
      )}

      {stage === 'result' && result && <ResultView result={result} onRetake={retake} />}

      <ToastHost toasts={toasts} onDismiss={dismiss} />
    </div>
  );
};

export default PersonalityTestPage;

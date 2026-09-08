/** Verdict banner plus per-test breakdown, shown under the editor. */
import React from 'react';
import { VERDICT_LABEL } from '../../pages/codequest/types';
import type { RunResult, SubmitResult } from '../../pages/codequest/types';

type Props = {
  runResult: RunResult | null;
  submitResult: SubmitResult | null;
};

export const JudgeResults: React.FC<Props> = ({ runResult, submitResult }) => {
  const active = submitResult ?? runResult;
  if (!active) return null;

  const cases = active.results ?? [];

  let note = '';
  if (submitResult) {
    note = `${submitResult.passed}/${submitResult.total} tests · ${submitResult.runtime_ms} ms`;
    if (submitResult.points_awarded > 0) note += ` · +${submitResult.points_awarded} pts`;
  } else if (runResult?.mode === 'samples') {
    note = `${runResult.passed}/${runResult.total} samples · ${runResult.runtime_ms} ms`;
  } else if (runResult) {
    note = `${runResult.runtime_ms} ms`;
  }

  return (
    <div className="cq-results">
      <div className={`cq-verdict ${active.verdict}`}>
        {VERDICT_LABEL[active.verdict]}
        {submitResult?.first_solve && ' · First solve!'}
        <span className="cq-verdict-note">{note}</span>
      </div>

      {active.error && (
        <div className="cq-case">
          <div className="cq-case-body" style={{ paddingTop: '0.6rem' }}>
            <div className="cq-case-block">
              <div className="cq-case-key">Error</div>
              <pre>{active.error}</pre>
            </div>
          </div>
        </div>
      )}

      {runResult?.mode === 'custom' && !submitResult && (
        <div className="cq-case">
          <div className="cq-case-body" style={{ paddingTop: '0.6rem' }}>
            <div className="cq-case-block">
              <div className="cq-case-key">Your output</div>
              <pre>{runResult.stdout || '(no output)'}</pre>
            </div>
            {runResult.stderr && (
              <div className="cq-case-block">
                <div className="cq-case-key">Stderr</div>
                <pre>{runResult.stderr}</pre>
              </div>
            )}
          </div>
        </div>
      )}

      {cases.map((testCase) => (
        <div className="cq-case" key={testCase.index}>
          <div className="cq-case-head">
            <span>
              {testCase.is_sample ? 'Sample' : 'Hidden'} test {testCase.index}
            </span>
            <span style={{ color: '#6f7d9f', fontSize: '0.72rem' }}>{testCase.runtime_ms} ms</span>
            <span className={`cq-case-verdict ${testCase.verdict}`}>
              {testCase.verdict === 'accepted' ? 'Passed' : VERDICT_LABEL[testCase.verdict]}
            </span>
          </div>

          {(testCase.input != null || testCase.expected != null || testCase.stderr) && (
            <div className="cq-case-body">
              {testCase.input != null && (
                <div className="cq-case-block">
                  <div className="cq-case-key">Input</div>
                  <pre>{testCase.input}</pre>
                </div>
              )}
              {testCase.expected != null && (
                <div className="cq-case-block">
                  <div className="cq-case-key">Expected</div>
                  <pre>{testCase.expected || '(empty)'}</pre>
                </div>
              )}
              {testCase.got != null && (
                <div className="cq-case-block">
                  <div className="cq-case-key">Your output</div>
                  <pre>{testCase.got || '(empty)'}</pre>
                </div>
              )}
              {testCase.stderr && (
                <div className="cq-case-block">
                  <div className="cq-case-key">Stderr</div>
                  <pre>{testCase.stderr}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      ))}

      {submitResult && submitResult.verdict !== 'accepted' && (
        <div className="cq-hidden-note">
          Inputs for hidden tests stay hidden — use Run with custom input to probe your logic.
        </div>
      )}
    </div>
  );
};

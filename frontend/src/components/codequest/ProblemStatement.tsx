/** The read-only left panel of the solve workspace. */
import React from 'react';
import { Lightbulb, Sparkles } from 'lucide-react';
import { Chip, InlineMarkdown, Prose } from './ui';
import type { ProblemDetail } from '../../pages/codequest/types';

type Props = {
  problem: ProblemDetail;
  hints: string[];
  hintCount: number;
  revealing: boolean;
  onRevealHint: () => void;
};

export const ProblemStatement: React.FC<Props> = ({
  problem,
  hints,
  hintCount,
  revealing,
  onRevealHint,
}) => (
  <div className="cq-card">
    <div className="cq-card-head" style={{ marginBottom: '0.5rem' }}>
      <h3 className="cq-card-title">Problem Description</h3>
      {problem.patterns.length > 0 && (
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Sparkles size={13} color="#f0921f" />
          <Chip tone="accent">{problem.patterns[0]}</Chip>
        </span>
      )}
    </div>

    <Prose text={problem.description} />

    {problem.notes.length > 0 && (
      <div className="cq-prose" style={{ marginTop: '0.6rem' }}>
        {problem.notes.map((note, index) => (
          <p key={index}>
            <InlineMarkdown text={note} />
          </p>
        ))}
      </div>
    )}

    {problem.pattern_note && (
      <>
        <div className="cq-section-label">
          <Sparkles size={12} /> Learn the pattern
        </div>
        <div className="cq-prose">
          <InlineMarkdown text={problem.pattern_note} />
        </div>
      </>
    )}

    <div className="cq-section-label">Input format</div>
    <ul className="cq-bullets">
      {problem.input_format.map((line, index) => (
        <li key={index}>
          <InlineMarkdown text={line} />
        </li>
      ))}
    </ul>

    <div className="cq-section-label">Output format</div>
    <ul className="cq-bullets">
      {problem.output_format.map((line, index) => (
        <li key={index}>
          <InlineMarkdown text={line} />
        </li>
      ))}
    </ul>

    {problem.examples.map((example, index) => (
      <React.Fragment key={index}>
        <div className="cq-section-label">Example {index + 1}</div>
        <div className="cq-example">
          <div className="cq-example-part">
            <div className="cq-example-key">Input</div>
            <pre>{example.input}</pre>
          </div>
          <div className="cq-example-part">
            <div className="cq-example-key">Output</div>
            <pre>{example.output || '(empty line)'}</pre>
          </div>
          {example.explanation && (
            <div className="cq-example-part">
              <div className="cq-example-key">Explanation</div>
              <div className="cq-example-note">
                <InlineMarkdown text={example.explanation} />
              </div>
            </div>
          )}
        </div>
      </React.Fragment>
    ))}

    <div className="cq-section-label">Constraints</div>
    {problem.constraints.map((constraint, index) => (
      <div className="cq-constraint" key={index}>
        {constraint}
      </div>
    ))}

    <div className="cq-section-label">
      <Lightbulb size={12} /> Need a hint?
    </div>
    <div className="cq-hintbox">
      <div className="cq-hint-meta">
        {hintCount} hint{hintCount === 1 ? '' : 's'} available —{' '}
        <span className="cq-hint-count">
          {hints.length === 0
            ? 'none revealed'
            : `${hints.length} revealed, ${hintCount - hints.length} left`}
        </span>
      </div>

      {hints.map((hint, index) => (
        <div className="cq-hint" key={index}>
          <span className="cq-hint-num">{index + 1}</span>
          <span>
            <InlineMarkdown text={hint} />
          </span>
        </div>
      ))}

      {hints.length < hintCount && (
        <button
          className="cq-btn cq-btn-outline cq-btn-sm"
          onClick={onRevealHint}
          disabled={revealing}
          style={{ marginTop: hints.length ? '0.6rem' : 0 }}
        >
          <Lightbulb size={13} />
          {revealing ? 'Revealing...' : `Show hint ${hints.length + 1} of ${hintCount}`}
        </button>
      )}
    </div>
  </div>
);

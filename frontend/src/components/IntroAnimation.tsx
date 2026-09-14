import React, { useEffect, useRef, useState } from 'react';
import { BrandMark } from './BrandLogo';
import '../styles/intro.css';

const STAGES = ['Explore', 'Learn', 'Prepare', 'Grow'];

/**
 * A ~6 second cinematic 3D-themed entry animation played once after login.
 *
 * Pure CSS 3D (perspective grid, depth-transformed logo assembly, orbiting
 * career tokens) so it stays lightweight — no WebGL/canvas dependency. Calls
 * ``onDone`` when the sequence finishes or when the user chooses to skip.
 */
export const IntroAnimation: React.FC<{ onDone: () => void; userName?: string }> = ({
  onDone,
  userName,
}) => {
  const [leaving, setLeaving] = useState(false);
  const [stage, setStage] = useState(0);
  const doneRef = useRef(false);

  const finish = () => {
    if (doneRef.current) return;
    doneRef.current = true;
    setLeaving(true);
    // Allow the fade-out to play before unmounting.
    window.setTimeout(onDone, 700);
  };

  useEffect(() => {
    // Cycle the journey words.
    const stageTimers = STAGES.map((_, i) =>
      window.setTimeout(() => setStage(i), 1600 + i * 900),
    );
    // Total run ~6.1s then auto-finish.
    const end = window.setTimeout(finish, 6100);
    // Let the user skip with a key/click too.
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === 'Escape' || e.key === ' ') finish();
    };
    window.addEventListener('keydown', onKey);
    return () => {
      stageTimers.forEach(clearTimeout);
      clearTimeout(end);
      window.removeEventListener('keydown', onKey);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className={`intro-root ${leaving ? 'is-leaving' : ''}`} role="dialog" aria-label="Welcome">
      {/* Depth backdrop */}
      <div className="intro-aurora" />
      <div className="intro-stage">
        {/* 3D perspective grid floor */}
        <div className="intro-grid-wrap">
          <div className="intro-grid" />
        </div>

        {/* Orbiting career tokens */}
        <div className="intro-orbit-scene">
          {['🎓', '💼', '🚀', '📈', '🧠', '⭐'].map((emoji, i) => (
            <div className="intro-orbit" style={{ ['--i' as any]: i }} key={emoji}>
              <span className="intro-token">{emoji}</span>
            </div>
          ))}
        </div>

        {/* Logo assembles in 3D */}
        <div className="intro-logo-3d">
          <div className="intro-logo-glow" />
          <BrandMark size={140} />
        </div>

        {/* Wordmark + tagline reveal */}
        <div className="intro-wordmark">
          <span className="intro-word">
            Carrerpulse <span className="intro-word-ai">Ai</span>
          </span>
          <span className="intro-tagline">A Brighter You, Ahead</span>
        </div>

        {/* Journey stepper */}
        <div className="intro-journey">
          {STAGES.map((s, i) => (
            <span key={s} className={`intro-step ${i <= stage ? 'on' : ''}`}>
              {s}
            </span>
          ))}
        </div>

        {userName && <div className="intro-greeting">Welcome, {userName.split(' ')[0]}</div>}
      </div>

      <button className="intro-skip" onClick={finish}>
        Skip intro →
      </button>
    </div>
  );
};

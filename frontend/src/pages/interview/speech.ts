/**
 * Thin wrappers around the browser Web Speech API used by the live interview:
 *  - speak():  text-to-speech for the interviewer's questions
 *  - createRecognizer(): incremental speech-to-text for the candidate's answers
 *
 * Everything degrades gracefully: if the browser has no support the callers
 * still work (the interviewer text is shown, and the candidate can rely on the
 * typed fallback). No answer is ever lost because we always keep the final
 * transcript string in React state.
 */

// ── Text to speech ──────────────────────────────────────────────

let _voices: SpeechSynthesisVoice[] = [];

function loadVoices(): SpeechSynthesisVoice[] {
  if (typeof window === 'undefined' || !window.speechSynthesis) return [];
  if (_voices.length === 0) _voices = window.speechSynthesis.getVoices();
  return _voices;
}

if (typeof window !== 'undefined' && window.speechSynthesis) {
  window.speechSynthesis.onvoiceschanged = () => {
    _voices = window.speechSynthesis.getVoices();
  };
}

export function ttsSupported(): boolean {
  return typeof window !== 'undefined' && 'speechSynthesis' in window;
}

/** Speak `text`; resolves when speech ends (or immediately if unsupported). */
export function speak(text: string): Promise<void> {
  return new Promise((resolve) => {
    if (!ttsSupported() || !text) {
      resolve();
      return;
    }
    try {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      const voices = loadVoices();
      // Prefer a natural English voice when available.
      const preferred =
        voices.find((v) => /en-IN/i.test(v.lang)) ||
        voices.find((v) => /en(-|_)?(GB|US)/i.test(v.lang)) ||
        voices.find((v) => v.lang.startsWith('en'));
      if (preferred) utter.voice = preferred;
      utter.rate = 1.0;
      utter.pitch = 1.0;
      utter.onend = () => resolve();
      utter.onerror = () => resolve();
      window.speechSynthesis.speak(utter);
    } catch {
      resolve();
    }
  });
}

export function stopSpeaking(): void {
  if (ttsSupported()) window.speechSynthesis.cancel();
}

// ── Speech to text ──────────────────────────────────────────────

export function sttSupported(): boolean {
  if (typeof window === 'undefined') return false;
  return 'SpeechRecognition' in window || 'webkitSpeechRecognition' in window;
}

export interface Recognizer {
  start: () => void;
  stop: () => void;
}

/**
 * Build a continuous recognizer. `onResult` receives the full transcript so far
 * (final + interim) so the UI can show live captions; `onEnd` fires when it stops.
 */
export function createRecognizer(
  onResult: (fullText: string, isFinal: boolean) => void,
  onEnd: () => void,
): Recognizer | null {
  if (!sttSupported()) return null;
  const Ctor: any =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognition = new Ctor();
  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = 'en-US';

  let finalText = '';
  let stopped = false;

  recognition.onresult = (event: any) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const chunk = event.results[i][0].transcript;
      if (event.results[i].isFinal) finalText += chunk + ' ';
      else interim += chunk;
    }
    onResult((finalText + interim).trim(), interim === '');
  };

  recognition.onerror = () => {
    /* swallow — 'no-speech'/'aborted' are common and non-fatal */
  };

  recognition.onend = () => {
    // Chrome auto-stops on silence; restart unless we intentionally stopped.
    if (!stopped) {
      try {
        recognition.start();
      } catch {
        onEnd();
      }
    } else {
      onEnd();
    }
  };

  return {
    start: () => {
      stopped = false;
      finalText = '';
      try {
        recognition.start();
      } catch {
        /* already started */
      }
    },
    stop: () => {
      stopped = true;
      try {
        recognition.stop();
      } catch {
        /* ignore */
      }
    },
  };
}

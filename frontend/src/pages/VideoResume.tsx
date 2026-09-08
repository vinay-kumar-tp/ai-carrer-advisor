import React, { useState } from 'react';
import { Video, Upload, Play, CheckCircle } from 'lucide-react';

export const VideoResumePage: React.FC = () => {
  const [recording, setRecording] = useState(false);
  const [recordedUrl, setRecordedUrl] = useState<string | null>(null);

  const handleSimulateRecord = () => {
    setRecording(true);
    setTimeout(() => {
      setRecording(false);
      setRecordedUrl('https://sample-videos.com/video321/mp4/480/big_buck_bunny_480p_1mb.mp4');
    }, 3000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h2>Video Resume Studio</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Record a 60-second video introduction pitch for recruiters and hiring managers.</p>
      </div>

      <div className="grid-2">
        {/* Recording Studio */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '350px', border: '2px dashed var(--border-color)', textAlign: 'center', padding: '2rem' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: 'rgba(236,72,153,0.15)', color: '#ec4899', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
            <Video size={32} />
          </div>
          <h3>Camera & WebRTC Pitch Studio</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '360px', margin: '0.5rem 0 1.5rem' }}>
            Ensure good lighting and speak clearly. State your background, key technical projects, and career aspirations.
          </p>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button onClick={handleSimulateRecord} className="btn btn-accent" disabled={recording}>
              {recording ? '🔴 Recording (3s demo)...' : 'Start Recording'}
            </button>
            <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
              <Upload size={16} /> Upload Video
              <input type="file" accept="video/*" style={{ display: 'none' }} />
            </label>
          </div>
        </div>

        {/* Video Preview & Transcripts */}
        <div className="glass-card">
          <h3 style={{ marginBottom: '1rem' }}>Pitch Preview & Auto-Transcript</h3>

          {recordedUrl ? (
            <div>
              <div style={{ width: '100%', height: '200px', background: '#000', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                <Play size={48} color="white" />
              </div>
              <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', padding: '0.75rem', borderRadius: '8px', color: '#34d399', fontSize: '0.85rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <CheckCircle size={16} /> Video pitch saved and encrypted in document vault.
              </div>
            </div>
          ) : (
            <div style={{ padding: '3rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No video recorded yet. Record or upload your pitch to generate automatic Speech-to-Text transcriptions.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

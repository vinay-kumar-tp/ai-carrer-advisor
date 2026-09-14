import React, { useEffect, useState } from 'react';
import api from '../services/api';
import '../styles/interview.css';
import { SetupStage } from './interview/SetupStage';
import { ReadinessModal, DeviceCheckModal } from './interview/PreflightModals';
import { LiveStage } from './interview/LiveStage';
import { FeedbackModal } from './interview/FeedbackModal';
import { ReportStage } from './interview/ReportStage';
import type {
  Stage,
  InterviewConfig,
  StartPayload,
  InterviewReport,
  HistoryItem,
} from './interview/types';

interface LiveState {
  sessionId: string;
  title: string;
  interviewerName: string;
  totalQuestions: number;
  questionNumber: number;
  question: string;
  isWarmup: boolean;
  thinking: boolean;
}

export const InterviewCoachPage: React.FC = () => {
  const [stage, setStage] = useState<Stage>('setup');
  const [config, setConfig] = useState<InterviewConfig | null>(null);
  const [pendingPayload, setPendingPayload] = useState<StartPayload | null>(null);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [live, setLive] = useState<LiveState | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [report, setReport] = useState<InterviewReport | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Load setup config once.
  useEffect(() => {
    api.get<InterviewConfig>('/interview/config')
      .then((res) => setConfig(res.data))
      .catch(() => setError('Could not load interview options. Is the backend running?'));
  }, []);

  const stopStream = () => {
    stream?.getTracks().forEach((t) => t.stop());
    setStream(null);
  };

  // Setup → open readiness modal (payload held until devices confirmed).
  const handleSetupStart = (payload: StartPayload) => {
    setError(null);
    setPendingPayload(payload);
    setStage('readiness');
  };

  // After device check → actually create the session, then go live.
  const beginSession = async (mediaStream: MediaStream | null) => {
    if (!pendingPayload) return;
    setStream(mediaStream);
    setStarting(true);
    try {
      const res = await api.post('/interview/start', pendingPayload);
      const d = res.data;
      setLive({
        sessionId: d.session_id,
        title: d.title,
        interviewerName: d.interviewer_name,
        totalQuestions: d.total_questions,
        questionNumber: d.question_number,
        question: d.question,
        isWarmup: d.is_warmup,
        thinking: false,
      });
      setStage('live');
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Could not start the interview.');
      setStage('setup');
      mediaStream?.getTracks().forEach((t) => t.stop());
      setStream(null);
    } finally {
      setStarting(false);
    }
  };

  // Candidate submitted an answer → post it, advance or finish.
  const handleAnswer = async (answerText: string) => {
    if (!live) return;
    setLive({ ...live, thinking: true });
    try {
      const res = await api.post(`/interview/${live.sessionId}/turn`, { answer_text: answerText });
      const d = res.data;
      if (d.completed) {
        setReport(d.report as InterviewReport);
        stopStream();
        setStage('feedback');
      } else {
        setLive({
          sessionId: live.sessionId,
          title: live.title,
          interviewerName: live.interviewerName,
          totalQuestions: d.total_questions,
          questionNumber: d.question_number,
          question: d.question,
          isWarmup: d.is_warmup,
          thinking: false,
        });
      }
    } catch (e: any) {
      // On failure, surface the report if the session actually finished; else recover.
      setError(e?.response?.data?.detail || 'Something went wrong. Try ending and reviewing your report.');
      setLive({ ...live, thinking: false });
    }
  };

  // End button during the interview → try to fetch a partial report.
  const handleEndInterview = async () => {
    stopStream();
    if (!live) {
      setStage('setup');
      return;
    }
    setStage('feedback');
  };

  const submitFeedback = async (data: any) => {
    if (report) {
      try {
        await api.post(`/interview/${report.session_id}/feedback`, data);
      } catch { /* non-blocking */ }
    }
    goToReport();
  };

  const goToReport = async () => {
    // Ensure we have a report (in case the user ended early).
    if (!report && live) {
      try {
        const res = await api.get(`/interview/${live.sessionId}/report`);
        setReport(res.data as InterviewReport);
      } catch {
        setStage('setup');
        return;
      }
    }
    setStage('report');
  };

  const resetToSetup = () => {
    stopStream();
    setLive(null);
    setReport(null);
    setPendingPayload(null);
    setError(null);
    setStage('setup');
  };

  const startSameInterview = () => {
    if (report && pendingPayload) {
      setReport(null);
      setLive(null);
      setStage('readiness');
    } else {
      resetToSetup();
    }
  };

  const openHistory = async () => {
    try {
      const res = await api.get<HistoryItem[]>('/interview/history');
      setHistory(res.data);
      setShowHistory(true);
    } catch { /* ignore */ }
  };

  const openHistoryReport = async (item: HistoryItem) => {
    if (!item.is_completed) return;
    try {
      const res = await api.get(`/interview/${item.id}/report`);
      setReport(res.data as InterviewReport);
      setShowHistory(false);
      setStage('report');
    } catch { /* ignore */ }
  };

  if (!config && stage === 'setup') {
    return (
      <div className="iv-wrap">
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          {error ? <p style={{ color: '#fca5a5' }}>{error}</p> : <p>Loading interview studio…</p>}
        </div>
      </div>
    );
  }

  return (
    <>
      {stage === 'setup' && config && (
        <SetupStage
          config={config}
          starting={starting}
          error={error}
          onStart={handleSetupStart}
          onViewAttempts={openHistory}
        />
      )}

      {stage === 'readiness' && (
        <>
          {/* keep setup visible behind the modal */}
          {config && (
            <SetupStage config={config} starting={starting} error={null} onStart={() => {}} onViewAttempts={() => {}} />
          )}
          <ReadinessModal onClose={resetToSetup} onContinue={() => setStage('device-check')} />
        </>
      )}

      {stage === 'device-check' && (
        <>
          {config && (
            <SetupStage config={config} starting={starting} error={null} onStart={() => {}} onViewAttempts={() => {}} />
          )}
          <DeviceCheckModal onCancel={resetToSetup} onStart={beginSession} />
        </>
      )}

      {stage === 'live' && live && (
        <LiveStage
          title={live.title}
          interviewerName={live.interviewerName}
          questionNumber={live.questionNumber}
          totalQuestions={live.totalQuestions}
          question={live.question}
          isWarmup={live.isWarmup}
          thinking={live.thinking}
          stream={stream}
          onSubmit={handleAnswer}
          onEnd={handleEndInterview}
        />
      )}

      {stage === 'feedback' && (
        <FeedbackModal onSkip={goToReport} onSubmit={submitFeedback} />
      )}

      {stage === 'report' && report && (
        <ReportStage report={report} onPracticeAgain={resetToSetup} onStartSame={startSameInterview} />
      )}

      {/* History drawer */}
      {showHistory && (
        <div className="iv-modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="iv-modal" onClick={(e) => e.stopPropagation()}>
            <h2 style={{ marginTop: 0 }}>My Interview Attempts</h2>
            {history.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No attempts yet. Start your first mock interview.</p>
            ) : (
              <div className="iv-mini-history">
                {history.map((h) => (
                  <div key={h.id} className="iv-history-row" onClick={() => openHistoryReport(h)}>
                    <div>
                      <strong>{h.title}</strong>
                      <div className="iv-hint">
                        {h.created_at ? new Date(h.created_at).toLocaleDateString() : ''} · {h.difficulty || 'mixed'}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      {h.is_completed ? (
                        <strong>{h.overall_score ?? '—'}/100</strong>
                      ) : (
                        <span className="iv-hint">Incomplete</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="iv-modal-actions">
              <button className="btn" onClick={() => setShowHistory(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

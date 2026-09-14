export type Stage =
  | 'setup'
  | 'readiness'
  | 'device-check'
  | 'live'
  | 'feedback'
  | 'report';

export type SourceTab = 'job' | 'skill' | 'resume';
export type JobSubSource = 'foundation' | 'standard' | 'jd';

export interface InterviewConfig {
  job_titles: string[];
  skills: string[];
  difficulty_levels: string[];
  question_mixes: string[];
  interviewer_name: string;
  total_questions: number;
  resumes: { id: string; name: string; source: string; is_primary: boolean }[];
}

export interface StartPayload {
  source: SourceTab;
  job_title?: string;
  job_description?: string;
  skill?: string;
  resume_id?: string;
  difficulty: string;
  question_mix: string;
}

export interface Dimension {
  [key: string]: number;
}

export interface ReportBreakdown {
  response_quality: { score: number; dimensions: Dimension };
  behavioural_competency: { score: number; dimensions: Dimension };
  speech_quality: { score: number; dimensions: Dimension; meta?: any };
}

export interface ReportQuestion {
  index: number;
  question: string;
  answer: string;
  score: number;
  is_warmup: boolean;
  evidence: string;
}

export interface Priority {
  topic: string;
  summary: string;
  what_to_study: string[];
  practice_drill: string;
  evidence_q?: number;
}

export interface AreaForImprovement {
  topic: string;
  detail: string;
  evidence_q?: number;
}

export interface InterviewReport {
  session_id: string;
  title: string;
  context_label: string;
  source?: string;
  difficulty?: string;
  created_at?: string;
  duration_min?: number;
  questions_spoken?: number;
  questions_reviewed?: number;
  overall_score: number;
  band: string;
  recruiter_perspective: string;
  breakdown: ReportBreakdown;
  strengths: string[];
  areas_for_improvement: AreaForImprovement[];
  priorities: Priority[];
  questions: ReportQuestion[];
}

export interface HistoryItem {
  id: string;
  title: string;
  context_label: string;
  difficulty?: string;
  overall_score?: number;
  band?: string;
  is_completed: boolean;
  created_at?: string;
}

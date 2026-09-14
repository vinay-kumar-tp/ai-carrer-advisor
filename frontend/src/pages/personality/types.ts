export interface FormMeta {
  key: string;
  name: string;
  short_name: string;
  description: string;
  est_minutes: number;
  total_questions: number;
}

export interface ScaleOption {
  value: number;
  label: string;
}

export interface FormQuestion {
  index: number;
  text: string;
}

export interface FormQuestions {
  form: FormMeta;
  prompt_prefix: string;
  scale: ScaleOption[];
  questions: FormQuestion[];
}

export interface TraitScore {
  label: string;
  raw_score: number;
  min_score: number;
  max_score: number;
  percentage: number;
  level: 'Low' | 'Moderate' | 'High';
}

export interface Compliance {
  status: 'Passed' | 'Flagged';
  longest_uniform_run?: number;
  neutral_responses?: number;
  neutral_ratio?: number;
  notes?: string;
}

export interface AssessmentResult {
  assessment_metadata: {
    form: string;
    total_questions: number;
    completed_questions: number;
    compliance_status: string;
    completion_time_seconds: number | null;
  };
  scores: Record<string, TraitScore>;
  workplace_behavioral_insights: {
    key_strengths?: string[];
    potential_challenges?: string[];
    team_collaboration_style?: string;
  };
  compliance: Compliance;
  completed_at: string | null;
}

export const TRAIT_ORDER = ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism'];

export const TRAIT_TINT: Record<string, string> = {
  openness: '#8b5cf6',
  conscientiousness: '#3b82f6',
  extraversion: '#f59e0b',
  agreeableness: '#10b981',
  neuroticism: '#ef4444',
};

export const LEVEL_COLOR: Record<string, string> = {
  Low: '#94a3b8',
  Moderate: '#60a5fa',
  High: '#34d399',
};

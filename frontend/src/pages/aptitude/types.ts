export type SectionKey = 'quant' | 'logical' | 'verbal' | 'technical';

export interface SubtopicMeta {
  name: string;
  question_count: number;
}

export interface TopicCard {
  slug: string;
  name: string;
  icon: string;
  blurb: string;
  section: SectionKey;
  section_label: string;
  question_count: number;
  subtopics: SubtopicMeta[];
  solved_count: number;
}

export interface CatalogSection {
  key: SectionKey;
  label: string;
  topics: TopicCard[];
}

export interface Catalog {
  sections: CatalogSection[];
  section_labels: Record<string, string>;
  total_questions: number;
  total_topics: number;
}

export interface PracticeQuestion {
  id: string;
  slug?: string;
  section: SectionKey;
  topic: string;
  subtopic?: string;
  difficulty: string;
  points: number;
  question_text: string;
  options: string[];
  solved: boolean;
}

export interface CheckResult {
  question_id: string;
  correct: boolean;
  correct_index: number;
  explanation?: string;
  points_earned: number;
  first_attempt: boolean;
}

export interface SectionProgress {
  key: SectionKey;
  label: string;
  total_questions: number;
  total_topics: number;
  attempted: number;
  accuracy: number;
  coverage: number;
  topics_touched: number;
  enough_evidence: boolean;
  score: number | null;
}

export interface ProgressData {
  overall_score: number | null;
  total_solved: number;
  total_questions: number;
  assessments_taken: number;
  sections: SectionProgress[];
}

export interface LeaderRow {
  rank: number;
  user_id: string;
  full_name: string;
  total_xp: number;
  level: number;
  quizzes_passed: number;
}

export const SECTION_ORDER: SectionKey[] = ['quant', 'logical', 'verbal', 'technical'];

export const SECTION_TINT: Record<SectionKey, string> = {
  quant: '#3b82f6',
  logical: '#f59e0b',
  verbal: '#10b981',
  technical: '#a855f7',
};

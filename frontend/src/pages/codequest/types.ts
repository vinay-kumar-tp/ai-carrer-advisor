/** Mirrors the /api/codequest responses. */

export type Difficulty = 'easy' | 'medium' | 'hard';
export type ProblemStatus = 'unsolved' | 'attempted' | 'solved';
export type Language = 'python' | 'javascript' | 'cpp' | 'java';

export type Verdict =
  | 'accepted'
  | 'wrong_answer'
  | 'runtime_error'
  | 'time_limit'
  | 'compile_error';

export type LanguageOption = { key: Language; label: string };

export type Meta = {
  total_problems: number;
  languages: LanguageOption[];
  difficulties: Difficulty[];
};

export type FacetValue = { name: string; count: number };

export type Facets = {
  topics: FacetValue[];
  patterns: FacetValue[];
  companies: FacetValue[];
  sheets: FacetValue[];
};

export type ProblemListItem = {
  slug: string;
  title: string;
  difficulty: Difficulty;
  topics: string[];
  patterns: string[];
  companies: string[];
  sheets: string[];
  points: number;
  status: ProblemStatus;
  acceptance: number | null;
};

export type ProblemListResponse = {
  items: ProblemListItem[];
  total: number;
  page: number;
  page_size: number;
  showing_from: number;
  showing_to: number;
};

export type Stats = {
  total_problems: number;
  solved: number;
  attempted: number;
  points: number;
  streak_days: number;
  by_difficulty: Record<string, { total: number; solved: number }>;
};

export type Example = { input: string; output: string; explanation?: string };

export type ProblemDetail = {
  slug: string;
  title: string;
  difficulty: Difficulty;
  points: number;
  time_limit_ms: number;
  description: string;
  notes: string[];
  input_format: string[];
  output_format: string[];
  constraints: string[];
  examples: Example[];
  topics: string[];
  patterns: string[];
  companies: string[];
  sheets: string[];
  languages: Language[];
  starter_code: Record<string, string>;
  hint_count: number;
  revealed_hints: string[];
  pattern_note: string;
  status: ProblemStatus;
  attempts: number;
  best_score: number;
  last_language: Language | null;
  draft: string | null;
  acceptance: number | null;
  position: number | null;
  total_in_filter: number | null;
  prev_slug: string | null;
  next_slug: string | null;
  related: ProblemListItem[];
};

export type CaseResult = {
  index: number;
  is_sample: boolean;
  verdict: Verdict;
  runtime_ms: number;
  input?: string | null;
  expected?: string | null;
  got?: string | null;
  stderr?: string | null;
};

export type RunResult = {
  mode: 'samples' | 'custom';
  verdict: Verdict;
  passed: number;
  total: number;
  runtime_ms: number;
  results: CaseResult[];
  stdout?: string | null;
  stderr?: string | null;
  error?: string | null;
};

export type SubmitResult = {
  submission_id: string;
  verdict: Verdict;
  passed: number;
  total: number;
  runtime_ms: number;
  score: number;
  points_awarded: number;
  first_solve: boolean;
  total_points: number;
  solved_count: number;
  streak_days: number;
  results: CaseResult[];
  error?: string | null;
};

export type SubmissionItem = {
  id: string;
  language: string;
  verdict: Verdict;
  passed: number;
  total: number;
  score: number;
  runtime_ms: number | null;
  points_awarded: number;
  created_at: string | null;
  /** On /progress this field carries the problem title instead of source code. */
  code?: string | null;
};

export type Progress = {
  total_problems: number;
  solved: number;
  attempted: number;
  points: number;
  level: number;
  streak_days: number;
  by_difficulty: Record<string, { total: number; solved: number }>;
  by_topic: { topic: string; total: number; solved: number }[];
  recent: SubmissionItem[];
};

export type LeaderboardRow = {
  rank: number;
  user_id: string;
  full_name: string;
  total_xp: number;
  level: number;
  problems_solved: number;
  streak_days: number;
};

export type Filters = {
  q: string;
  difficulty: 'all' | Difficulty;
  status: 'all' | 'solved' | 'unsolved';
  topic: string;
  pattern: string;
  company: string;
  sheet: string;
};

export const EMPTY_FILTERS: Filters = {
  q: '',
  difficulty: 'all',
  status: 'all',
  topic: '',
  pattern: '',
  company: '',
  sheet: '',
};

/** Only the keys the API accepts, with blanks stripped. */
export const filtersToParams = (filters: Filters): Record<string, string> => {
  const params: Record<string, string> = {};
  if (filters.q.trim()) params.q = filters.q.trim();
  if (filters.difficulty !== 'all') params.difficulty = filters.difficulty;
  if (filters.status !== 'all') params.status = filters.status;
  if (filters.topic) params.topic = filters.topic;
  if (filters.pattern) params.pattern = filters.pattern;
  if (filters.company) params.company = filters.company;
  if (filters.sheet) params.sheet = filters.sheet;
  return params;
};

export const VERDICT_LABEL: Record<Verdict, string> = {
  accepted: 'Accepted',
  wrong_answer: 'Wrong Answer',
  runtime_error: 'Runtime Error',
  time_limit: 'Time Limit Exceeded',
  compile_error: 'Compilation Error',
};

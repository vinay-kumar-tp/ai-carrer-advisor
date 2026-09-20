/** Mirrors the payloads returned by /api/position-ai/*. */

export type JdOption = {
  id: string;
  title: string;
  company: string;
  location: string;
  required_skills_count: number;
  required_skills: string[];
};

export type MissingSkill = {
  skill: string;
  jd_count: number;
  total_jds: number;
  top_jd_title: string;
};

export type GapScopeJd = {
  id: string;
  title: string;
  company: string;
  location: string;
  source: 'job' | 'text';
  sample_skills: string[];
  extra_count: number;
};

export type Analysis = {
  id: string | null;
  matchPercentage: number;
  matchedSkills: string[];
  missingSkills: MissingSkill[];
  jdTitle: string;
  profileSkillCount: number;
  selectedJdCount: number;
  scope: GapScopeJd[];
};

export type HistoryItem = {
  id: string;
  analyzed_at: string;
  jd_titles: string[];
  jd_snapshots: { job_id: string | null; title: string; company: string; required_skills: string[] }[];
  missing_skills: MissingSkill[];
  profile_skill_count: number;
  match_percentage: number;
};

export type HistoryResponse = {
  items: HistoryItem[];
  latest_missing_skills: string[];
};

export type SkillsResponse = {
  skills: string[];
  total: number;
};

/** "19 Sept 2026, 08:56 pm" — matches the History table in the design. */
export const formatAnalyzedAt = (iso: string): string => {
  if (!iso) return '';
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  const day = date.getDate();
  const month = date.toLocaleString('en-GB', { month: 'short' });
  const year = date.getFullYear();
  let hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const suffix = hours >= 12 ? 'pm' : 'am';
  hours = hours % 12 || 12;
  return `${day} ${month} ${year}, ${String(hours).padStart(2, '0')}:${minutes} ${suffix}`;
};

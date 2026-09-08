/** Mirrors the aggregate returned by GET /api/profile. */

export type PairRow = { label: string; value: string };
export type LinkRow = { label: string; url: string };

export type Semester = {
  semester: string;
  cgpa: number | null;
  ongoing_backlogs: number | null;
  total_backlogs: number | null;
  marksheet_doc_id?: string | null;
};

export type BasicInfo = {
  full_name: string;
  headline: string;
  enrollment_id: string;
  location: string;
  experience_level: string;
  avatar_url: string;
};

export type ContactInfo = { email: string; phone: string };

export type PersonalInfo = {
  gender: string;
  country: string;
  state: string;
  city: string;
  date_of_birth: string;
};

export type SocialInfo = {
  github_url: string;
  linkedin_url: string;
  dribbble_url: string;
  behance_url: string;
  portfolio_url: string;
  other_links: LinkRow[];
};

export type ProgramInfo = {
  program_name: string;
  program_year: string;
  institution_rating: string;
  program_extra: PairRow[];
};

export type MentorshipInfo = { is_mentee: boolean; mentor_name: string; mentorship_notes: string };

export type TrainingRow = { name: string; status: string; score: string; notes: string };

export type AcademicSummary = {
  class_10_percentage: number | null;
  class_10_board: string;
  class_12_percentage: number | null;
  class_12_board: string;
};

export type JobPreferences = {
  open_for: string[];
  job_roles: string[];
  available_for_hire: boolean;
  willing_to_relocate: boolean;
  preferred_locations: string[];
  industry: string;
  expected_ctc: number | null;
  ctc_period: string;
};

export type SkillRow = { skill_id: string; name: string; proficiency: number; category: string };

export type EducationRow = {
  id: string;
  institute: string;
  degree: string;
  specialization: string;
  start_year: string;
  end_year: string;
  cgpa: number | null;
  cgpa_scale: number;
  percentage: number | null;
  is_current: boolean;
  ongoing_backlogs: number;
  total_backlogs: number;
  semesters: Semester[];
  display_order: number;
};

export type WorkRow = {
  id: string;
  company: string;
  role: string;
  employment_type: string;
  location: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  highlights: string[];
  display_order: number;
};

export type PositionRow = {
  id: string;
  title: string;
  event_name: string;
  department: string;
  organization: string;
  start_date: string;
  end_date: string;
  highlights: string[];
  display_order: number;
};

export type ProjectRow = {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  tech_stack: string[];
  highlights: string[];
  start_date: string;
  end_date: string;
  is_ongoing: boolean;
  project_url: string;
  repo_url: string;
  display_order: number;
};

export type AwardRow = {
  id: string;
  title: string;
  issued_by: string;
  issue_date: string;
  achievement_type: string;
  description: string;
  award_url: string;
  certificate_doc_id: string | null;
  display_order: number;
};

export type CertificationRow = {
  id: string;
  name: string;
  issuer: string;
  course_duration: string;
  validity: string;
  cert_type: string;
  specialization: string;
  courses: string;
  pre_assessment_score: string;
  marks_obtained: string;
  points_earned: string;
  conclusion: string;
  credential_url: string;
  certificate_doc_id: string | null;
  display_order: number;
};

export type BenchmarkRow = {
  id: string | null;
  stage: string;
  provider: string;
  analytical_score: number | null;
  logical_score: number | null;
  verbal_score: number | null;
  quantitative_score: number | null;
  total_score: number | null;
  taken_on: string;
};

export type CompletionItem = {
  key: string;
  title: string;
  weight: number;
  complete: boolean;
  missing_fields: string[];
  action_label: string;
};

export type Completion = {
  percentage: number;
  items: CompletionItem[];
  next_suggestions: CompletionItem[];
};

export type ProfileAggregate = {
  user_id: string;
  email: string;
  full_name: string;
  role: string;
  basic: BasicInfo;
  contact: ContactInfo;
  personal: PersonalInfo;
  social: SocialInfo;
  about_me: string;
  additional_info: PairRow[];
  program: ProgramInfo;
  mentorship: MentorshipInfo;
  training: TrainingRow[];
  academic_summary: AcademicSummary;
  job_preferences: JobPreferences;
  skills: SkillRow[];
  educations: EducationRow[];
  work_experiences: WorkRow[];
  positions: PositionRow[];
  projects: ProjectRow[];
  awards: AwardRow[];
  certifications: CertificationRow[];
  benchmarks: Record<'baseline' | 'midline' | 'endline', BenchmarkRow>;
  resume_count: number;
  completion: Completion;
};

/* ── Resume library ─────────────────────────────────────── */

export type ResumeRow = {
  id: string;
  name: string;
  source: string;
  template: string;
  ats_score: number | null;
  status: string;
  is_primary: boolean;
  target_job_id: string | null;
  document_id: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type ResumeLibrary = { resumes: ResumeRow[]; total: number; templates: string[] };

export type AtsReport = {
  ats_score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  suggestions: string[];
  word_count: number;
};

/* ── Scorecard ──────────────────────────────────────────── */

export type AssessmentRow = {
  name: string;
  type: string;
  attempted: boolean;
  attempts: number;
  score: number;
  max_score: number;
  percentage: number | null;
};

export type MockInterviewRow = {
  id: string;
  mode: string;
  job_context: string;
  overall_score: number | null;
  scores: Record<string, number>;
  is_completed: boolean;
  created_at: string | null;
};

export type ScorecardEntryRow = {
  id: string;
  category: string;
  title: string;
  score: number;
  max_score: number | null;
  scored_on: string;
  notes: string;
};

export type Scorecard = {
  assessments: AssessmentRow[];
  stats: {
    total_available: number;
    total_attempted: number;
    attempt_rate: number;
    avg_score: number;
    highest_score: number;
    lowest_score: number;
  };
  mock_interviews: MockInterviewRow[];
  personality: Record<string, number> | null;
  other_scores: ScorecardEntryRow[];
  custom_event_scores: ScorecardEntryRow[];
};

/* ── Documents ──────────────────────────────────────────── */

export type DocumentRow = {
  id: string;
  filename: string;
  label: string;
  doc_type: string;
  file_size: number;
  is_public: boolean;
  created_at: string | null;
  download_url: string;
};

export type ProfileDocuments = {
  resumes: DocumentRow[];
  marksheets: DocumentRow[];
  certificates: DocumentRow[];
  others: DocumentRow[];
  resume_library: ResumeRow[];
  primary_resume: ResumeRow | null;
  total: number;
};

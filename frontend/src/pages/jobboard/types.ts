export type FacetValue = { name: string; count: number };

export type JobCard = {
  id: string;
  slug?: string;
  title: string;
  company: string;
  description: string;
  location: string;
  remote: boolean;
  salary_range?: string | null;
  required_skills: string[];
  experience_level: string;
  job_type: string;
  posted_at: string;
  source_portal: string;
  company_logo: string;
  company_tagline: string;
  industry: string;
  employment_mode: string;
  openings: number;
  application_deadline: string;
  ctc_min?: number | null;
  ctc_max?: number | null;
  stipend_min?: number | null;
  stipend_max?: number | null;
  experience_min_years: number;
  experience_max_years?: number | null;
  applied?: boolean;
};

export type EligibilityCriterion = {
  key: string;
  type: string;
  label: string;
  met: boolean;
  requirement: string;
  candidate_value: string;
  note?: string;
};

export type Eligibility = {
  eligible: boolean;
  met_count: number;
  total: number;
  criteria: EligibilityCriterion[];
  has_criteria: boolean;
};

export type Prefill = {
  full_name: string;
  email: string;
  phone: string;
  headline: string;
  location: string;
  gender: string;
  date_of_birth: string;
  linkedin_url: string;
  github_url: string;
  portfolio_url: string;
  current_institute: string;
  degree: string;
  specialization: string;
  graduation_year: string;
  cgpa?: number | null;
  total_experience_years: number;
  skills: string[];
  expected_ctc?: number | null;
  willing_to_relocate: boolean;
  preferred_locations: string[];
};

export type ApplyQuestion = {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'number' | 'select' | 'multiselect' | 'boolean' | 'url' | 'date';
  required?: boolean;
  options?: string[];
  placeholder?: string;
  help?: string;
};

export type JobDetail = JobCard & {
  about_company: string;
  responsibilities: string[];
  qualifications: string[];
  perks: string[];
  ctc_breakdown: { component: string; amount: string }[];
  eligibility_criteria: any[];
  apply_questions: ApplyQuestion[];
  eligibility: Eligibility;
  prefill: Prefill;
  applied: boolean;
  application_status?: string | null;
};

export type Facets = {
  job_types: FacetValue[];
  roles: FacetValue[];
  locations: FacetValue[];
  industries: FacetValue[];
  employers: FacetValue[];
  employment_modes: FacetValue[];
  portals: FacetValue[];
  total: number;
};

export type Filters = {
  keyword: string;
  job_type: string;
  role: string;
  location: string;
  industry: string;
  employer: string;
  employment_mode: string;
  source_portal: string;
  status: string;
  min_experience: string;
  max_experience: string;
  posted_in: string;
  min_ctc: string;
  max_ctc: string;
  min_stipend: string;
  max_stipend: string;
  sort: string;
};

export const EMPTY_FILTERS: Filters = {
  keyword: '',
  job_type: '',
  role: '',
  location: '',
  industry: '',
  employer: '',
  employment_mode: '',
  source_portal: '',
  status: '',
  min_experience: '',
  max_experience: '',
  posted_in: '',
  min_ctc: '',
  max_ctc: '',
  min_stipend: '',
  max_stipend: '',
  sort: 'recent',
};

export type AppNotification = {
  id: string;
  message: string;
  notification_type: string;
  read: boolean;
  created_at: string;
};

export type MyApplication = {
  id: string;
  job_id: string;
  status: string;
  applied_at: string;
  updated_at: string;
  answers: Record<string, any>;
  cover_letter?: string | null;
  job: JobCard | null;
};

export const formatCTC = (min?: number | null, max?: number | null): string => {
  if (min == null && max == null) return '';
  const toL = (v: number) => {
    if (v >= 10000000) return `${(v / 10000000).toFixed(v % 10000000 === 0 ? 0 : 1)} Cr`;
    if (v >= 100000) return `${(v / 100000).toFixed(v % 100000 === 0 ? 0 : 1)} LPA`;
    return `₹${v.toLocaleString('en-IN')}`;
  };
  if (min === 0 && max === 0) return 'Unpaid';
  if (min != null && max != null) return `₹${toL(min)} - ${toL(max)}`;
  return `₹${toL((min ?? max) as number)}`;
};

export const formatStipend = (min?: number | null, max?: number | null): string => {
  if (min == null && max == null) return '';
  const k = (v: number) => (v >= 1000 ? `${v / 1000}K` : `${v}`);
  if (min != null && max != null && min !== max) return `₹${k(min)} - ${k(max)}/mo`;
  return `₹${k((min ?? max) as number)}/mo`;
};

// Per-company brand colors so the mock logos look distinct and "real".
const BRAND_COLORS: Record<string, string> = {
  'Nexora Labs': '2563eb',
  'BrightWave Digital': '0ea5e9',
  'DataCraft Analytics': '7c3aed',
  'Cognita AI': '9333ea',
  'CloudPeak Systems': '0284c7',
  'WebSpring Tech': '16a34a',
  'PixelForge Studio': 'db2777',
  'ScriptBay Clients': '15803d',
  'LoopStack (Seed)': 'ea580c',
  'Testlyne Solutions': '059669',
  'CoreBank Technologies': '1d4ed8',
  'TechNova Systems': '4f46e5',
  'Flowbit': 'f59e0b',
  'Vantage Commerce': 'e11d48',
  'QuickCare Services': '0891b2',
  'SwiftLogix': 'c2410c',
  'ScaleOn': '2563eb',
  'Mobio Apps': '7c3aed',
  'Inclusiv Tech': 'db2777',
  'Altitude Cloud': '0369a1',
  'Metricly': '6366f1',
  'DocuWise': '334155',
  'Code For Good Foundation': '15803d',
  'Zenith (Series A)': '0d9488',
};

const hashColor = (name: string): string => {
  let h = 0;
  for (let i = 0; i < name.length; i += 1) h = (h * 31 + name.charCodeAt(i)) & 0xffffff;
  return h.toString(16).padStart(6, '0');
};

/** A clean initials-based brand mark (mock "real" logo) rendered as an SVG avatar. */
export const companyLogoUrl = (company: string): string => {
  const clean = (company || 'Company').replace(/\s*\(.*?\)\s*/g, '').trim() || company;
  const color = BRAND_COLORS[company] || hashColor(company || 'Company');
  const name = encodeURIComponent(clean);
  return `https://ui-avatars.com/api/?name=${name}&background=${color}&color=fff&bold=true&size=128&length=2&font-size=0.4`;
};

export const timeAgo = (iso: string): string => {
  const then = new Date(iso).getTime();
  const days = Math.floor((Date.now() - then) / 86400000);
  if (days <= 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 30) return `${days}d ago`;
  const months = Math.floor(days / 30);
  return `${months}mo ago`;
};

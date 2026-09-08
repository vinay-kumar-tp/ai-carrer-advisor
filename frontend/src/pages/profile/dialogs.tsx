/**
 * Edit dialogs for every card on the Profile tab.
 *
 * Each dialog keeps its own draft copy so cancelling never mutates the page,
 * and owns its own busy/error state so one failing save can't block the others.
 */
import React, { useState } from 'react';
import { Modal } from '../../components/profile/ui';
import {
  BulletEditor,
  CheckboxField,
  FieldsetTitle,
  FormGrid,
  LinkEditor,
  NumberField,
  PairEditor,
  SelectField,
  SemesterEditor,
  TagInput,
  TextAreaField,
  TextField,
  TrainingEditor,
} from '../../components/profile/forms';
import type {
  AcademicSummary,
  AwardRow,
  BasicInfo,
  BenchmarkRow,
  CertificationRow,
  ContactInfo,
  EducationRow,
  JobPreferences,
  MentorshipInfo,
  PairRow,
  PersonalInfo,
  PositionRow,
  ProgramInfo,
  ProjectRow,
  SocialInfo,
  TrainingRow,
  WorkRow,
} from './types';

export type SaveResult = { ok: boolean; message?: string };
export type SaveFn<T> = (value: T) => Promise<SaveResult>;

type DialogProps<T> = {
  initial: T;
  onClose: () => void;
  onSave: SaveFn<T>;
};

/** Shared submit plumbing: busy flag, error surface, close-on-success. */
const useSubmit = <T,>(draft: T, onSave: SaveFn<T>, onClose: () => void) => {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setBusy(true);
    setError(null);
    const result = await onSave(draft);
    if (result.ok) {
      onClose();
    } else {
      setError(result.message ?? 'Could not save. Please try again.');
      setBusy(false);
    }
  };

  return { busy, error, submit };
};

/* ── Option lists (generic, reusable for any student) ────── */

export const GENDERS = ['Male', 'Female', 'Non-binary', 'Prefer not to say'];
export const EXPERIENCE_LEVELS = ['Fresher', '0-1 years', '1-3 years', '3-5 years', '5+ years'];
export const EMPLOYMENT_TYPES = ['Internship', 'Full-time', 'Part-time', 'Freelance', 'Apprenticeship', 'Volunteer'];
export const DEGREES = [
  'BE/B.Tech', 'B.Sc', 'BCA', 'B.Com', 'BA', 'BBA',
  'ME/M.Tech', 'M.Sc', 'MCA', 'MBA', 'Diploma', 'PhD',
];
export const OPEN_FOR_OPTIONS = ['Full Time', 'Internship', 'Part Time', 'Contract', 'Freelance'];
export const ACHIEVEMENT_TYPES = ['Academic', 'Technical', 'Sports', 'Cultural', 'Leadership', 'Community', 'Other'];
export const INDUSTRIES = [
  'Engineering - Software', 'Engineering - Hardware', 'Data & Analytics', 'Artificial Intelligence',
  'Product Management', 'Design', 'Finance', 'Consulting', 'Healthcare', 'Education', 'Manufacturing', 'Other',
];
export const CONCLUSIONS = ['Completed', 'In Progress', 'Not Started'];
export const COMMON_ROLES = [
  'Software Engineer', 'Backend Developer', 'Frontend Developer', 'Full Stack Developer',
  'Data Analyst', 'Data Scientist', 'ML Engineer', 'DevOps Engineer', 'QA Engineer', 'Product Analyst',
];

/* ── Basic details ──────────────────────────────────────── */

export const BasicDialog: React.FC<DialogProps<BasicInfo>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<BasicInfo>({ ...initial });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<BasicInfo>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal title="Edit Basic Details" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid>
        <TextField label="Full name" value={draft.full_name} onChange={(v) => set({ full_name: v })} required />
        <TextField
          label="Student / Enrollment ID"
          value={draft.enrollment_id}
          onChange={(v) => set({ enrollment_id: v })}
          placeholder="e.g. STU2026001"
        />
        <TextField
          label="Professional headline"
          value={draft.headline}
          onChange={(v) => set({ headline: v })}
          placeholder="AI & Data Science Undergraduate | Full-Stack Developer"
          hint="Separate highlights with | — this is the first thing recruiters read."
          maxLength={500}
          span
        />
        <TextField label="Location" value={draft.location} onChange={(v) => set({ location: v })} placeholder="Bengaluru" />
        <SelectField
          label="Experience level"
          value={draft.experience_level}
          onChange={(v) => set({ experience_level: v })}
          options={EXPERIENCE_LEVELS}
        />
        <TextField
          label="Profile photo URL"
          type="url"
          value={draft.avatar_url}
          onChange={(v) => set({ avatar_url: v })}
          placeholder="https://..."
          hint="Paste a link to a square image."
          span
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Contact ────────────────────────────────────────────── */

export const ContactDialog: React.FC<DialogProps<ContactInfo>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<ContactInfo>({ ...initial });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);

  return (
    <Modal title="Edit Contact Details" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid cols={1}>
        <TextField
          label="Email"
          type="email"
          value={draft.email}
          onChange={(v) => setDraft((d) => ({ ...d, email: v }))}
          required
          hint="This is also your sign-in email."
        />
        <TextField
          label="Contact number"
          type="tel"
          value={draft.phone}
          onChange={(v) => setDraft((d) => ({ ...d, phone: v }))}
          placeholder="+91 90000 00000"
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Personal ───────────────────────────────────────────── */

export const PersonalDialog: React.FC<DialogProps<PersonalInfo>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<PersonalInfo>({ ...initial });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<PersonalInfo>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal title="Edit Personal Details" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid>
        <SelectField label="Gender" value={draft.gender} onChange={(v) => set({ gender: v })} options={GENDERS} />
        <TextField label="Date of birth" type="date" value={draft.date_of_birth} onChange={(v) => set({ date_of_birth: v })} />
        <TextField label="Country" value={draft.country} onChange={(v) => set({ country: v })} placeholder="India" />
        <TextField label="State" value={draft.state} onChange={(v) => set({ state: v })} placeholder="Karnataka" />
        <TextField label="City" value={draft.city} onChange={(v) => set({ city: v })} placeholder="Bengaluru" />
      </FormGrid>
    </Modal>
  );
};

/* ── Social links ───────────────────────────────────────── */

export const SocialDialog: React.FC<DialogProps<SocialInfo>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<SocialInfo>({ ...initial, other_links: [...(initial.other_links || [])] });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<SocialInfo>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal title="Edit Social Links" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid>
        <TextField label="GitHub" type="url" value={draft.github_url} onChange={(v) => set({ github_url: v })} placeholder="https://github.com/username" span />
        <TextField label="LinkedIn" type="url" value={draft.linkedin_url} onChange={(v) => set({ linkedin_url: v })} placeholder="https://linkedin.com/in/username" span />
        <TextField label="Dribbble" type="url" value={draft.dribbble_url} onChange={(v) => set({ dribbble_url: v })} placeholder="https://dribbble.com/username" span />
        <TextField label="Behance" type="url" value={draft.behance_url} onChange={(v) => set({ behance_url: v })} placeholder="https://behance.net/username" span />
        <TextField label="Portfolio" type="url" value={draft.portfolio_url} onChange={(v) => set({ portfolio_url: v })} placeholder="https://yoursite.dev" span />
        <LinkEditor label="Other links" rows={draft.other_links || []} onChange={(rows) => set({ other_links: rows })} />
      </FormGrid>
    </Modal>
  );
};

/* ── About me ───────────────────────────────────────────── */

export const AboutDialog: React.FC<DialogProps<string>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState(initial || '');
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);

  return (
    <Modal title="Edit About Me" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid cols={1}>
        <TextAreaField
          label="About me"
          value={draft}
          onChange={setDraft}
          rows={7}
          maxLength={5000}
          placeholder="Two or three sentences on what you build, what you're strong at, and what you're looking for next."
          hint={`${draft.length}/5000 characters`}
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Additional information ─────────────────────────────── */

export const AdditionalInfoDialog: React.FC<DialogProps<PairRow[]>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<PairRow[]>(initial?.length ? [...initial] : [{ label: '', value: '' }]);
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);

  return (
    <Modal title="Edit Additional Information" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid cols={1}>
        <PairEditor
          label="Custom details"
          rows={draft}
          onChange={setDraft}
          labelPlaceholder="e.g. Languages known"
          valuePlaceholder="e.g. English, Hindi, Kannada"
          addLabel="Add detail"
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Program details ────────────────────────────────────── */

export const ProgramDialog: React.FC<DialogProps<ProgramInfo>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<ProgramInfo>({ ...initial, program_extra: [...(initial.program_extra || [])] });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<ProgramInfo>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal title="Edit Program Details" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid>
        <TextField
          label="Program / scholarship name"
          value={draft.program_name}
          onChange={(v) => set({ program_name: v })}
          placeholder="e.g. Merit Scholarship Program"
          span
        />
        <TextField label="Academic / financial year" value={draft.program_year} onChange={(v) => set({ program_year: v })} placeholder="2026-27" />
        <TextField label="Institution rating" value={draft.institution_rating} onChange={(v) => set({ institution_rating: v })} placeholder="AAAA" />
        <PairEditor
          label="Additional program fields"
          rows={draft.program_extra || []}
          onChange={(rows) => set({ program_extra: rows })}
          labelPlaceholder="e.g. Cohort"
          valuePlaceholder="e.g. Batch 12"
          addLabel="Add program field"
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Mentorship ─────────────────────────────────────────── */

export const MentorshipDialog: React.FC<DialogProps<MentorshipInfo>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<MentorshipInfo>({ ...initial });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<MentorshipInfo>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal title="Edit Mentorship" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid cols={1}>
        <CheckboxField label="I am enrolled in a mentorship program" checked={draft.is_mentee} onChange={(v) => set({ is_mentee: v })} />
        <TextField label="Mentor name" value={draft.mentor_name} onChange={(v) => set({ mentor_name: v })} placeholder="Mentor's full name" />
        <TextAreaField
          label="Notes"
          value={draft.mentorship_notes}
          onChange={(v) => set({ mentorship_notes: v })}
          rows={3}
          placeholder="Focus areas, cadence, goals..."
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Training ───────────────────────────────────────────── */

export const TrainingDialog: React.FC<DialogProps<TrainingRow[]>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<TrainingRow[]>([...(initial || [])]);
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);

  return (
    <Modal title="Edit Training" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid cols={1}>
        <TrainingEditor rows={draft} onChange={setDraft} />
      </FormGrid>
    </Modal>
  );
};

/* ── School results ─────────────────────────────────────── */

export const AcademicSummaryDialog: React.FC<DialogProps<AcademicSummary>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<AcademicSummary>({ ...initial });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<AcademicSummary>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal title="Edit School Results" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid>
        <NumberField
          label="Class 10 percentage"
          value={draft.class_10_percentage}
          onChange={(v) => set({ class_10_percentage: v })}
          min={0}
          max={100}
          step={0.01}
          placeholder="79.40"
        />
        <TextField label="Class 10 board" value={draft.class_10_board} onChange={(v) => set({ class_10_board: v })} placeholder="CBSE" />
        <NumberField
          label="Class 12 percentage"
          value={draft.class_12_percentage}
          onChange={(v) => set({ class_12_percentage: v })}
          min={0}
          max={100}
          step={0.01}
          placeholder="96.33"
        />
        <TextField label="Class 12 board" value={draft.class_12_board} onChange={(v) => set({ class_12_board: v })} placeholder="State Board" />
      </FormGrid>
    </Modal>
  );
};

/* ── Job preferences ────────────────────────────────────── */

export const JobPreferencesDialog: React.FC<DialogProps<JobPreferences>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<JobPreferences>({
    ...initial,
    open_for: [...(initial.open_for || [])],
    job_roles: [...(initial.job_roles || [])],
    preferred_locations: [...(initial.preferred_locations || [])],
  });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<JobPreferences>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal title="Edit Job Preferences" onClose={onClose} onSubmit={submit} busy={busy} error={error} wide>
      <FormGrid>
        <TagInput
          label="Open for"
          values={draft.open_for}
          onChange={(v) => set({ open_for: v })}
          suggestions={OPEN_FOR_OPTIONS}
          placeholder="Full Time, Internship..."
        />
        <TagInput
          label="Job roles"
          values={draft.job_roles}
          onChange={(v) => set({ job_roles: v })}
          suggestions={COMMON_ROLES}
          placeholder="Backend Developer..."
        />
        <TagInput
          label="Preferred locations"
          values={draft.preferred_locations}
          onChange={(v) => set({ preferred_locations: v })}
          placeholder="Bengaluru, Pune, Remote..."
        />
        <SelectField label="Industry" value={draft.industry} onChange={(v) => set({ industry: v })} options={INDUSTRIES} />
        <NumberField
          label="Expected CTC"
          value={draft.expected_ctc}
          onChange={(v) => set({ expected_ctc: v })}
          min={0}
          step={10000}
          placeholder="1200000"
        />
        <SelectField
          label="CTC period"
          value={draft.ctc_period || 'Year'}
          onChange={(v) => set({ ctc_period: v })}
          options={['Year', 'Month']}
          allowBlank={false}
        />
        <CheckboxField label="Available for hire" checked={draft.available_for_hire} onChange={(v) => set({ available_for_hire: v })} />
        <CheckboxField label="Willing to relocate" checked={draft.willing_to_relocate} onChange={(v) => set({ willing_to_relocate: v })} />
      </FormGrid>
    </Modal>
  );
};

/* ── Skills ─────────────────────────────────────────────── */

export const SkillsDialog: React.FC<DialogProps<string[]> & { suggestions: string[] }> = ({
  initial,
  onClose,
  onSave,
  suggestions,
}) => {
  const [draft, setDraft] = useState<string[]>([...(initial || [])]);
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);

  return (
    <Modal title="Edit Skills" onClose={onClose} onSubmit={submit} busy={busy} error={error}>
      <FormGrid cols={1}>
        <TagInput
          label="Your skills"
          values={draft}
          onChange={setDraft}
          suggestions={suggestions}
          placeholder="Type a skill and press Enter"
          hint="Add at least 3 skills — recruiters filter on these."
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Education ──────────────────────────────────────────── */

export const emptyEducation = (): EducationRow => ({
  id: '',
  institute: '',
  degree: '',
  specialization: '',
  start_year: '',
  end_year: '',
  cgpa: null,
  cgpa_scale: 10,
  percentage: null,
  is_current: true,
  ongoing_backlogs: 0,
  total_backlogs: 0,
  semesters: [],
  display_order: 0,
});

export const EducationDialog: React.FC<
  DialogProps<EducationRow> & { marksheets?: { id: string; label: string }[] }
> = ({ initial, onClose, onSave, marksheets = [] }) => {
  const [draft, setDraft] = useState<EducationRow>({ ...initial, semesters: [...(initial.semesters || [])] });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<EducationRow>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal
      title={initial.id ? 'Edit Education' : 'Add Education'}
      onClose={onClose}
      onSubmit={submit}
      busy={busy}
      error={error}
      wide
    >
      <FormGrid>
        <TextField label="Institute" value={draft.institute} onChange={(v) => set({ institute: v })} required span />
        <SelectField label="Degree" value={draft.degree} onChange={(v) => set({ degree: v })} options={DEGREES} />
        <TextField
          label="Specialization"
          value={draft.specialization}
          onChange={(v) => set({ specialization: v })}
          placeholder="Artificial Intelligence and Data Science"
        />
        <TextField label="Start year" value={draft.start_year} onChange={(v) => set({ start_year: v })} placeholder="2023" />
        <TextField label="End year" value={draft.end_year} onChange={(v) => set({ end_year: v })} placeholder="2027" />
        <NumberField label="CGPA" value={draft.cgpa} onChange={(v) => set({ cgpa: v })} min={0} max={100} step={0.01} placeholder="8.75" />
        <NumberField label="CGPA scale" value={draft.cgpa_scale} onChange={(v) => set({ cgpa_scale: v ?? 10 })} min={1} max={100} step={0.5} />
        <NumberField
          label="Overall percentage"
          value={draft.percentage}
          onChange={(v) => set({ percentage: v })}
          min={0}
          max={100}
          step={0.01}
          placeholder="87.55"
        />
        <CheckboxField label="Currently studying here" checked={draft.is_current} onChange={(v) => set({ is_current: v })} />

        <FieldsetTitle>Backlogs</FieldsetTitle>
        <NumberField label="Ongoing backlogs" value={draft.ongoing_backlogs} onChange={(v) => set({ ongoing_backlogs: v ?? 0 })} min={0} />
        <NumberField label="Total backlogs" value={draft.total_backlogs} onChange={(v) => set({ total_backlogs: v ?? 0 })} min={0} />

        <FieldsetTitle>Semester wise performance</FieldsetTitle>
        <SemesterEditor rows={draft.semesters} onChange={(rows) => set({ semesters: rows })} marksheets={marksheets} />
      </FormGrid>
    </Modal>
  );
};

/* ── Work experience ────────────────────────────────────── */

export const emptyWork = (): WorkRow => ({
  id: '',
  company: '',
  role: '',
  employment_type: 'Internship',
  location: '',
  start_date: '',
  end_date: '',
  is_current: false,
  highlights: [],
  display_order: 0,
});

export const WorkDialog: React.FC<DialogProps<WorkRow>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<WorkRow>({ ...initial, highlights: [...(initial.highlights || [])] });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<WorkRow>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal
      title={initial.id ? 'Edit Work Experience' : 'Add Work Experience'}
      onClose={onClose}
      onSubmit={submit}
      busy={busy}
      error={error}
      wide
    >
      <FormGrid>
        <TextField label="Role / title" value={draft.role} onChange={(v) => set({ role: v })} required />
        <TextField label="Company" value={draft.company} onChange={(v) => set({ company: v })} required />
        <SelectField
          label="Employment type"
          value={draft.employment_type}
          onChange={(v) => set({ employment_type: v })}
          options={EMPLOYMENT_TYPES}
          allowBlank={false}
        />
        <TextField label="Location" value={draft.location} onChange={(v) => set({ location: v })} placeholder="Bengaluru / Remote" />
        <TextField label="Start date" type="month" value={draft.start_date} onChange={(v) => set({ start_date: v })} />
        <TextField label="End date" type="month" value={draft.end_date} onChange={(v) => set({ end_date: v })} hint="Leave blank if ongoing" />
        <CheckboxField label="I currently work here" checked={draft.is_current} onChange={(v) => set({ is_current: v })} span />
        <BulletEditor
          label="What you did"
          values={draft.highlights}
          onChange={(v) => set({ highlights: v })}
          placeholder="Built REST APIs serving 10k requests/day"
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Position of responsibility ─────────────────────────── */

export const emptyPosition = (): PositionRow => ({
  id: '',
  title: '',
  event_name: '',
  department: '',
  organization: '',
  start_date: '',
  end_date: '',
  highlights: [],
  display_order: 0,
});

export const PositionDialog: React.FC<DialogProps<PositionRow>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<PositionRow>({ ...initial, highlights: [...(initial.highlights || [])] });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<PositionRow>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal
      title={initial.id ? 'Edit Position of Responsibility' : 'Add Position of Responsibility'}
      onClose={onClose}
      onSubmit={submit}
      busy={busy}
      error={error}
      wide
    >
      <FormGrid>
        <TextField label="Position title" value={draft.title} onChange={(v) => set({ title: v })} required placeholder="Campaigning Coordinator" />
        <TextField label="Event / committee" value={draft.event_name} onChange={(v) => set({ event_name: v })} placeholder="Annual College Fest" />
        <TextField label="Department" value={draft.department} onChange={(v) => set({ department: v })} placeholder="Co-curricular Activities" />
        <TextField label="Organization" value={draft.organization} onChange={(v) => set({ organization: v })} placeholder="Institute name" />
        <TextField label="Start date" type="date" value={draft.start_date} onChange={(v) => set({ start_date: v })} />
        <TextField label="End date" type="date" value={draft.end_date} onChange={(v) => set({ end_date: v })} />
        <BulletEditor
          label="Responsibilities"
          values={draft.highlights}
          onChange={(v) => set({ highlights: v })}
          placeholder="Coordinated promotional activities and campus outreach"
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Project ────────────────────────────────────────────── */

export const emptyProject = (): ProjectRow => ({
  id: '',
  title: '',
  subtitle: '',
  description: '',
  tech_stack: [],
  highlights: [],
  start_date: '',
  end_date: '',
  is_ongoing: false,
  project_url: '',
  repo_url: '',
  display_order: 0,
});

export const ProjectDialog: React.FC<DialogProps<ProjectRow>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<ProjectRow>({
    ...initial,
    tech_stack: [...(initial.tech_stack || [])],
    highlights: [...(initial.highlights || [])],
  });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<ProjectRow>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal
      title={initial.id ? 'Edit Project' : 'Add Project'}
      onClose={onClose}
      onSubmit={submit}
      busy={busy}
      error={error}
      wide
    >
      <FormGrid>
        <TextField label="Project title" value={draft.title} onChange={(v) => set({ title: v })} required />
        <TextField label="Subtitle" value={draft.subtitle} onChange={(v) => set({ subtitle: v })} placeholder="Personal / Academic / Hackathon" />
        <TextAreaField
          label="Description"
          value={draft.description}
          onChange={(v) => set({ description: v })}
          rows={3}
          placeholder="What problem does it solve, and what did you build?"
        />
        <TagInput label="Tech stack" values={draft.tech_stack} onChange={(v) => set({ tech_stack: v })} placeholder="Python, FastAPI, React..." />
        <TextField label="Start date" type="month" value={draft.start_date} onChange={(v) => set({ start_date: v })} />
        <TextField label="End date" type="month" value={draft.end_date} onChange={(v) => set({ end_date: v })} />
        <CheckboxField label="Still working on this" checked={draft.is_ongoing} onChange={(v) => set({ is_ongoing: v })} span />
        <TextField label="Live URL" type="url" value={draft.project_url} onChange={(v) => set({ project_url: v })} placeholder="https://" />
        <TextField label="Repository URL" type="url" value={draft.repo_url} onChange={(v) => set({ repo_url: v })} placeholder="https://github.com/..." />
        <BulletEditor
          label="Key highlights"
          values={draft.highlights}
          onChange={(v) => set({ highlights: v })}
          placeholder="Cut query latency by 60% with a vector index"
        />
      </FormGrid>
    </Modal>
  );
};

/* ── Award ──────────────────────────────────────────────── */

export const emptyAward = (): AwardRow => ({
  id: '',
  title: '',
  issued_by: '',
  issue_date: '',
  achievement_type: 'Academic',
  description: '',
  award_url: '',
  certificate_doc_id: null,
  display_order: 0,
});

export const AwardDialog: React.FC<
  DialogProps<AwardRow> & { certificates?: { id: string; label: string }[] }
> = ({ initial, onClose, onSave, certificates = [] }) => {
  const [draft, setDraft] = useState<AwardRow>({ ...initial });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<AwardRow>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal
      title={initial.id ? 'Edit Achievement' : 'Add Achievement'}
      onClose={onClose}
      onSubmit={submit}
      busy={busy}
      error={error}
      wide
    >
      <FormGrid>
        <TextField label="Title" value={draft.title} onChange={(v) => set({ title: v })} required placeholder="2nd Runner Up - CodeSprint 3.0" />
        <TextField label="Issued by" value={draft.issued_by} onChange={(v) => set({ issued_by: v })} placeholder="Institute / organisation" />
        <TextField label="Issue date" type="date" value={draft.issue_date} onChange={(v) => set({ issue_date: v })} />
        <SelectField
          label="Achievement type"
          value={draft.achievement_type}
          onChange={(v) => set({ achievement_type: v })}
          options={ACHIEVEMENT_TYPES}
          allowBlank={false}
        />
        <TextField label="Award link" type="url" value={draft.award_url} onChange={(v) => set({ award_url: v })} placeholder="https://" span />
        <TextAreaField label="Description" value={draft.description} onChange={(v) => set({ description: v })} rows={3} />
        {certificates.length > 0 && (
          <div className="span-2">
            <label className="mp-input-label">Attach certificate</label>
            <select
              className="mp-select"
              value={draft.certificate_doc_id ?? ''}
              onChange={(e) => set({ certificate_doc_id: e.target.value || null })}
            >
              <option value="">No attachment</option>
              {certificates.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.label}
                </option>
              ))}
            </select>
            <div className="mp-hint">Upload files from the Documents tab to see them here.</div>
          </div>
        )}
      </FormGrid>
    </Modal>
  );
};

/* ── Certification ──────────────────────────────────────── */

export const emptyCertification = (): CertificationRow => ({
  id: '',
  name: '',
  issuer: '',
  course_duration: '',
  validity: 'Lifetime Validity',
  cert_type: '',
  specialization: '',
  courses: '',
  pre_assessment_score: '',
  marks_obtained: '',
  points_earned: '',
  conclusion: 'Completed',
  credential_url: '',
  certificate_doc_id: null,
  display_order: 0,
});

export const CertificationDialog: React.FC<DialogProps<CertificationRow>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<CertificationRow>({ ...initial });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<CertificationRow>) => setDraft((d) => ({ ...d, ...patch }));

  return (
    <Modal
      title={initial.id ? 'Edit Certification' : 'Add Certification'}
      onClose={onClose}
      onSubmit={submit}
      busy={busy}
      error={error}
      wide
    >
      <FormGrid>
        <TextField label="Certification name" value={draft.name} onChange={(v) => set({ name: v })} required />
        <TextField label="Issued by" value={draft.issuer} onChange={(v) => set({ issuer: v })} placeholder="Provider name" />
        <TextField label="Course duration" value={draft.course_duration} onChange={(v) => set({ course_duration: v })} placeholder="6 weeks" />
        <TextField label="Validity" value={draft.validity} onChange={(v) => set({ validity: v })} placeholder="Lifetime Validity" />
        <TextField label="Type" value={draft.cert_type} onChange={(v) => set({ cert_type: v })} placeholder="Aptitude / Technical / Communication" />
        <TextField label="Specialization" value={draft.specialization} onChange={(v) => set({ specialization: v })} />
        <TextField label="Courses covered" value={draft.courses} onChange={(v) => set({ courses: v })} span />

        <FieldsetTitle>Scores</FieldsetTitle>
        <TextField label="Pre-assessment score" value={draft.pre_assessment_score} onChange={(v) => set({ pre_assessment_score: v })} />
        <TextField label="Marks obtained" value={draft.marks_obtained} onChange={(v) => set({ marks_obtained: v })} />
        <TextField label="Points earned" value={draft.points_earned} onChange={(v) => set({ points_earned: v })} />
        <SelectField label="Conclusion" value={draft.conclusion} onChange={(v) => set({ conclusion: v })} options={CONCLUSIONS} />
        <TextField label="Credential URL" type="url" value={draft.credential_url} onChange={(v) => set({ credential_url: v })} span />
      </FormGrid>
    </Modal>
  );
};

/* ── Benchmark assessment ───────────────────────────────── */

export const BenchmarkDialog: React.FC<DialogProps<BenchmarkRow>> = ({ initial, onClose, onSave }) => {
  const [draft, setDraft] = useState<BenchmarkRow>({ ...initial });
  const { busy, error, submit } = useSubmit(draft, onSave, onClose);
  const set = (patch: Partial<BenchmarkRow>) => setDraft((d) => ({ ...d, ...patch }));
  const stageName = draft.stage.charAt(0).toUpperCase() + draft.stage.slice(1);

  return (
    <Modal title={`Edit ${stageName} Assessment`} onClose={onClose} onSubmit={submit} busy={busy} error={error} wide>
      <FormGrid>
        <TextField label="Assessment provider" value={draft.provider} onChange={(v) => set({ provider: v })} placeholder="e.g. Employability Test" />
        <TextField label="Taken on" type="date" value={draft.taken_on} onChange={(v) => set({ taken_on: v })} />
        <NumberField label="Analytical score" value={draft.analytical_score} onChange={(v) => set({ analytical_score: v })} min={0} max={100} step={0.01} />
        <NumberField label="Logical score" value={draft.logical_score} onChange={(v) => set({ logical_score: v })} min={0} max={100} step={0.01} />
        <NumberField label="Verbal score" value={draft.verbal_score} onChange={(v) => set({ verbal_score: v })} min={0} max={100} step={0.01} />
        <NumberField label="Quantitative score" value={draft.quantitative_score} onChange={(v) => set({ quantitative_score: v })} min={0} max={100} step={0.01} />
        <NumberField label="Total score" value={draft.total_score} onChange={(v) => set({ total_score: v })} min={0} max={100} step={0.01} span />
      </FormGrid>
    </Modal>
  );
};

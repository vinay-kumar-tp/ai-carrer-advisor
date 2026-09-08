import React, { useEffect, useMemo, useState } from 'react';
// lucide-react v1 removed brand glyphs, so social rows use semantic icons
// tinted with each platform's colour instead.
import { Award as AwardIcon, Brush, Briefcase, GitBranch, Globe, MapPin, Palette, Plus } from 'lucide-react';
import api from '../../services/api';
import {
  Card,
  Chip,
  ConfirmDialog,
  EMPTY,
  EmptyState,
  Field,
  FieldGrid,
  IconButton,
  Pill,
  ProgressBar,
  SeeMore,
  dateRange,
  display,
  joinParts,
} from '../../components/profile/ui';
import {
  AboutDialog,
  AcademicSummaryDialog,
  AdditionalInfoDialog,
  AwardDialog,
  BasicDialog,
  BenchmarkDialog,
  CertificationDialog,
  ContactDialog,
  EducationDialog,
  JobPreferencesDialog,
  MentorshipDialog,
  PersonalDialog,
  PositionDialog,
  ProgramDialog,
  ProjectDialog,
  SkillsDialog,
  SocialDialog,
  TrainingDialog,
  WorkDialog,
  emptyAward,
  emptyCertification,
  emptyEducation,
  emptyPosition,
  emptyProject,
  emptyWork,
} from './dialogs';
import type {
  AwardRow,
  BenchmarkRow,
  CertificationRow,
  EducationRow,
  PositionRow,
  ProfileAggregate,
  ProjectRow,
  WorkRow,
} from './types';

type SaveResult = { ok: boolean; message?: string };

type Props = {
  profile: ProfileAggregate;
  save: (method: 'put' | 'post' | 'delete', path: string, body?: unknown) => Promise<SaveResult>;
  notify: (message: string, tone?: 'success' | 'error') => void;
  onGoToTab: (tab: 'resume' | 'documents') => void;
};

type Dialog =
  | null
  | { kind: 'basic' | 'contact' | 'personal' | 'social' | 'about' | 'additional' }
  | { kind: 'program' | 'mentorship' | 'training' | 'academic' | 'jobprefs' | 'skills' }
  | { kind: 'education'; row: EducationRow }
  | { kind: 'work'; row: WorkRow }
  | { kind: 'position'; row: PositionRow }
  | { kind: 'project'; row: ProjectRow }
  | { kind: 'award'; row: AwardRow }
  | { kind: 'certification'; row: CertificationRow }
  | { kind: 'benchmark'; row: BenchmarkRow };

type PendingDelete = { title: string; message: string; path: string } | null;

const STAGE_LABEL: Record<string, string> = {
  baseline: 'Baseline Assessment',
  midline: 'Midline Assessment',
  endline: 'Endline Assessment',
};

const initials = (name: string) =>
  name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('') || '?';

const formatCtc = (amount: number | null, period: string) =>
  amount === null || amount === undefined ? EMPTY : `${amount.toLocaleString('en-IN')}/${period || 'Year'}`;

export const ProfileTab: React.FC<Props> = ({ profile, save, notify, onGoToTab }) => {
  const [dialog, setDialog] = useState<Dialog>(null);
  const [pendingDelete, setPendingDelete] = useState<PendingDelete>(null);
  const [deleting, setDeleting] = useState(false);
  const [skillCatalog, setSkillCatalog] = useState<string[]>([]);
  const [docs, setDocs] = useState<{ marksheets: { id: string; label: string }[]; certificates: { id: string; label: string }[] }>(
    { marksheets: [], certificates: [] },
  );

  // Suggestion sources for the dialogs. Failures are non-fatal — the inputs
  // still accept free text, so we stay quiet if these can't load.
  useEffect(() => {
    api
      .get('/profile/skills/catalog')
      .then(({ data }) => setSkillCatalog((data as { name: string }[]).map((s) => s.name)))
      .catch(() => undefined);

    api
      .get('/profile/documents')
      .then(({ data }) =>
        setDocs({
          marksheets: (data.marksheets || []).map((d: any) => ({ id: d.id, label: d.label })),
          certificates: [...(data.certificates || []), ...(data.others || [])].map((d: any) => ({
            id: d.id,
            label: d.label,
          })),
        }),
      )
      .catch(() => undefined);
  }, []);

  /** Wraps a save so success closes the dialog and raises a toast. */
  const handler =
    (method: 'put' | 'post' | 'delete', path: string, successMessage: string) =>
    async (body?: unknown): Promise<SaveResult> => {
      const result = await save(method, path, body);
      if (result.ok) notify(successMessage);
      return result;
    };

  const confirmDelete = async () => {
    if (!pendingDelete) return;
    setDeleting(true);
    const result = await save('delete', pendingDelete.path);
    setDeleting(false);
    setPendingDelete(null);
    notify(result.ok ? 'Removed' : result.message ?? 'Could not remove this item.', result.ok ? 'success' : 'error');
  };

  const { basic, contact, personal, social, program, mentorship, academic_summary: academic, job_preferences: prefs } = profile;

  const socialRows = useMemo(
    () => [
      { key: 'github', name: 'Github', url: social.github_url, icon: <GitBranch size={14} color="#24292f" /> },
      { key: 'linkedin', name: 'LinkedIn', url: social.linkedin_url, icon: <Briefcase size={14} color="#0a66c2" /> },
      { key: 'dribbble', name: 'Dribbble', url: social.dribbble_url, icon: <Palette size={14} color="#ea4c89" /> },
      { key: 'behance', name: 'Behance', url: social.behance_url, icon: <Brush size={14} color="#1769ff" /> },
      { key: 'portfolio', name: 'Portfolio', url: social.portfolio_url, icon: <Globe size={14} color="#64748b" /> },
    ],
    [social],
  );

  return (
    <>
      <div className="mp-grid">
        {/* ─────────────── Main column ─────────────── */}
        <div className="mp-col">
          {/* Identity */}
          <Card onEdit={() => setDialog({ kind: 'basic' })} editLabel="Edit basic details">
            <div className="mp-identity">
              {basic.avatar_url ? (
                <img className="mp-avatar" src={basic.avatar_url} alt={`${profile.full_name}'s profile photo`} />
              ) : (
                <div className="mp-avatar mp-avatar-fallback" aria-hidden="true">
                  {initials(profile.full_name)}
                </div>
              )}
              <div className="mp-identity-body">
                <h2 className="mp-identity-name">{profile.full_name}</h2>
                {basic.headline ? (
                  <div className="mp-identity-headline">{basic.headline}</div>
                ) : (
                  <button className="mp-btn-link" onClick={() => setDialog({ kind: 'basic' })}>
                    + Add a professional headline
                  </button>
                )}
                <div className="mp-identity-id">
                  Student ID: <strong>{display(basic.enrollment_id)}</strong>
                </div>
                <div className="mp-identity-meta">
                  <span>
                    <MapPin size={13} /> {display(basic.location)}
                  </span>
                  <span>
                    <Briefcase size={13} /> {display(basic.experience_level)}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Completion */}
          <Card>
            <div className="mp-progress-title">{profile.completion.percentage}% Profile Completed</div>
            <ProgressBar percentage={profile.completion.percentage} />
            {profile.completion.next_suggestions.length > 0 ? (
              <div className="mp-nudges">
                {profile.completion.next_suggestions.map((item) => (
                  <div className="mp-nudge" key={item.key}>
                    <h4>{item.title}</h4>
                    <p>Completing this section strengthens how recruiters read your profile.</p>
                    <div className="mp-nudge-missing">Missing fields:</div>
                    <ul>
                      {item.missing_fields.map((field) => (
                        <li key={field}>{field}</li>
                      ))}
                    </ul>
                    <div className="mp-nudge-foot">
                      <button
                        className="mp-btn mp-btn-outline mp-btn-sm"
                        onClick={() => {
                          const jump: Record<string, Dialog> = {
                            basic: { kind: 'basic' },
                            contact: { kind: 'contact' },
                            personal: { kind: 'personal' },
                            social: { kind: 'social' },
                            about: { kind: 'about' },
                            skills: { kind: 'skills' },
                            job_preferences: { kind: 'jobprefs' },
                            education: { kind: 'education', row: emptyEducation() },
                            projects: { kind: 'project', row: emptyProject() },
                            experience: { kind: 'work', row: emptyWork() },
                            awards: { kind: 'award', row: emptyAward() },
                            certifications: { kind: 'certification', row: emptyCertification() },
                          };
                          if (item.key === 'resume') onGoToTab('resume');
                          else setDialog(jump[item.key] ?? null);
                        }}
                      >
                        {item.action_label}
                      </button>
                      <span className="mp-nudge-gain">+{item.weight.toFixed(2)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="mp-inline-note" style={{ marginTop: '0.7rem' }}>
                Every section is filled in. Keep it fresh as you take on new work.
              </p>
            )}
          </Card>

          {/* Additional information */}
          <Card title="Additional Information" onEdit={() => setDialog({ kind: 'additional' })}>
            {profile.additional_info.length ? (
              <FieldGrid cols={2}>
                {profile.additional_info.map((row, index) => (
                  <Field key={`${row.label}-${index}`} label={row.label || 'Detail'} value={row.value} />
                ))}
              </FieldGrid>
            ) : (
              <p className="mp-inline-note">
                No extra details yet.{' '}
                <button className="mp-btn-link" onClick={() => setDialog({ kind: 'additional' })}>
                  Add custom fields
                </button>
              </p>
            )}
          </Card>

          {/* Program details */}
          <Card title="Program Details" onEdit={() => setDialog({ kind: 'program' })}>
            <SeeMore collapsedHeight={110}>
              <FieldGrid cols={2}>
                <Field label="Program Name" value={program.program_name} />
                <Field label="Academic / Financial Year" value={program.program_year} />
                <Field label="Institution Rating" value={program.institution_rating} />
                {program.program_extra.map((row, index) => (
                  <Field key={`${row.label}-${index}`} label={row.label || 'Detail'} value={row.value} />
                ))}
              </FieldGrid>
            </SeeMore>
          </Card>

          {/* Mentorship */}
          <Card title="Mentorship" onEdit={() => setDialog({ kind: 'mentorship' })}>
            <FieldGrid cols={2}>
              <Field label="Enrolled as Mentee" value={mentorship.is_mentee} />
              <Field label="Mentor" value={mentorship.mentor_name} />
              <Field label="Notes" value={mentorship.mentorship_notes} />
            </FieldGrid>
          </Card>

          {/* Training */}
          <Card title="Training" onEdit={() => setDialog({ kind: 'training' })}>
            {profile.training.length ? (
              <div className="mp-table-wrap">
                <table className="mp-table">
                  <thead>
                    <tr>
                      <th>Module</th>
                      <th>Status</th>
                      <th>Score</th>
                      <th>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    {profile.training.map((row, index) => (
                      <tr key={`${row.name}-${index}`}>
                        <td style={{ fontWeight: 700, color: '#1f2937' }}>{display(row.name)}</td>
                        <td>
                          {row.status ? (
                            <Pill tone={row.status === 'Completed' ? 'ready' : 'info'}>{row.status}</Pill>
                          ) : (
                            EMPTY
                          )}
                        </td>
                        <td>{display(row.score)}</td>
                        <td>{display(row.notes)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <EmptyState
                title="No training recorded"
                text="Track the training modules you've completed so recruiters see your upskilling."
                actionLabel="Add training"
                onAction={() => setDialog({ kind: 'training' })}
              />
            )}
          </Card>

          {/* Benchmark assessments */}
          {(['baseline', 'midline', 'endline'] as const).map((stage) => {
            const row = profile.benchmarks[stage];
            return (
              <Card
                key={stage}
                title={STAGE_LABEL[stage]}
                subtitle={row.provider || undefined}
                onEdit={() => setDialog({ kind: 'benchmark', row })}
              >
                <SeeMore collapsedHeight={96}>
                  <FieldGrid cols={3}>
                    <Field label="Analytical Score" value={row.analytical_score} />
                    <Field label="Logical Score" value={row.logical_score} />
                    <Field label="Verbal Score" value={row.verbal_score} />
                    <Field label="Quantitative Score" value={row.quantitative_score} />
                    <Field label="Total Score" value={row.total_score} />
                    <Field label="Taken On" value={row.taken_on} />
                  </FieldGrid>
                </SeeMore>
              </Card>
            );
          })}

          {/* Skills */}
          <Card title="Skills" onEdit={() => setDialog({ kind: 'skills' })}>
            {profile.skills.length ? (
              <div className="mp-chips">
                {profile.skills.map((skill) => (
                  <Chip key={skill.skill_id}>{skill.name}</Chip>
                ))}
              </div>
            ) : (
              <EmptyState
                title="No skills added"
                text="Recruiters filter candidates on skills. Add at least three to start showing up."
                actionLabel="Add skills"
                onAction={() => setDialog({ kind: 'skills' })}
              />
            )}
          </Card>

          {/* Job preferences */}
          <Card title="Job Preferences" onEdit={() => setDialog({ kind: 'jobprefs' })}>
            <FieldGrid cols={2}>
              <Field label="Open For" value={prefs.open_for} />
              <Field label="Job Roles" value={prefs.job_roles} />
              <Field label="Available for Hire" value={prefs.available_for_hire} />
              <Field label="Willing to relocate" value={prefs.willing_to_relocate} />
              <Field label="Preferred Location" value={prefs.preferred_locations} />
              <Field label="Industry" value={prefs.industry} />
              <Field label="Expected CTC" value={formatCtc(prefs.expected_ctc, prefs.ctc_period)} />
            </FieldGrid>
          </Card>

          {/* About me */}
          <Card title="About Me" onEdit={profile.about_me ? () => setDialog({ kind: 'about' }) : undefined}>
            {profile.about_me ? (
              <p style={{ margin: 0, fontSize: '0.87rem', color: '#45536e', whiteSpace: 'pre-wrap' }}>
                {profile.about_me}
              </p>
            ) : (
              <EmptyState
                text="Add a short summary of who you are and what you're aiming for."
                actionLabel="Add About Me"
                onAction={() => setDialog({ kind: 'about' })}
              />
            )}
          </Card>

          {/* Work experience */}
          <Card
            title="Work Experience"
            onAdd={() => setDialog({ kind: 'work', row: emptyWork() })}
            addLabel="Add work experience"
          >
            {profile.work_experiences.length ? (
              profile.work_experiences.map((row) => (
                <div className="mp-entry" key={row.id}>
                  <div className="mp-entry-head">
                    <div style={{ minWidth: 0 }}>
                      <div className="mp-entry-title">{row.role}</div>
                      <div className="mp-entry-meta">
                        {joinParts([row.company, row.employment_type, row.location])}
                      </div>
                      <div className="mp-entry-dates">
                        {dateRange(row.start_date, row.end_date, row.is_current) || EMPTY}
                      </div>
                    </div>
                    <div className="mp-card-actions">
                      <IconButton icon="pencil" label="Edit experience" onClick={() => setDialog({ kind: 'work', row })} />
                      <IconButton
                        icon="trash"
                        variant="danger"
                        label="Delete experience"
                        onClick={() =>
                          setPendingDelete({
                            title: 'Delete work experience',
                            message: `Remove "${row.role} at ${row.company}" from your profile?`,
                            path: `/profile/work-experience/${row.id}`,
                          })
                        }
                      />
                    </div>
                  </div>
                  {row.highlights.length > 0 && (
                    <SeeMore collapsedHeight={78}>
                      <ul className="mp-bullets">
                        {row.highlights.map((point, index) => (
                          <li key={index}>{point}</li>
                        ))}
                      </ul>
                    </SeeMore>
                  )}
                </div>
              ))
            ) : (
              <>
                <div className="mp-field-value" style={{ marginBottom: '0.6rem' }}>
                  {basic.experience_level || 'Fresher'}
                </div>
                <EmptyState
                  text="Add internships, part-time roles or freelance work."
                  actionLabel="Add work experience"
                  onAction={() => setDialog({ kind: 'work', row: emptyWork() })}
                />
              </>
            )}
          </Card>

          {/* Positions of responsibility */}
          <Card
            title="Position Of Responsibility"
            onAdd={() => setDialog({ kind: 'position', row: emptyPosition() })}
            addLabel="Add position"
          >
            {profile.positions.length ? (
              profile.positions.map((row) => (
                <div className="mp-entry" key={row.id}>
                  <div className="mp-entry-head">
                    <div style={{ minWidth: 0 }}>
                      <div className="mp-entry-title">{row.title}</div>
                      {(row.event_name || row.department) && (
                        <div className="mp-entry-meta">
                          <span className="mp-meta-label">Event/Committee: </span>
                          {joinParts([row.event_name, row.department ? `(${row.department})` : ''], ' ')}
                        </div>
                      )}
                      {row.organization && (
                        <div className="mp-entry-meta">
                          <span className="mp-meta-label">Organization: </span>
                          {row.organization}
                        </div>
                      )}
                      <div className="mp-entry-dates">{dateRange(row.start_date, row.end_date) || EMPTY}</div>
                    </div>
                    <div className="mp-card-actions">
                      <IconButton icon="pencil" label="Edit position" onClick={() => setDialog({ kind: 'position', row })} />
                      <IconButton
                        icon="trash"
                        variant="danger"
                        label="Delete position"
                        onClick={() =>
                          setPendingDelete({
                            title: 'Delete position',
                            message: `Remove "${row.title}" from your profile?`,
                            path: `/profile/positions/${row.id}`,
                          })
                        }
                      />
                    </div>
                  </div>
                  {row.highlights.length > 0 && (
                    <SeeMore collapsedHeight={78}>
                      <ul className="mp-bullets">
                        {row.highlights.map((point, index) => (
                          <li key={index}>{point}</li>
                        ))}
                      </ul>
                    </SeeMore>
                  )}
                </div>
              ))
            ) : (
              <EmptyState
                text="Club roles, event coordination and committee work all count."
                actionLabel="Add position"
                onAction={() => setDialog({ kind: 'position', row: emptyPosition() })}
              />
            )}
          </Card>

          {/* Education */}
          <Card
            title="Education"
            onAdd={() => setDialog({ kind: 'education', row: emptyEducation() })}
            addLabel="Add education"
            actions={
              <button className="mp-btn mp-btn-ghost mp-btn-sm" onClick={() => setDialog({ kind: 'academic' })}>
                School results
              </button>
            }
          >
            {profile.educations.length ? (
              profile.educations.map((row) => (
                <div className="mp-entry" key={row.id}>
                  <div className="mp-entry-head">
                    <div style={{ minWidth: 0 }}>
                      <div className="mp-entry-title">{row.institute}</div>
                      <div className="mp-entry-meta">
                        {joinParts([
                          row.degree,
                          row.specialization,
                          row.cgpa !== null ? `CGPA: ${row.cgpa}/${row.cgpa_scale}` : '',
                          row.percentage !== null ? `${row.percentage}%` : '',
                        ])}
                      </div>
                      <div className="mp-entry-dates">
                        {dateRange(row.start_year, row.end_year, row.is_current) || EMPTY}
                      </div>
                    </div>
                    <div className="mp-card-actions">
                      <IconButton
                        icon="pencil"
                        label="Edit education"
                        onClick={() => setDialog({ kind: 'education', row })}
                      />
                      <IconButton
                        icon="trash"
                        variant="danger"
                        label="Delete education"
                        onClick={() =>
                          setPendingDelete({
                            title: 'Delete education',
                            message: `Remove "${row.institute}" from your profile?`,
                            path: `/profile/education/${row.id}`,
                          })
                        }
                      />
                    </div>
                  </div>

                  {row.semesters.length > 0 && (
                    <>
                      <div style={{ fontWeight: 700, fontSize: '0.84rem', margin: '0.7rem 0 0.4rem' }}>
                        Semester wise Performance
                      </div>
                      <div className="mp-table-wrap">
                        <table className="mp-table">
                          <thead>
                            <tr>
                              <th>Semester</th>
                              <th>CGPA</th>
                              <th>Ongoing Backlogs</th>
                              <th>Total Backlogs</th>
                              <th>Marksheet</th>
                            </tr>
                          </thead>
                          <tbody>
                            {row.semesters.map((sem, index) => {
                              const doc = docs.marksheets.find((d) => d.id === sem.marksheet_doc_id);
                              return (
                                <tr key={`${sem.semester}-${index}`}>
                                  <td>{display(sem.semester)}</td>
                                  <td className="mp-num">{display(sem.cgpa)}</td>
                                  <td>{display(sem.ongoing_backlogs)}</td>
                                  <td>{display(sem.total_backlogs)}</td>
                                  <td>
                                    {doc ? (
                                      <button className="mp-btn-link" onClick={() => onGoToTab('documents')}>
                                        {doc.label}
                                      </button>
                                    ) : (
                                      EMPTY
                                    )}
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </>
                  )}

                  <div style={{ marginTop: '0.7rem' }}>
                    <div style={{ fontWeight: 700, fontSize: '0.84rem', marginBottom: '0.25rem' }}>Backlogs</div>
                    <div className="mp-inline-note">Ongoing Backlogs: {row.ongoing_backlogs}</div>
                    <div className="mp-inline-note">Total Backlogs: {row.total_backlogs}</div>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState
                title="No education added"
                text="Add your degree, specialization and semester results."
                actionLabel="Add education"
                onAction={() => setDialog({ kind: 'education', row: emptyEducation() })}
              />
            )}

            <div className="mp-divider" />
            <FieldGrid cols={2}>
              <Field
                label="10th"
                value={academic.class_10_percentage !== null ? `${academic.class_10_percentage}%` : null}
              >
                {academic.class_10_percentage !== null ? (
                  <>
                    {academic.class_10_percentage}%
                    {academic.class_10_board ? (
                      <span className="mp-inline-note"> · {academic.class_10_board}</span>
                    ) : null}
                  </>
                ) : undefined}
              </Field>
              <Field
                label="12th"
                value={academic.class_12_percentage !== null ? `${academic.class_12_percentage}%` : null}
              >
                {academic.class_12_percentage !== null ? (
                  <>
                    {academic.class_12_percentage}%
                    {academic.class_12_board ? (
                      <span className="mp-inline-note"> · {academic.class_12_board}</span>
                    ) : null}
                  </>
                ) : undefined}
              </Field>
            </FieldGrid>
          </Card>

          {/* Projects */}
          <Card title="Projects" onAdd={() => setDialog({ kind: 'project', row: emptyProject() })} addLabel="Add project">
            {profile.projects.length ? (
              profile.projects.map((row) => (
                <div className="mp-entry" key={row.id}>
                  <div className="mp-entry-head">
                    <div style={{ minWidth: 0 }}>
                      <div className="mp-entry-title">{row.title}</div>
                      {row.subtitle && <div className="mp-entry-meta">{row.subtitle}</div>}
                      {row.tech_stack.length > 0 && (
                        <div className="mp-chips" style={{ marginTop: '0.35rem' }}>
                          {row.tech_stack.map((tech) => (
                            <Chip key={tech} accent>
                              {tech}
                            </Chip>
                          ))}
                        </div>
                      )}
                      <div className="mp-entry-dates">
                        {dateRange(row.start_date, row.end_date, row.is_ongoing) || EMPTY}
                      </div>
                    </div>
                    <div className="mp-card-actions">
                      <IconButton icon="pencil" label="Edit project" onClick={() => setDialog({ kind: 'project', row })} />
                      <IconButton
                        icon="trash"
                        variant="danger"
                        label="Delete project"
                        onClick={() =>
                          setPendingDelete({
                            title: 'Delete project',
                            message: `Remove "${row.title}" from your profile?`,
                            path: `/profile/projects/${row.id}`,
                          })
                        }
                      />
                    </div>
                  </div>
                  {row.description && (
                    <p style={{ margin: '0.45rem 0 0', fontSize: '0.83rem', color: '#45536e' }}>{row.description}</p>
                  )}
                  {row.highlights.length > 0 && (
                    <SeeMore collapsedHeight={78}>
                      <ul className="mp-bullets">
                        {row.highlights.map((point, index) => (
                          <li key={index}>{point}</li>
                        ))}
                      </ul>
                    </SeeMore>
                  )}
                  {(row.project_url || row.repo_url) && (
                    <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.45rem', fontSize: '0.8rem' }}>
                      {row.project_url && (
                        <a href={row.project_url} target="_blank" rel="noreferrer noopener">
                          Live demo
                        </a>
                      )}
                      {row.repo_url && (
                        <a href={row.repo_url} target="_blank" rel="noreferrer noopener">
                          Source code
                        </a>
                      )}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <EmptyState
                title="No projects yet"
                text="Projects boost your resume's credibility and showcase your expertise."
                actionLabel="Add Projects"
                onAction={() => setDialog({ kind: 'project', row: emptyProject() })}
              />
            )}
          </Card>

          {/* Awards */}
          <Card
            title="Awards or Achievements"
            onAdd={() => setDialog({ kind: 'award', row: emptyAward() })}
            addLabel="Add achievement"
          >
            {profile.awards.length ? (
              profile.awards.map((row) => {
                const doc = docs.certificates.find((d) => d.id === row.certificate_doc_id);
                return (
                  <div className="mp-entry" key={row.id}>
                    <div className="mp-entry-head">
                      <div style={{ minWidth: 0 }}>
                        <div className="mp-entry-title">{row.title}</div>
                        <div className="mp-entry-meta">
                          <span className="mp-meta-label">Issued By: </span>
                          {display(row.issued_by)}
                        </div>
                        <div className="mp-entry-meta">
                          <span className="mp-meta-label">Issued Date: </span>
                          {display(row.issue_date)}
                        </div>
                        <div className="mp-entry-meta">
                          <span className="mp-meta-label">Achievement Type: </span>
                          {display(row.achievement_type)}
                        </div>
                        {row.award_url && (
                          <div style={{ marginTop: '0.25rem', fontSize: '0.8rem' }}>
                            <a href={row.award_url} target="_blank" rel="noreferrer noopener">
                              Award Link
                            </a>
                          </div>
                        )}
                      </div>
                      <div className="mp-card-actions">
                        <IconButton icon="pencil" label="Edit achievement" onClick={() => setDialog({ kind: 'award', row })} />
                        <IconButton
                          icon="trash"
                          variant="danger"
                          label="Delete achievement"
                          onClick={() =>
                            setPendingDelete({
                              title: 'Delete achievement',
                              message: `Remove "${row.title}" from your profile?`,
                              path: `/profile/awards/${row.id}`,
                            })
                          }
                        />
                      </div>
                    </div>
                    {row.description && (
                      <p style={{ margin: '0.4rem 0 0', fontSize: '0.83rem', color: '#45536e' }}>{row.description}</p>
                    )}
                    {doc && (
                      <button className="mp-doc-chip" style={{ marginTop: '0.5rem' }} onClick={() => onGoToTab('documents')}>
                        <AwardIcon size={13} /> {doc.label}
                      </button>
                    )}
                  </div>
                );
              })
            ) : (
              <EmptyState
                title="No achievements yet"
                text="Hackathon placements, scholarships and competition wins belong here."
                actionLabel="Add achievement"
                onAction={() => setDialog({ kind: 'award', row: emptyAward() })}
              />
            )}
          </Card>

          {/* Certifications */}
          <Card
            title="Certifications"
            onAdd={() => setDialog({ kind: 'certification', row: emptyCertification() })}
            addLabel="Add certification"
          >
            {profile.certifications.length ? (
              profile.certifications.map((row) => (
                <div className="mp-entry" key={row.id}>
                  <div className="mp-entry-head">
                    <div style={{ minWidth: 0 }}>
                      <div className="mp-entry-title">{row.name}</div>
                      <div className="mp-entry-meta">{display(row.issuer)}</div>
                      <div className="mp-entry-meta">
                        <span className="mp-meta-label">Course Duration: </span>
                        {display(row.course_duration)} · {display(row.validity)}
                      </div>
                      <div className="mp-entry-meta">
                        <span className="mp-meta-label">Type: </span>
                        {display(row.cert_type)}
                        <span className="mp-meta-label"> Specialization: </span>
                        {display(row.specialization)}
                        <span className="mp-meta-label"> Courses: </span>
                        {display(row.courses)}
                      </div>
                      <div className="mp-entry-meta">
                        <span className="mp-meta-label">Pre assessment score: </span>
                        {display(row.pre_assessment_score)}
                        <span className="mp-meta-label"> Marks obtained: </span>
                        {display(row.marks_obtained)}
                        <span className="mp-meta-label"> Points earned: </span>
                        {display(row.points_earned)}
                        <span className="mp-meta-label"> Conclusion: </span>
                        {display(row.conclusion)}
                      </div>
                      {row.credential_url && (
                        <div style={{ marginTop: '0.25rem', fontSize: '0.8rem' }}>
                          <a href={row.credential_url} target="_blank" rel="noreferrer noopener">
                            View credential
                          </a>
                        </div>
                      )}
                    </div>
                    <div className="mp-card-actions">
                      <IconButton
                        icon="pencil"
                        label="Edit certification"
                        onClick={() => setDialog({ kind: 'certification', row })}
                      />
                      <IconButton
                        icon="trash"
                        variant="danger"
                        label="Delete certification"
                        onClick={() =>
                          setPendingDelete({
                            title: 'Delete certification',
                            message: `Remove "${row.name}" from your profile?`,
                            path: `/profile/certifications/${row.id}`,
                          })
                        }
                      />
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState
                title="No certifications yet"
                text="Add courses and specializations you've completed."
                actionLabel="Add certification"
                onAction={() => setDialog({ kind: 'certification', row: emptyCertification() })}
              />
            )}
          </Card>
        </div>

        {/* ─────────────── Sidebar ─────────────── */}
        <div className="mp-col">
          <Card title="Contact Details" onEdit={() => setDialog({ kind: 'contact' })}>
            <FieldGrid cols={1}>
              <Field label="Email" value={contact.email} />
              <Field label="Contact No." value={contact.phone} />
            </FieldGrid>
          </Card>

          <Card title="Social Links" onEdit={() => setDialog({ kind: 'social' })}>
            {socialRows.map((row) =>
              row.url ? (
                <a
                  key={row.key}
                  className="mp-social-row is-linked"
                  href={row.url}
                  target="_blank"
                  rel="noreferrer noopener"
                >
                  {row.icon}
                  <span className="mp-social-name">{row.name}</span>
                </a>
              ) : (
                <button key={row.key} className="mp-social-row" onClick={() => setDialog({ kind: 'social' })}>
                  {row.icon}
                  <span className="mp-social-name">{row.name}</span>
                  <span className="mp-social-add" aria-hidden="true">
                    <Plus size={12} />
                  </span>
                </button>
              ),
            )}
            {social.other_links.map((link, index) => (
              <a
                key={`${link.url}-${index}`}
                className="mp-social-row is-linked"
                href={link.url}
                target="_blank"
                rel="noreferrer noopener"
              >
                <Globe size={14} />
                <span className="mp-social-name">{link.label || link.url}</span>
              </a>
            ))}
          </Card>

          <Card title="Personal Details" onEdit={() => setDialog({ kind: 'personal' })}>
            <FieldGrid cols={1}>
              <Field label="Gender" value={personal.gender} />
              <Field label="Country" value={personal.country} />
              <Field label="State" value={personal.state} />
              <Field label="City" value={personal.city} />
              <Field label="Date of Birth" value={personal.date_of_birth} />
            </FieldGrid>
          </Card>
        </div>
      </div>

      {/* ─────────────── Dialogs ─────────────── */}
      {dialog?.kind === 'basic' && (
        <BasicDialog
          initial={{ ...basic, full_name: profile.full_name }}
          onClose={() => setDialog(null)}
          onSave={handler('put', '/profile/basic', 'Basic details saved')}
        />
      )}
      {dialog?.kind === 'contact' && (
        <ContactDialog initial={contact} onClose={() => setDialog(null)} onSave={handler('put', '/profile/contact', 'Contact details saved')} />
      )}
      {dialog?.kind === 'personal' && (
        <PersonalDialog initial={personal} onClose={() => setDialog(null)} onSave={handler('put', '/profile/personal', 'Personal details saved')} />
      )}
      {dialog?.kind === 'social' && (
        <SocialDialog initial={social} onClose={() => setDialog(null)} onSave={handler('put', '/profile/social', 'Social links saved')} />
      )}
      {dialog?.kind === 'about' && (
        <AboutDialog
          initial={profile.about_me}
          onClose={() => setDialog(null)}
          onSave={async (about_me) => handler('put', '/profile/about', 'About me saved')({ about_me })}
        />
      )}
      {dialog?.kind === 'additional' && (
        <AdditionalInfoDialog
          initial={profile.additional_info}
          onClose={() => setDialog(null)}
          onSave={async (rows) =>
            handler('put', '/profile/additional-info', 'Additional information saved')({
              additional_info: rows.filter((r) => r.label.trim() || r.value.trim()),
            })
          }
        />
      )}
      {dialog?.kind === 'program' && (
        <ProgramDialog initial={program} onClose={() => setDialog(null)} onSave={handler('put', '/profile/program', 'Program details saved')} />
      )}
      {dialog?.kind === 'mentorship' && (
        <MentorshipDialog initial={mentorship} onClose={() => setDialog(null)} onSave={handler('put', '/profile/mentorship', 'Mentorship saved')} />
      )}
      {dialog?.kind === 'training' && (
        <TrainingDialog
          initial={profile.training}
          onClose={() => setDialog(null)}
          onSave={async (rows) =>
            handler('put', '/profile/training', 'Training saved')({ training_details: rows.filter((r) => r.name.trim()) })
          }
        />
      )}
      {dialog?.kind === 'academic' && (
        <AcademicSummaryDialog
          initial={academic}
          onClose={() => setDialog(null)}
          onSave={handler('put', '/profile/academic-summary', 'School results saved')}
        />
      )}
      {dialog?.kind === 'jobprefs' && (
        <JobPreferencesDialog initial={prefs} onClose={() => setDialog(null)} onSave={handler('put', '/profile/job-preferences', 'Job preferences saved')} />
      )}
      {dialog?.kind === 'skills' && (
        <SkillsDialog
          initial={profile.skills.map((s) => s.name)}
          suggestions={skillCatalog}
          onClose={() => setDialog(null)}
          onSave={async (skills) => handler('put', '/profile/skills', 'Skills saved')({ skills })}
        />
      )}
      {dialog?.kind === 'education' && (
        <EducationDialog
          initial={dialog.row}
          marksheets={docs.marksheets}
          onClose={() => setDialog(null)}
          onSave={async (row) => {
            const { id, ...body } = row;
            return id
              ? handler('put', `/profile/education/${id}`, 'Education updated')(body)
              : handler('post', '/profile/education', 'Education added')(body);
          }}
        />
      )}
      {dialog?.kind === 'work' && (
        <WorkDialog
          initial={dialog.row}
          onClose={() => setDialog(null)}
          onSave={async (row) => {
            const { id, ...body } = row;
            body.highlights = body.highlights.filter((h) => h.trim());
            return id
              ? handler('put', `/profile/work-experience/${id}`, 'Work experience updated')(body)
              : handler('post', '/profile/work-experience', 'Work experience added')(body);
          }}
        />
      )}
      {dialog?.kind === 'position' && (
        <PositionDialog
          initial={dialog.row}
          onClose={() => setDialog(null)}
          onSave={async (row) => {
            const { id, ...body } = row;
            body.highlights = body.highlights.filter((h) => h.trim());
            return id
              ? handler('put', `/profile/positions/${id}`, 'Position updated')(body)
              : handler('post', '/profile/positions', 'Position added')(body);
          }}
        />
      )}
      {dialog?.kind === 'project' && (
        <ProjectDialog
          initial={dialog.row}
          onClose={() => setDialog(null)}
          onSave={async (row) => {
            const { id, ...body } = row;
            body.highlights = body.highlights.filter((h) => h.trim());
            return id
              ? handler('put', `/profile/projects/${id}`, 'Project updated')(body)
              : handler('post', '/profile/projects', 'Project added')(body);
          }}
        />
      )}
      {dialog?.kind === 'award' && (
        <AwardDialog
          initial={dialog.row}
          certificates={docs.certificates}
          onClose={() => setDialog(null)}
          onSave={async (row) => {
            const { id, ...body } = row;
            return id
              ? handler('put', `/profile/awards/${id}`, 'Achievement updated')(body)
              : handler('post', '/profile/awards', 'Achievement added')(body);
          }}
        />
      )}
      {dialog?.kind === 'certification' && (
        <CertificationDialog
          initial={dialog.row}
          onClose={() => setDialog(null)}
          onSave={async (row) => {
            const { id, ...body } = row;
            return id
              ? handler('put', `/profile/certifications/${id}`, 'Certification updated')(body)
              : handler('post', '/profile/certifications', 'Certification added')(body);
          }}
        />
      )}
      {dialog?.kind === 'benchmark' && (
        <BenchmarkDialog
          initial={dialog.row}
          onClose={() => setDialog(null)}
          onSave={async (row) => {
            const { id, ...body } = row;
            return handler('put', `/profile/benchmarks/${row.stage}`, 'Assessment scores saved')(body);
          }}
        />
      )}

      {pendingDelete && (
        <ConfirmDialog
          title={pendingDelete.title}
          message={pendingDelete.message}
          busy={deleting}
          onConfirm={confirmDelete}
          onClose={() => setPendingDelete(null)}
        />
      )}
    </>
  );
};

import React, { useCallback, useEffect, useRef, useState } from 'react';
import { Download, Eye, FileUp, Pencil, Sparkles, Star, Trash2, Wand2 } from 'lucide-react';
import api from '../../services/api';
import {
  Card,
  ConfirmDialog,
  EMPTY,
  EmptyState,
  Loading,
  Modal,
  Pager,
  Pill,
  usePaged,
} from '../../components/profile/ui';
import { FormGrid, SelectField, TextField } from '../../components/profile/forms';
import { errorMessage } from './useProfileData';
import type { AtsReport, ResumeLibrary, ResumeRow } from './types';

type Props = {
  notify: (message: string, tone?: 'success' | 'error') => void;
  onChanged: () => void;
};

type JobOption = { id: string; title: string; company: string };

const SOURCE_LABEL: Record<string, string> = {
  generated: 'Generated',
  existing: 'Existing',
  tailored: 'Tailored',
};

const formatDate = (iso: string | null) =>
  iso ? new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric' }) : EMPTY;

/** Auth headers can't ride on a plain <a href>, so fetch the bytes then save. */
const saveBlob = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
};

export const ResumeTab: React.FC<Props> = ({ notify, onChanged }) => {
  const [library, setLibrary] = useState<ResumeLibrary | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);

  const [generating, setGenerating] = useState(false);
  const [generateOpen, setGenerateOpen] = useState(false);
  const [template, setTemplate] = useState('Template 1');
  const [generateError, setGenerateError] = useState<string | null>(null);

  const [renaming, setRenaming] = useState<ResumeRow | null>(null);
  const [renameDraft, setRenameDraft] = useState('');
  const [renameBusy, setRenameBusy] = useState(false);
  const [renameError, setRenameError] = useState<string | null>(null);

  const [tailoring, setTailoring] = useState<ResumeRow | null>(null);
  const [jobs, setJobs] = useState<JobOption[]>([]);
  const [jobId, setJobId] = useState('');
  const [tailorBusy, setTailorBusy] = useState(false);
  const [tailorError, setTailorError] = useState<string | null>(null);

  const [report, setReport] = useState<{ resume: ResumeRow; data: AtsReport } | null>(null);
  const [pendingDelete, setPendingDelete] = useState<ResumeRow | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [preview, setPreview] = useState<{ name: string; url: string } | null>(null);

  const fileInput = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get<ResumeLibrary>('/profile/resumes');
      setLibrary(data);
    } catch (error) {
      notify(errorMessage(error, 'Could not load your resumes.'), 'error');
    } finally {
      setLoading(false);
    }
  }, [notify]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => () => {
    if (preview) URL.revokeObjectURL(preview.url);
  }, [preview]);

  const paged = usePaged(library?.resumes ?? [], 10);

  const generate = async () => {
    setGenerating(true);
    setGenerateError(null);
    try {
      await api.post('/profile/resumes/generate', { template });
      setGenerateOpen(false);
      notify('Resume generated from your profile');
      await load();
      onChanged();
    } catch (error) {
      setGenerateError(errorMessage(error));
    } finally {
      setGenerating(false);
    }
  };

  const upload = async (file: File) => {
    setBusyId('upload');
    try {
      const form = new FormData();
      form.append('file', file);
      form.append('doc_type', 'resume');
      const { data: doc } = await api.post('/documents/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      await api.post('/profile/resumes', {
        name: file.name,
        source: 'existing',
        document_id: doc.id,
        status: 'ready',
      });
      notify('Resume uploaded');
      await load();
      onChanged();
    } catch (error) {
      notify(errorMessage(error, 'Upload failed.'), 'error');
    } finally {
      setBusyId(null);
      if (fileInput.current) fileInput.current.value = '';
    }
  };

  const checkAts = async (resume: ResumeRow) => {
    setBusyId(resume.id);
    try {
      const { data } = await api.post(`/profile/resumes/${resume.id}/ats-score`);
      setReport({ resume: data.resume, data });
      await load();
    } catch (error) {
      notify(errorMessage(error, 'Could not score this resume.'), 'error');
    } finally {
      setBusyId(null);
    }
  };

  const setPrimary = async (resume: ResumeRow) => {
    setBusyId(resume.id);
    try {
      await api.post(`/profile/resumes/${resume.id}/primary`);
      notify(`"${resume.name}" is now your primary resume`);
      await load();
      onChanged();
    } catch (error) {
      notify(errorMessage(error), 'error');
    } finally {
      setBusyId(null);
    }
  };

  const fetchPdf = async (resume: ResumeRow) => {
    const { data } = await api.get(`/profile/resumes/${resume.id}/download`, { responseType: 'blob' });
    return data as Blob;
  };

  const download = async (resume: ResumeRow) => {
    setBusyId(resume.id);
    try {
      const blob = await fetchPdf(resume);
      const extension = blob.type === 'application/pdf' ? '.pdf' : '';
      saveBlob(blob, /\.\w{2,4}$/.test(resume.name) ? resume.name : `${resume.name}${extension}`);
    } catch (error) {
      notify(errorMessage(error, 'Download failed.'), 'error');
    } finally {
      setBusyId(null);
    }
  };

  const openPreview = async (resume: ResumeRow) => {
    setBusyId(resume.id);
    try {
      const blob = await fetchPdf(resume);
      setPreview({ name: resume.name, url: URL.createObjectURL(blob) });
    } catch (error) {
      notify(errorMessage(error, 'Preview failed.'), 'error');
    } finally {
      setBusyId(null);
    }
  };

  const rename = async () => {
    if (!renaming) return;
    setRenameBusy(true);
    setRenameError(null);
    try {
      await api.put(`/profile/resumes/${renaming.id}`, { name: renameDraft.trim() });
      setRenaming(null);
      notify('Resume renamed');
      await load();
    } catch (error) {
      setRenameError(errorMessage(error));
    } finally {
      setRenameBusy(false);
    }
  };

  const openTailor = async (resume: ResumeRow) => {
    setTailoring(resume);
    setTailorError(null);
    setJobId('');
    try {
      const { data } = await api.get('/jobs/');
      setJobs(data.map((job: any) => ({ id: job.id, title: job.title, company: job.company })));
    } catch {
      setJobs([]);
    }
  };

  const tailor = async () => {
    if (!tailoring || !jobId) {
      setTailorError('Pick a job to optimise against.');
      return;
    }
    setTailorBusy(true);
    setTailorError(null);
    try {
      const { data } = await api.post(`/profile/resumes/${tailoring.id}/tailor`, { job_id: jobId });
      setTailoring(null);
      notify('Tailored copy created — your profile was left untouched');
      await load();
      onChanged();
      setReport({ resume: data.resume, data: data.ats_report });
    } catch (error) {
      setTailorError(errorMessage(error));
    } finally {
      setTailorBusy(false);
    }
  };

  const remove = async () => {
    if (!pendingDelete) return;
    setDeleteBusy(true);
    try {
      await api.delete(`/profile/resumes/${pendingDelete.id}`);
      notify('Resume removed');
      await load();
      onChanged();
    } catch (error) {
      notify(errorMessage(error), 'error');
    } finally {
      setDeleteBusy(false);
      setPendingDelete(null);
    }
  };

  if (loading) return <Loading label="Loading your resume library..." />;

  const resumes = library?.resumes ?? [];

  return (
    <>
      <Card
        title="Resume Library"
        subtitle={`${resumes.length} resume${resumes.length === 1 ? '' : 's'} · ${library?.templates.length ?? 0} templates available`}
        actions={
          <>
            <input
              ref={fileInput}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              style={{ display: 'none' }}
              onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])}
            />
            <button
              className="mp-btn mp-btn-ghost mp-btn-sm"
              onClick={() => fileInput.current?.click()}
              disabled={busyId === 'upload'}
            >
              <FileUp size={13} /> {busyId === 'upload' ? 'Uploading...' : 'Upload resume'}
            </button>
            <button className="mp-btn mp-btn-primary mp-btn-sm" onClick={() => setGenerateOpen(true)}>
              <Wand2 size={13} /> Generate My Resume
            </button>
          </>
        }
      >
        <p className="mp-inline-note" style={{ marginBottom: '0.8rem' }}>
          Only your primary resume updates automatically when you edit your profile. Use the{' '}
          <Sparkles size={12} style={{ verticalAlign: -1 }} /> action to optimise a copy for a specific job without
          changing your profile.
        </p>

        {resumes.length === 0 ? (
          <EmptyState
            title="No resumes yet"
            text="Generate one from your profile in a single click, or upload a resume you already have."
            actionLabel="Generate My Resume"
            onAction={() => setGenerateOpen(true)}
          />
        ) : (
          <>
            <div className="mp-table-wrap">
              <table className="mp-table" style={{ minWidth: 880 }}>
                <thead>
                  <tr>
                    <th style={{ width: 60 }}>Sr. No</th>
                    <th>Resume name</th>
                    <th style={{ width: 170 }}>Actions</th>
                    <th>Source</th>
                    <th>Template</th>
                    <th style={{ width: 150 }}>ATS Score</th>
                    <th>Status</th>
                    <th>Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {paged.slice.map((resume, index) => (
                    <tr key={resume.id}>
                      <td>{(paged.page - 1) * paged.pageSize + index + 1}</td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                          <span style={{ fontWeight: 700, color: '#1f2937' }}>{resume.name}</span>
                          {resume.is_primary && <Pill tone="primary">Primary</Pill>}
                        </div>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.25rem' }}>
                          <button
                            className="mp-iconbtn is-plain"
                            title="Preview"
                            aria-label={`Preview ${resume.name}`}
                            onClick={() => openPreview(resume)}
                            disabled={busyId === resume.id}
                          >
                            <Eye size={13} />
                          </button>
                          <button
                            className="mp-iconbtn is-plain"
                            title="Rename"
                            aria-label={`Rename ${resume.name}`}
                            onClick={() => {
                              setRenaming(resume);
                              setRenameDraft(resume.name);
                              setRenameError(null);
                            }}
                          >
                            <Pencil size={13} />
                          </button>
                          <button
                            className="mp-iconbtn"
                            title="Optimise for a job"
                            aria-label={`Optimise ${resume.name} for a job`}
                            onClick={() => openTailor(resume)}
                          >
                            <Sparkles size={13} />
                          </button>
                          <button
                            className="mp-iconbtn"
                            style={resume.is_primary ? { background: '#f0921f', color: '#fff' } : undefined}
                            title={resume.is_primary ? 'Primary resume' : 'Make primary'}
                            aria-label={resume.is_primary ? 'Primary resume' : `Make ${resume.name} primary`}
                            onClick={() => !resume.is_primary && setPrimary(resume)}
                            disabled={busyId === resume.id}
                          >
                            <Star size={13} />
                          </button>
                          <button
                            className="mp-iconbtn is-plain"
                            title="Download"
                            aria-label={`Download ${resume.name}`}
                            onClick={() => download(resume)}
                            disabled={busyId === resume.id}
                          >
                            <Download size={13} />
                          </button>
                          <button
                            className="mp-iconbtn is-danger"
                            title="Delete"
                            aria-label={`Delete ${resume.name}`}
                            onClick={() => setPendingDelete(resume)}
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </td>
                      <td>
                        <Pill tone="info">{SOURCE_LABEL[resume.source] || resume.source}</Pill>
                      </td>
                      <td>{resume.template || EMPTY}</td>
                      <td>
                        {resume.ats_score === null ? (
                          <button
                            className="mp-btn mp-btn-outline mp-btn-sm"
                            onClick={() => checkAts(resume)}
                            disabled={busyId === resume.id}
                          >
                            {busyId === resume.id ? 'Scoring...' : 'Check ATS score'}
                          </button>
                        ) : (
                          <button className="mp-btn-link" onClick={() => checkAts(resume)} disabled={busyId === resume.id}>
                            {resume.ats_score}/100 · re-check
                          </button>
                        )}
                      </td>
                      <td>
                        <Pill tone={resume.status === 'ready' ? 'ready' : 'draft'}>{resume.status}</Pill>
                      </td>
                      <td>{formatDate(resume.updated_at || resume.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Pager
              page={paged.page}
              pageCount={paged.pageCount}
              pageSize={paged.pageSize}
              onPage={paged.setPage}
              onPageSize={paged.setPageSize}
            />
          </>
        )}
      </Card>

      {/* Generate */}
      {generateOpen && (
        <Modal
          title="Generate My Resume"
          onClose={() => setGenerateOpen(false)}
          onSubmit={generate}
          submitLabel="Generate"
          busy={generating}
          error={generateError}
        >
          <FormGrid cols={1}>
            <SelectField
              label="Template"
              value={template}
              onChange={setTemplate}
              options={library?.templates ?? ['Template 1']}
              allowBlank={false}
              hint="Your profile data is snapshotted into the resume and scored for ATS readiness."
            />
          </FormGrid>
        </Modal>
      )}

      {/* Rename */}
      {renaming && (
        <Modal
          title="Rename Resume"
          onClose={() => setRenaming(null)}
          onSubmit={rename}
          busy={renameBusy}
          error={renameError}
        >
          <FormGrid cols={1}>
            <TextField label="Resume name" value={renameDraft} onChange={setRenameDraft} required />
          </FormGrid>
        </Modal>
      )}

      {/* Tailor */}
      {tailoring && (
        <Modal
          title="Optimise for a job"
          onClose={() => setTailoring(null)}
          onSubmit={tailor}
          submitLabel="Create tailored copy"
          busy={tailorBusy}
          error={tailorError}
        >
          <FormGrid cols={1}>
            {jobs.length === 0 ? (
              <p className="mp-inline-note">No jobs available on the job board yet.</p>
            ) : (
              <div>
                <label className="mp-input-label">
                  Target job <span className="mp-req">*</span>
                </label>
                <select className="mp-select" value={jobId} onChange={(e) => setJobId(e.target.value)} required>
                  <option value="">Select a job...</option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title} — {job.company}
                    </option>
                  ))}
                </select>
                <div className="mp-hint">
                  We copy "{tailoring.name}" and score the copy against that job's required skills. Your profile and
                  original resume stay as they are.
                </div>
              </div>
            )}
          </FormGrid>
        </Modal>
      )}

      {/* ATS report */}
      {report && (
        <Modal title="ATS Report" onClose={() => setReport(null)} wide>
          <div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.6rem', marginBottom: '0.4rem' }}>
              <span style={{ fontSize: '2rem', fontWeight: 700, color: '#f0921f' }}>{report.data.ats_score}</span>
              <span className="mp-inline-note">/ 100 for "{report.resume.name}"</span>
            </div>
            <div className="mp-progress-track">
              <div
                className="mp-progress-fill"
                style={{
                  width: `${report.data.ats_score}%`,
                  background: report.data.ats_score >= 70 ? '#22c55e' : report.data.ats_score >= 45 ? '#f0921f' : '#ef4444',
                }}
              />
            </div>
            <div className="mp-hint">Based on {report.data.word_count} words of resume content.</div>
          </div>

          <div>
            <div className="mp-field-label">Matched keywords ({report.data.matched_keywords.length})</div>
            <div className="mp-chips">
              {report.data.matched_keywords.length ? (
                report.data.matched_keywords.map((word) => (
                  <span className="mp-chip" key={word}>
                    {word}
                  </span>
                ))
              ) : (
                <span className="mp-inline-note">None matched yet.</span>
              )}
            </div>
          </div>

          <div>
            <div className="mp-field-label">Missing keywords ({report.data.missing_keywords.length})</div>
            <div className="mp-chips">
              {report.data.missing_keywords.length ? (
                report.data.missing_keywords.map((word) => (
                  <span className="mp-chip is-accent" key={word}>
                    {word}
                  </span>
                ))
              ) : (
                <span className="mp-inline-note">Nothing missing. Nice.</span>
              )}
            </div>
          </div>

          <div>
            <div className="mp-field-label">Suggestions</div>
            <ul className="mp-bullets">
              {report.data.suggestions.map((tip, index) => (
                <li key={index}>{tip}</li>
              ))}
            </ul>
          </div>
        </Modal>
      )}

      {/* Preview */}
      {preview && (
        <Modal title={preview.name} onClose={() => setPreview(null)} wide>
          <div className="mp-preview">
            <iframe src={preview.url} title={`Preview of ${preview.name}`} />
          </div>
        </Modal>
      )}

      {pendingDelete && (
        <ConfirmDialog
          title="Delete resume"
          message={`Remove "${pendingDelete.name}" from your library? The original uploaded file stays in Documents.`}
          busy={deleteBusy}
          onConfirm={remove}
          onClose={() => setPendingDelete(null)}
        />
      )}
    </>
  );
};

import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Download, Eye, FileText, Pencil, Trash2, Upload } from 'lucide-react';
import api from '../../services/api';
import {
  Card,
  ConfirmDialog,
  EMPTY,
  EmptyState,
  Loading,
  Modal,
  Pill,
} from '../../components/profile/ui';
import { FormGrid, SelectField, TextField } from '../../components/profile/forms';
import { errorMessage } from './useProfileData';
import type { DocumentRow, ProfileDocuments } from './types';

type Props = { notify: (message: string, tone?: 'success' | 'error') => void; onChanged: () => void };

const UPLOAD_TYPES = [
  { value: 'resume', label: 'Resume' },
  { value: 'transcript', label: 'Marksheet / Transcript' },
  { value: 'certificate', label: 'Certificate' },
  { value: 'other', label: 'Other' },
];

const prettySize = (bytes: number) => {
  if (!bytes) return EMPTY;
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

export const DocumentsTab: React.FC<Props> = ({ notify, onChanged }) => {
  const [docs, setDocs] = useState<ProfileDocuments | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);

  const [selected, setSelected] = useState<DocumentRow | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewType, setPreviewType] = useState<string>('');

  const [uploadOpen, setUploadOpen] = useState(false);
  const [uploadType, setUploadType] = useState('transcript');
  const [uploadLabel, setUploadLabel] = useState('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadBusy, setUploadBusy] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const [renaming, setRenaming] = useState<DocumentRow | null>(null);
  const [renameDraft, setRenameDraft] = useState('');
  const [renameBusy, setRenameBusy] = useState(false);
  const [renameError, setRenameError] = useState<string | null>(null);

  const [visibilityOpen, setVisibilityOpen] = useState(false);
  const [publicIds, setPublicIds] = useState<Set<string>>(new Set());
  const [visibilityBusy, setVisibilityBusy] = useState(false);

  const [pendingDelete, setPendingDelete] = useState<DocumentRow | null>(null);
  const [deleteBusy, setDeleteBusy] = useState(false);

  const fileInput = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get<ProfileDocuments>('/profile/documents');
      setDocs(data);
      setSelected((current) => {
        const all = [...data.resumes, ...data.marksheets, ...data.certificates, ...data.others];
        if (current) {
          const still = all.find((d) => d.id === current.id);
          if (still) return still;
        }
        return data.resumes[0] ?? all[0] ?? null;
      });
    } catch (error) {
      notify(errorMessage(error, 'Could not load your documents.'), 'error');
    } finally {
      setLoading(false);
    }
  }, [notify]);

  useEffect(() => {
    load();
  }, [load]);

  const allDocs = useMemo(
    () => (docs ? [...docs.resumes, ...docs.marksheets, ...docs.certificates, ...docs.others] : []),
    [docs],
  );

  // Fetch the selected document through axios so the auth header is applied,
  // then hand the blob to the iframe.
  useEffect(() => {
    let objectUrl: string | null = null;
    let cancelled = false;

    if (!selected) {
      setPreviewUrl(null);
      return;
    }

    api
      .get(`/profile/documents/${selected.id}/file`, { responseType: 'blob' })
      .then(({ data }) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(data as Blob);
        setPreviewType((data as Blob).type);
        setPreviewUrl(objectUrl);
      })
      .catch(() => {
        if (!cancelled) setPreviewUrl(null);
      });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [selected]);

  const upload = async () => {
    if (!uploadFile) {
      setUploadError('Choose a file to upload.');
      return;
    }
    setUploadBusy(true);
    setUploadError(null);
    try {
      const form = new FormData();
      form.append('file', uploadFile);
      form.append('doc_type', uploadType);
      const { data: doc } = await api.post('/documents/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const label = uploadLabel.trim();
      if (label) await api.put(`/profile/documents/${doc.id}/label`, { label });
      if (uploadType === 'resume') {
        await api.post('/profile/resumes', {
          name: label || uploadFile.name,
          source: 'existing',
          document_id: doc.id,
          status: 'ready',
        });
      }

      setUploadOpen(false);
      setUploadFile(null);
      setUploadLabel('');
      if (fileInput.current) fileInput.current.value = '';
      notify('Document uploaded');
      await load();
      onChanged();
    } catch (error) {
      setUploadError(errorMessage(error, 'Upload failed.'));
    } finally {
      setUploadBusy(false);
    }
  };

  const rename = async () => {
    if (!renaming) return;
    setRenameBusy(true);
    setRenameError(null);
    try {
      await api.put(`/profile/documents/${renaming.id}/label`, { label: renameDraft.trim() });
      setRenaming(null);
      notify('Document renamed');
      await load();
    } catch (error) {
      setRenameError(errorMessage(error));
    } finally {
      setRenameBusy(false);
    }
  };

  const download = async (doc: DocumentRow) => {
    setBusyId(doc.id);
    try {
      const { data } = await api.get(`/profile/documents/${doc.id}/file`, { responseType: 'blob' });
      const url = URL.createObjectURL(data as Blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = doc.filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (error) {
      notify(errorMessage(error, 'Download failed.'), 'error');
    } finally {
      setBusyId(null);
    }
  };

  const saveVisibility = async () => {
    if (!docs) return;
    setVisibilityBusy(true);
    try {
      const toPublic = allDocs.filter((d) => publicIds.has(d.id)).map((d) => d.id);
      const toPrivate = allDocs.filter((d) => !publicIds.has(d.id)).map((d) => d.id);
      if (toPublic.length) await api.put('/profile/documents/visibility', { document_ids: toPublic, is_public: true });
      if (toPrivate.length) await api.put('/profile/documents/visibility', { document_ids: toPrivate, is_public: false });
      setVisibilityOpen(false);
      notify('Public documents updated');
      await load();
    } catch (error) {
      notify(errorMessage(error), 'error');
    } finally {
      setVisibilityBusy(false);
    }
  };

  const remove = async () => {
    if (!pendingDelete) return;
    setDeleteBusy(true);
    try {
      await api.delete(`/documents/${pendingDelete.id}`);
      notify('Document deleted');
      if (selected?.id === pendingDelete.id) setSelected(null);
      await load();
      onChanged();
    } catch (error) {
      notify(errorMessage(error), 'error');
    } finally {
      setDeleteBusy(false);
      setPendingDelete(null);
    }
  };

  if (loading && !docs) return <Loading label="Loading your documents..." />;
  if (!docs) return null;

  const group = (title: string, rows: DocumentRow[]) => (
    <Card title={title} subtitle={`${rows.length} file${rows.length === 1 ? '' : 's'}`}>
      {rows.length === 0 ? (
        <p className="mp-inline-note">Nothing uploaded yet.</p>
      ) : (
        <div className="mp-doclist">
          {rows.map((doc) => (
            <div key={doc.id} className={`mp-doclist-item${selected?.id === doc.id ? ' is-active' : ''}`}>
              <FileText size={14} />
              <button className="mp-doclist-name" onClick={() => setSelected(doc)} title={doc.filename}>
                {doc.label}
              </button>
              {doc.is_public && selected?.id !== doc.id && <Pill tone="ready">Public</Pill>}
              <button
                className="mp-iconbtn is-plain"
                aria-label={`Rename ${doc.label}`}
                onClick={() => {
                  setRenaming(doc);
                  setRenameDraft(doc.label);
                  setRenameError(null);
                }}
              >
                <Pencil size={12} />
              </button>
              <button
                className="mp-iconbtn is-plain"
                aria-label={`Download ${doc.label}`}
                onClick={() => download(doc)}
                disabled={busyId === doc.id}
              >
                <Download size={12} />
              </button>
              <button className="mp-iconbtn is-danger" aria-label={`Delete ${doc.label}`} onClick={() => setPendingDelete(doc)}>
                <Trash2 size={12} />
              </button>
            </div>
          ))}
        </div>
      )}
    </Card>
  );

  return (
    <>
      <div className="mp-topbar" style={{ marginTop: '0.9rem', marginBottom: 0 }}>
        <span className="mp-inline-note">
          {docs.total} document{docs.total === 1 ? '' : 's'} stored
          {docs.primary_resume ? ` · primary resume: ${docs.primary_resume.name}` : ''}
        </span>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className="mp-btn mp-btn-ghost mp-btn-sm"
            onClick={() => {
              setPublicIds(new Set(allDocs.filter((d) => d.is_public).map((d) => d.id)));
              setVisibilityOpen(true);
            }}
          >
            Change public documents
          </button>
          <button className="mp-btn mp-btn-primary mp-btn-sm" onClick={() => setUploadOpen(true)}>
            <Upload size={13} /> Upload document
          </button>
        </div>
      </div>

      <div className="mp-grid">
        <div className="mp-col">
          <Card
            title={selected ? selected.label : 'Preview'}
            subtitle={selected ? `${selected.filename} · ${prettySize(selected.file_size)}` : undefined}
            actions={
              selected && (
                <button className="mp-btn mp-btn-ghost mp-btn-sm" onClick={() => download(selected)}>
                  <Download size={13} /> Download
                </button>
              )
            }
          >
            {!selected ? (
              <EmptyState
                title="No document selected"
                text="Upload a resume, marksheet or certificate to preview it here."
                actionLabel="Upload document"
                onAction={() => setUploadOpen(true)}
              />
            ) : !previewUrl ? (
              <Loading label="Loading preview..." />
            ) : previewType.startsWith('image/') ? (
              <div className="mp-preview" style={{ display: 'flex', justifyContent: 'center', padding: '1rem' }}>
                <img src={previewUrl} alt={selected.label} style={{ maxWidth: '100%', objectFit: 'contain' }} />
              </div>
            ) : (
              <div className="mp-preview">
                <iframe src={previewUrl} title={`Preview of ${selected.label}`} />
              </div>
            )}
            {selected && !previewType.startsWith('image/') && previewType !== 'application/pdf' && previewUrl && (
              <p className="mp-inline-note" style={{ marginTop: '0.6rem' }}>
                <Eye size={12} style={{ verticalAlign: -2 }} /> Inline preview may not render this file type — use
                Download to open it locally.
              </p>
            )}
          </Card>
        </div>

        <div className="mp-col">
          {group('Resumes', docs.resumes)}
          {group('Marksheets', docs.marksheets)}
          {group('Certificates', docs.certificates)}
          {group('Other Documents', docs.others)}
        </div>
      </div>

      {/* Upload */}
      {uploadOpen && (
        <Modal
          title="Upload Document"
          onClose={() => setUploadOpen(false)}
          onSubmit={upload}
          submitLabel="Upload"
          busy={uploadBusy}
          error={uploadError}
        >
          <FormGrid cols={1}>
            <div>
              <label className="mp-input-label">
                File <span className="mp-req">*</span>
              </label>
              <input
                ref={fileInput}
                className="mp-input"
                type="file"
                accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg"
                onChange={(e) => setUploadFile(e.target.files?.[0] ?? null)}
              />
              <div className="mp-hint">Max 10 MB.</div>
            </div>
            <SelectField
              label="Document type"
              value={uploadType}
              onChange={setUploadType}
              options={UPLOAD_TYPES}
              allowBlank={false}
              hint="Marksheets can be linked to individual semesters from the Education card."
            />
            <TextField
              label="Display name"
              value={uploadLabel}
              onChange={setUploadLabel}
              placeholder="e.g. 3rd year scorecard"
              hint="Optional — defaults to the file name."
            />
          </FormGrid>
        </Modal>
      )}

      {/* Rename */}
      {renaming && (
        <Modal title="Rename Document" onClose={() => setRenaming(null)} onSubmit={rename} busy={renameBusy} error={renameError}>
          <FormGrid cols={1}>
            <TextField label="Display name" value={renameDraft} onChange={setRenameDraft} required />
          </FormGrid>
        </Modal>
      )}

      {/* Public documents */}
      {visibilityOpen && (
        <Modal
          title="Change public documents"
          onClose={() => setVisibilityOpen(false)}
          onSubmit={saveVisibility}
          submitLabel="Save visibility"
          busy={visibilityBusy}
        >
          <p className="mp-inline-note">
            Public documents can be shared with recruiters alongside your profile. Everything else stays private to you.
          </p>
          {allDocs.length === 0 ? (
            <p className="mp-inline-note">No documents to configure yet.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
              {allDocs.map((doc) => (
                <label key={doc.id} className="mp-check">
                  <input
                    type="checkbox"
                    checked={publicIds.has(doc.id)}
                    onChange={(e) =>
                      setPublicIds((current) => {
                        const next = new Set(current);
                        if (e.target.checked) next.add(doc.id);
                        else next.delete(doc.id);
                        return next;
                      })
                    }
                  />
                  {doc.label}
                  <span className="mp-inline-note">({doc.doc_type})</span>
                </label>
              ))}
            </div>
          )}
        </Modal>
      )}

      {pendingDelete && (
        <ConfirmDialog
          title="Delete document"
          message={`Permanently delete "${pendingDelete.label}"? This also removes the stored file.`}
          busy={deleteBusy}
          onConfirm={remove}
          onClose={() => setPendingDelete(null)}
        />
      )}
    </>
  );
};

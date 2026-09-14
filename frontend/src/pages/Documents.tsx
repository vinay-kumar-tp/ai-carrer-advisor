import { useEffect, useRef, useState } from 'react';
import {
  FolderOpen, Upload, Trash2, FileText, Download, ExternalLink, Eye,
  Sparkles, Pencil, X, File as FileIcon,
} from 'lucide-react';
import api from '../services/api';
import '../styles/documents.css';
import { ToastHost, useToasts, Loading, EmptyState } from '../components/codequest/ui';
import { OptimizeModal } from './documents/OptimizeModal';

interface DocRow {
  id: string;
  filename: string;
  label: string;
  doc_type: string;
  type_label: string;
  file_size: number;
  is_public: boolean;
  has_text: boolean;
  created_at: string | null;
  download_url: string;
}

interface DocType { value: string; label: string; }

const prettySize = (b: number) => (!b ? '' : b < 1024 ? `${b} B` : b < 1048576 ? `${(b / 1024).toFixed(0)} KB` : `${(b / 1048576).toFixed(1)} MB`);

const GROUPS: { key: string; title: string; types: string[] }[] = [
  { key: 'resumes', title: 'Resumes', types: ['resume'] },
  { key: 'marksheets', title: 'Marksheets & Transcripts', types: ['transcript'] },
  { key: 'certificates', title: 'Certificates', types: ['certificate'] },
  { key: 'other', title: 'Other Documents', types: ['cover_letter', 'portfolio', 'project', 'id_proof', 'offer_letter', 'other'] },
];

export const DocumentsPage: React.FC = () => {
  const { toasts, push, dismiss } = useToasts();
  const [docs, setDocs] = useState<DocRow[]>([]);
  const [docTypes, setDocTypes] = useState<DocType[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<DocRow | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewMime, setPreviewMime] = useState('');

  const [uploadOpen, setUploadOpen] = useState(false);
  const [uType, setUType] = useState('resume');
  const [uLabel, setULabel] = useState('');
  const [uFile, setUFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const [renaming, setRenaming] = useState<DocRow | null>(null);
  const [renameDraft, setRenameDraft] = useState('');
  const [optimizeDoc, setOptimizeDoc] = useState<DocRow | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await api.get<DocRow[]>('/documents/');
      setDocs(data);
      setSelected((cur) => (cur ? data.find((d) => d.id === cur.id) ?? data[0] ?? null : data[0] ?? null));
    } catch {
      push('Could not load your documents.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    api.get<DocType[]>('/documents/doc-types').then(({ data }) => setDocTypes(data)).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch selected file as an authed blob for inline preview.
  useEffect(() => {
    let url: string | null = null;
    let cancelled = false;
    if (!selected) { setPreviewUrl(null); return; }
    setPreviewUrl(null);
    api.get(`/documents/${selected.id}/file`, { responseType: 'blob' })
      .then(({ data }) => {
        if (cancelled) return;
        url = URL.createObjectURL(data as Blob);
        setPreviewMime((data as Blob).type);
        setPreviewUrl(url);
      })
      .catch(() => { if (!cancelled) setPreviewUrl(null); });
    return () => { cancelled = true; if (url) URL.revokeObjectURL(url); };
  }, [selected]);

  const openInNewTab = async (doc: DocRow) => {
    try {
      const { data } = await api.get(`/documents/${doc.id}/file`, { responseType: 'blob' });
      const url = URL.createObjectURL(data as Blob);
      window.open(url, '_blank');
      // give the tab time to load before revoking
      setTimeout(() => URL.revokeObjectURL(url), 60000);
    } catch {
      push('Could not open the document.', 'error');
    }
  };

  const download = async (doc: DocRow) => {
    try {
      const { data } = await api.get(`/documents/${doc.id}/file`, { responseType: 'blob' });
      const url = URL.createObjectURL(data as Blob);
      const a = document.createElement('a');
      a.href = url; a.download = doc.filename;
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
    } catch {
      push('Download failed.', 'error');
    }
  };

  const doUpload = async () => {
    if (!uFile) { push('Choose a file first.', 'error'); return; }
    setUploading(true);
    try {
      const form = new FormData();
      form.append('file', uFile);
      form.append('doc_type', uType);
      form.append('label', uLabel.trim());
      await api.post('/documents/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } });
      setUploadOpen(false); setUFile(null); setULabel('');
      if (fileRef.current) fileRef.current.value = '';
      push('Document uploaded');
      await load();
    } catch (e: any) {
      push(e?.response?.data?.detail || 'Upload failed.', 'error');
    } finally {
      setUploading(false);
    }
  };

  const doRename = async () => {
    if (!renaming) return;
    try {
      await api.put(`/documents/${renaming.id}/label`, { label: renameDraft.trim() });
      setRenaming(null); push('Renamed'); await load();
    } catch { push('Rename failed.', 'error'); }
  };

  const remove = async (doc: DocRow) => {
    if (!window.confirm(`Delete "${doc.label}"? This removes the stored file.`)) return;
    try {
      await api.delete(`/documents/${doc.id}`);
      if (selected?.id === doc.id) setSelected(null);
      push('Document deleted'); await load();
    } catch { push('Delete failed.', 'error'); }
  };

  if (loading && docs.length === 0) return <Loading label="Loading your documents…" />;

  return (
    <div className="dv">
      <div className="dv-hero">
        <div>
          <h2>Document Vault</h2>
          <p>Store, preview and manage your resumes, marksheets, certificates and more. Optimize resumes for any job with AI.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setUploadOpen(true)}>
          <Upload size={15} /> Upload document
        </button>
      </div>

      {docs.length === 0 ? (
        <div className="glass-card">
          <EmptyState
            title="Your vault is empty"
            text="Upload a resume, marksheet or certificate to preview it here and unlock AI optimization."
            actionLabel="Upload document"
            onAction={() => setUploadOpen(true)}
          />
        </div>
      ) : (
        <div className="dv-grid">
          {/* Preview */}
          <div className="glass-card dv-preview-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div>
                <strong>{selected?.label || 'Preview'}</strong>
                {selected && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{selected.filename} · {prettySize(selected.file_size)}</div>}
              </div>
              {selected && (
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button className="btn btn-secondary" onClick={() => openInNewTab(selected)}><ExternalLink size={13} /> Open</button>
                  <button className="btn btn-secondary" onClick={() => download(selected)}><Download size={13} /> Download</button>
                </div>
              )}
            </div>
            {!selected ? (
              <div className="dv-preview-empty"><Eye size={28} /> Select a document to preview it.</div>
            ) : !previewUrl ? (
              <Loading label="Loading preview…" />
            ) : previewMime.startsWith('image/') ? (
              <div className="dv-preview"><img src={previewUrl} alt={selected.label} /></div>
            ) : previewMime === 'application/pdf' || selected.filename.toLowerCase().endsWith('.pdf') ? (
              <div className="dv-preview"><iframe src={previewUrl} title={selected.label} /></div>
            ) : (
              <div className="dv-preview-empty">
                <FileIcon size={28} />
                <div>Inline preview isn&apos;t available for this file type.</div>
                <button className="btn btn-primary" onClick={() => openInNewTab(selected)}><ExternalLink size={14} /> Open in new tab</button>
              </div>
            )}
          </div>

          {/* Groups */}
          <div>
            {GROUPS.map((g) => {
              const rows = docs.filter((d) => g.types.includes(d.doc_type));
              if (rows.length === 0) return null;
              return (
                <div className="dv-group" key={g.key}>
                  <div className="dv-group-title">{g.title} <span className="dv-group-count">({rows.length})</span></div>
                  {rows.map((doc) => (
                    <div key={doc.id} className={`dv-doc ${selected?.id === doc.id ? 'is-active' : ''}`} onClick={() => setSelected(doc)}>
                      <span className="dv-doc-icon"><FileText size={15} /></span>
                      <div className="dv-doc-body">
                        <div className="dv-doc-name" title={doc.filename}>
                          {doc.label} {doc.is_public && <span className="dv-badge">Public</span>}
                        </div>
                        <div className="dv-doc-meta">{doc.type_label} · {prettySize(doc.file_size)}</div>
                      </div>
                      <div className="dv-doc-actions" onClick={(e) => e.stopPropagation()}>
                        {doc.doc_type === 'resume' && (
                          <button className="dv-iconbtn opt" title="Optimize for a job" onClick={() => setOptimizeDoc(doc)}>
                            <Sparkles size={14} />
                          </button>
                        )}
                        <button className="dv-iconbtn" title="Open in new tab" onClick={() => openInNewTab(doc)}><ExternalLink size={14} /></button>
                        <button className="dv-iconbtn" title="Download" onClick={() => download(doc)}><Download size={14} /></button>
                        <button className="dv-iconbtn" title="Rename" onClick={() => { setRenaming(doc); setRenameDraft(doc.label); }}><Pencil size={13} /></button>
                        <button className="dv-iconbtn danger" title="Delete" onClick={() => remove(doc)}><Trash2 size={13} /></button>
                      </div>
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Upload modal */}
      {uploadOpen && (
        <div className="iv-modal-overlay" onClick={() => setUploadOpen(false)}>
          <div className="iv-modal" style={{ maxWidth: 480 }} onClick={(e) => e.stopPropagation()}>
            <button className="iv-modal-close" onClick={() => setUploadOpen(false)}><X size={16} /></button>
            <h2 style={{ marginTop: 0, fontSize: '1.25rem' }}>Upload Document</h2>

            <label className="label" style={{ fontSize: '0.8rem', fontWeight: 600 }}>Document name</label>
            <input className="input-field" placeholder="e.g. Vinay — Backend Resume" value={uLabel} onChange={(e) => setULabel(e.target.value)} style={{ marginBottom: '0.7rem' }} />

            <label className="label" style={{ fontSize: '0.8rem', fontWeight: 600 }}>Document type</label>
            <select className="input-field" value={uType} onChange={(e) => setUType(e.target.value)} style={{ marginBottom: '0.7rem' }}>
              {docTypes.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>

            <label className="label" style={{ fontSize: '0.8rem', fontWeight: 600 }}>File</label>
            <input ref={fileRef} className="input-field" type="file"
              accept=".pdf,.doc,.docx,.txt,.md,.rtf,.png,.jpg,.jpeg,.webp"
              onChange={(e) => setUFile(e.target.files?.[0] ?? null)} />
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
              PDF, DOC, DOCX, TXT or images · max 10 MB. Text-based resumes unlock AI optimization.
            </div>

            <div className="iv-modal-actions" style={{ marginTop: '1.25rem' }}>
              <button className="btn" onClick={() => setUploadOpen(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={doUpload} disabled={uploading}>
                {uploading ? 'Uploading…' : 'Upload'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Rename modal */}
      {renaming && (
        <div className="iv-modal-overlay" onClick={() => setRenaming(null)}>
          <div className="iv-modal" style={{ maxWidth: 420 }} onClick={(e) => e.stopPropagation()}>
            <button className="iv-modal-close" onClick={() => setRenaming(null)}><X size={16} /></button>
            <h2 style={{ marginTop: 0, fontSize: '1.15rem' }}>Rename document</h2>
            <input className="input-field" value={renameDraft} onChange={(e) => setRenameDraft(e.target.value)} />
            <div className="iv-modal-actions" style={{ marginTop: '1rem' }}>
              <button className="btn" onClick={() => setRenaming(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={doRename}>Save</button>
            </div>
          </div>
        </div>
      )}

      {optimizeDoc && (
        <OptimizeModal
          docId={optimizeDoc.id}
          docLabel={optimizeDoc.label}
          onClose={() => setOptimizeDoc(null)}
          notify={push}
        />
      )}

      <ToastHost toasts={toasts} onDismiss={dismiss} />
    </div>
  );
};

export default DocumentsPage;

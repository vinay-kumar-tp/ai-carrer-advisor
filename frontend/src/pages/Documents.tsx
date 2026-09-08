import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { FolderOpen, Upload, Trash2, FileText } from 'lucide-react';

export const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);
  const [docType, setDocType] = useState('resume');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const res = await api.get('/documents/');
      setDocuments(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);

    setUploading(true);
    try {
      await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      fetchDocuments();
    } catch (err) {
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/documents/${id}`);
      fetchDocuments();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2>Document Vault & Storage</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Secure storage for resumes, certificates, project files, and portfolio documents.</p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <select className="input-field" value={docType} onChange={(e) => setDocType(e.target.value)} style={{ width: '130px' }}>
            <option value="resume">Resume</option>
            <option value="certificate">Certificate</option>
            <option value="transcript">Transcript</option>
            <option value="other">Other</option>
          </select>

          <label className="btn btn-primary" style={{ cursor: 'pointer' }}>
            <Upload size={16} /> {uploading ? 'Uploading...' : 'Upload Document'}
            <input type="file" onChange={handleFileUpload} style={{ display: 'none' }} />
          </label>
        </div>
      </div>

      <div className="glass-card">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {documents.map((doc) => (
            <div key={doc.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem', background: 'rgba(10,13,20,0.5)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ padding: '0.6rem', borderRadius: '8px', background: 'rgba(99,102,241,0.15)', color: '#818cf8' }}>
                  <FileText size={20} />
                </div>
                <div>
                  <span style={{ fontWeight: 600, display: 'block' }}>{doc.filename}</span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Type: <strong style={{ textTransform: 'capitalize' }}>{doc.doc_type}</strong> • {(doc.file_size / 1024).toFixed(1)} KB
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <button onClick={() => handleDelete(doc.id)} style={{ background: 'none', border: 'none', color: '#f87171', cursor: 'pointer' }}>
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}

          {documents.length === 0 && (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              No documents uploaded yet. Upload your resume or certificates to enable ATS analysis.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

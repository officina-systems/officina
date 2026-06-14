import { useState, useEffect, useRef } from 'react';
import { selectDocuments, selectSearch } from '../data/selectors';

const FileIco = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--text-med)" strokeWidth="1.6">
    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
);

/* ── Panel de recursos ── */
export function KBPanel({ open, conversationId, folderId, onClose, t }) {
  const docs = [
    ...selectDocuments({ conversationId }),
    ...selectDocuments({ folderId }),
  ];
  return (
    <aside className={'kb-panel' + (open ? ' open' : '')}>
      <div className="kb-header">
        <span className="kb-sec-label">{t.resourcesPanel}</span>
        <button className="hdr-btn" onClick={onClose} aria-label={t.close}>×</button>
      </div>
      <div className="kb-list">
        {docs.length === 0 && (
          <p style={{ textAlign:'center', fontSize:12, color:'var(--text-lo)', padding:'28px 12px' }}>
            Sin documentos. Adjunta uno al chat.
          </p>
        )}
        {docs.map(d => (
          <div key={d.id} className="kb-item">
            <FileIco />
            <div style={{ minWidth:0 }}>
              <div className="kb-item-name" title={d.filename}>{d.filename}</div>
              <div className="kb-item-meta">
                {d.size_kb} KB · {d.status === 'pending' ? '⏳ procesando' : '✓ en el grafo'}
              </div>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}

/* ── Command palette ── */
export function CommandPalette({ open, onClose, onOpenConversation, t }) {
  const [q, setQ]   = useState('');
  const [idx, setIdx] = useState(0);
  const inputRef    = useRef(null);

  useEffect(() => { if (open) { setQ(''); setIdx(0); setTimeout(() => inputRef.current?.focus(), 40); } }, [open]);
  if (!open) return null;

  const r = selectSearch(q);
  const flat = [
    ...r.conversations.map(c => ({ kind: t.kindChat,      id: c.id, label: c.title })),
    ...r.workspaces.map(w =>    ({ kind: t.kindProject,  id: w.id, label: w.name  })),
    ...r.folders.map(f =>       ({ kind: t.kindFolder,   id: f.id, label: f.name  })),
    ...r.nodes.slice(0,4).map(n=>({ kind: t.kindNode,     id: n.id, label: n.name  })),
  ];

  const go = item => {
    if (item?.kind === 'chat') onOpenConversation(item.id);
    onClose();
  };

  return (
    <div className="palette-overlay" onClick={onClose}>
      <div className="palette-box" onClick={e => e.stopPropagation()}>
        <input ref={inputRef} className="palette-input"
          placeholder={t.paletteHint}
          value={q} onChange={e => { setQ(e.target.value); setIdx(0); }}
          onKeyDown={e => {
            if (e.key==='ArrowDown') { e.preventDefault(); setIdx(i => Math.min(i+1, flat.length-1)); }
            if (e.key==='ArrowUp')   { e.preventDefault(); setIdx(i => Math.max(i-1, 0)); }
            if (e.key==='Enter')     go(flat[idx]);
            if (e.key==='Escape')    onClose();
          }} />
        <div className="palette-results">
          {flat.length === 0 && (
            <p style={{ textAlign:'center', fontSize:13, color:'var(--text-lo)', padding:'32px 16px' }}>
              {q ? `Sin resultados para "${q}"` : 'Escribe para buscar…'}
            </p>
          )}
          {flat.map((item, i) => (
            <button key={item.kind+item.id}
              className={'palette-item' + (i===idx ? ' selected' : '')}
              onClick={() => go(item)} onMouseEnter={() => setIdx(i)}>
              <span className="palette-kind">{item.kind}</span>
              <span style={{ overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                {item.label}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

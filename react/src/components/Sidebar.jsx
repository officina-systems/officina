import { useState } from 'react';
import { selectWorkspaces, selectFolders, selectConversations,
         selectRecent, renameEntity } from '../data/selectors';

const Ico = {
  folder: <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>,
  chat:   <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>,
  plus:   <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 5v14M5 12h14"/></svg>,
  moon:   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>,
  config: <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>,
};

function EditableName({ value, kind, id, onRenamed, style = {} }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const commit = () => {
    setEditing(false);
    const v = draft.trim();
    if (v && v !== value) { renameEntity(kind, id, v); onRenamed(); }
    else setDraft(value);
  };
  if (editing) return (
    <input autoFocus className="rename-input" value={draft}
      onChange={e => setDraft(e.target.value)}
      onBlur={commit}
      onKeyDown={e => {
        if (e.key === 'Enter') commit();
        if (e.key === 'Escape') { setDraft(value); setEditing(false); }
      }}
      onClick={e => e.stopPropagation()} />
  );
  return (
    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis',
                   whiteSpace: 'nowrap', minWidth: 0, ...style }}
      title={value} onDoubleClick={e => { e.stopPropagation(); setEditing(true); }}>
      {value}
    </span>
  );
}

function Row({ children, active, indent = 0, onClick, onDot }) {
  return (
    <div className={'tree-row' + (active ? ' active' : '')}
      style={{ paddingLeft: 12 + indent * 14 }}
      onClick={onClick} role="button" tabIndex={0}
      onKeyDown={e => e.key === 'Enter' && onClick?.()}>
      {children}
      {onDot && (
        <button className="row-dot" title="editar"
          onClick={e => { e.stopPropagation(); onDot(); }}>●</button>
      )}
    </div>
  );
}

export default function Sidebar({ open, activeConvId, onOpenConversation,
                                  onNewChat, onEditContext, onToggleTheme,
                                  user, onRefreshed }) {
  const [collapsed, setCollapsed] = useState({});
  const toggle = (id) => setCollapsed(c => ({ ...c, [id]: !c[id] }));

  return (
    <aside className={'sidebar' + (open ? '' : ' collapsed')}>
      <div className="sidebar-logo">
        <button className="logo-text" onClick={onNewChat}>officina</button>
        <button className="hdr-btn" onClick={onToggleTheme} aria-label="tema">{Ico.moon}</button>
      </div>

      <nav className="sidebar-nav">
        <div className="sec-header">
          <span className="sec-label">PROYECTOS</span>
          <button className="hdr-btn" onClick={() => onEditContext({ kind: 'workspace', isNew: true })}
            aria-label="nuevo proyecto">{Ico.plus}</button>
        </div>

        {selectWorkspaces().map(w => {
          const folders   = selectFolders(w.id);
          const rootChats = selectConversations({ workspaceId: w.id });
          const open_w    = !collapsed[w.id];
          return (
            <div key={w.id}>
              <Row indent={0} onClick={() => toggle(w.id)}
                onDot={() => onEditContext({ kind: 'workspace', entity: w })}>
                <EditableName value={w.name} kind="workspace" id={w.id}
                  onRenamed={onRefreshed} style={{ fontWeight: 600, flex: 1 }} />
              </Row>
              {open_w && <>
                {folders.map(f => {
                  const open_f = !collapsed[f.id];
                  return (
                    <div key={f.id}>
                      <Row indent={1} onClick={() => toggle(f.id)}
                        onDot={() => onEditContext({ kind: 'folder', entity: f })}>
                        <span style={{ color: 'var(--text-med)', flexShrink: 0 }}>{Ico.folder}</span>
                        <EditableName value={f.name} kind="folder" id={f.id}
                          onRenamed={onRefreshed} style={{ flex: 1 }} />
                      </Row>
                      {open_f && selectConversations({ folderId: f.id }).map(c => (
                        <Row key={c.id} indent={2} active={c.id === activeConvId}
                          onClick={() => onOpenConversation(c.id)}
                          onDot={() => onEditContext({ kind: 'conversation', entity: c })}>
                          <span style={{ color: 'var(--text-lo)', flexShrink: 0 }}>{Ico.chat}</span>
                          <EditableName value={c.title} kind="conversation" id={c.id}
                            onRenamed={onRefreshed}
                            style={{ flex: 1, fontWeight: 300 }} />
                        </Row>
                      ))}
                    </div>
                  );
                })}
                {rootChats.map(c => (
                  <Row key={c.id} indent={1} active={c.id === activeConvId}
                    onClick={() => onOpenConversation(c.id)}
                    onDot={() => onEditContext({ kind: 'conversation', entity: c })}>
                    <span style={{ color: 'var(--text-lo)', flexShrink: 0 }}>{Ico.chat}</span>
                    <EditableName value={c.title} kind="conversation" id={c.id}
                      onRenamed={onRefreshed} style={{ flex: 1, fontWeight: 300 }} />
                  </Row>
                ))}
              </>}
            </div>
          );
        })}

        {/* RECIENTES — vista por updated_at */}
        <div className="sec-header" style={{ marginTop: 8 }}>
          <span className="sec-label">RECIENTES</span>
        </div>
        {selectRecent(5).map(c => (
          <Row key={'r-' + c.id} indent={1} active={c.id === activeConvId}
            onClick={() => onOpenConversation(c.id)}>
            <span style={{ color: 'var(--text-lo)', flexShrink: 0 }}>{Ico.chat}</span>
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis',
                           whiteSpace: 'nowrap', fontWeight: 300 }}>{c.title}</span>
          </Row>
        ))}
      </nav>

      {/* Footer — coordenada USER */}
      <div className="sidebar-footer">
        <button style={{ display: 'flex', alignItems: 'center', gap: 10,
                         background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
          onClick={() => onEditContext({ kind: 'system' })}>
          <div className="avatar">{user.initials}</div>
          <span className="username">{user.name}</span>
        </button>
        <button className="hdr-btn" style={{ marginLeft: 'auto' }}
          onClick={() => onEditContext({ kind: 'system' })}
          aria-label="configuración">{Ico.config}</button>
      </div>
    </aside>
  );
}

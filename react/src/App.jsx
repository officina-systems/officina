import { useState, useEffect, useCallback, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import Composer from './components/Composer';
import { KBPanel, CommandPalette } from './components/Panels';
import { selectMessages, selectPath, selectUser,
         selectMirrorNode, appendMessage, createConversation,
         deactivateEntity, updateMirrorFD } from './data/selectors';
import { openTurn } from './data/turn';

const Ico = {
  search: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>,
  kb:     <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>,
  menu:   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><path d="M9 18l6-6-6-6"/></svg>,
};

const emptyTurn = { active:false, phase:null, streamText:'', toolEvents:[] };

export default function App() {
  const [activeConvId, setActiveConvId] = useState(null);
  const [turn, setTurn]           = useState(emptyTurn);
  const [sideOpen, setSideOpen]   = useState(true);
  const [kbOpen, setKbOpen]       = useState(false);
  const [paletteOpen, setPalette] = useState(false);
  const [toast, setToast]         = useState(null);
  const [editCtx, setEditCtx]     = useState(null);
  const [seedText, setSeed]       = useState('');
  const [, forceRender]           = useState(0);
  const refresh   = useCallback(() => forceRender(n => n+1), []);
  const turnRef   = useRef(null);

  const user     = selectUser();
  const messages = activeConvId ? selectMessages(activeConvId) : [];
  const path     = activeConvId ? selectPath(activeConvId) : [];

  const showToast = msg => { setToast(msg); setTimeout(() => setToast(null), 2800); };

  /* Atajos B.7 */
  useEffect(() => {
    const fn = e => {
      if ((e.ctrlKey||e.metaKey) && e.key==='k') { e.preventDefault(); setPalette(true); }
      if ((e.ctrlKey||e.metaKey) && e.key==='b') { e.preventDefault(); setSideOpen(s=>!s); }
      if ((e.ctrlKey||e.metaKey) && e.key==='i') { e.preventDefault(); setKbOpen(k=>!k); }
      if (e.key==='Escape') {
        if (paletteOpen) setPalette(false);
        else if (editCtx) setEditCtx(null);
        else if (kbOpen)  setKbOpen(false);
      }
    };
    window.addEventListener('keydown', fn);
    return () => window.removeEventListener('keydown', fn);
  }, [paletteOpen, kbOpen, editCtx]);

  /* Eventos del turno — misma interfaz que el WS canónico */
  const handleEvent = useCallback((ev, convId) => {
    if (ev.type==='system' && ev.phase) {
      setTurn(t => ({ ...t, phase: ev.phase }));
    } else if (ev.type==='tool_event') {
      setTurn(t => ({ ...t, phase:'reasoning',
        toolEvents: [...t.toolEvents, ev] }));
    } else if (ev.type==='token') {
      setTurn(t => ({ ...t, phase:'streaming',
        streamText: t.streamText + ev.content }));
    } else if (ev.type==='done') {
      setTurn(t => {
        const content = t.streamText || (ev.stopped ? '_Generación cancelada._' : '');
        if (content) appendMessage(convId, {
          id: ev.message_id ?? 'm-'+Date.now(), role:'assistant',
          content, model_used: ev.model_used ?? 'simulador',
          created_at: new Date().toISOString(),
        });
        return emptyTurn;
      });
      refresh();
    } else if (ev.type==='agent_event') {
      showToast('✓ Sleep Agent — turno cristalizado');
    }
  }, [refresh]);

  /* Envío principal */
  const handleSend = (content, attachments, modelGroup) => {
    if (editCtx) { handleEditTurn(content); return; }
    let convId = activeConvId;
    if (!convId) {
      const c = createConversation({ userId: user.id,
        title: content.slice(0,42) || 'Nuevo chat', modelGroup });
      convId = c.id;
      setActiveConvId(convId);
    }
    appendMessage(convId, {
      id:'m-'+Date.now(), role:'user', user_id: user.id,
      content: content || `📎 ${attachments.map(a=>a.name).join(', ')}`,
      created_at: new Date().toISOString(),
    });
    refresh();
    setTurn({ ...emptyTurn, active:true, phase:'retrieving' });
    turnRef.current = openTurn(convId, { onEvent: ev => handleEvent(ev, convId) });
    turnRef.current.send(content);
  };

  /* Chat-driven edit (B.6, D2) */
  const handleEditTurn = content => {
    const { kind, entity, pendingDelete } = editCtx;
    const yes = /^(si|sí|confirmo|confirmado|procede|ok)\b/i.test(content.trim());
    if (pendingDelete) {
      if (yes) {
        deactivateEntity(kind, entity.id);
        if (kind==='conversation' && entity.id===activeConvId) setActiveConvId(null);
        showToast(`Desactivado: ${entity.name ?? entity.title} — recuperable.`);
        setEditCtx(null); refresh();
      } else {
        showToast('Cancelado.'); setEditCtx(null);
      }
      return;
    }
    if (/^(elimina|borra|desactiva)/i.test(content.trim())) {
      setEditCtx(c => ({ ...c, pendingDelete:true }));
      showToast(`¿Confirmas desactivar "${entity.name ?? entity.title}"? Responde "sí".`);
      return;
    }
    if (entity && content.trim()) {
      const node = selectMirrorNode(entity.id);
      const fd = node
        ? node.functional_definition.replace(/\[OPERATION\][^[]*/,
            `[OPERATION] ${content.trim()} `)
        : `[IDENTITY] ${entity.name ?? entity.title}. [OPERATION] ${content.trim()}`;
      updateMirrorFD(entity.id, fd);
      showToast('Instrucciones actualizadas en el nodo espejo.');
      setEditCtx(null); refresh();
    }
  };

  const startEdit = ctx => {
    setEditCtx(ctx);
    if (ctx.kind==='system')
      showToast('Configuración: describe el cambio en el chat.');
    else
      showToast(`Editando ${ctx.entity?.name ?? ctx.entity?.title ?? 'nuevo'}: escribe instrucciones o "desactiva".`);
  };

  const folderId = path.find(p => p.workspace_id)?.id;

  return (
    <div className="app">
      <Sidebar open={sideOpen} activeConvId={activeConvId} user={user}
        onOpenConversation={id => { setActiveConvId(id); setEditCtx(null); }}
        onNewChat={() => { setActiveConvId(null); setEditCtx(null); setTurn(emptyTurn); }}
        onEditContext={startEdit}
        onToggleTheme={() => document.body.classList.toggle('light')}
        onRefreshed={refresh} />

      <main className="app-main">
        {/* Header */}
        <header className="app-header">
          <div style={{ display:'flex', alignItems:'center', gap:8, minWidth:0 }}>
            <button className={'hdr-btn' + (sideOpen ? ' active' : '')} onClick={() => setSideOpen(s => !s)}
              aria-label={sideOpen ? 'cerrar sidebar' : 'abrir sidebar'} title="Ctrl+B">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <path d={sideOpen ? 'M15 18l-6-6 6-6' : 'M9 18l6-6-6-6'} />
              </svg>
            </button>
            {editCtx ? (
              <div className="edit-banner">
                <span>✎ Editando · {editCtx.entity?.name ?? editCtx.entity?.title ?? editCtx.kind}</span>
                <button onClick={() => setEditCtx(null)} aria-label="salir">✕</button>
              </div>
            ) : path.length ? (
              <nav className="breadcrumb" aria-label="ruta">
                {path.map((p, i) => (
                  <span key={p.id} style={{ display:'flex', alignItems:'center', gap:6, minWidth:0 }}>
                    {i > 0 && <span className="bc-sep">/</span>}
                    <span className="bc-item"
                      style={{ fontWeight: [700,400,300][i] }}>
                      {p.name ?? p.title}
                    </span>
                  </span>
                ))}
              </nav>
            ) : (
              <span style={{ fontSize:13, color:'var(--oro)' }}>Nuevo chat</span>
            )}
          </div>
          <div style={{ display:'flex', gap:4 }}>
            <button className="hdr-btn" onClick={() => setPalette(true)}
              aria-label="buscar (Ctrl+K)" title="Ctrl+K">{Ico.search}</button>
            <button className={'hdr-btn' + (kbOpen ? ' active' : '')}
              onClick={() => setKbOpen(k=>!k)}
              aria-label="recursos (Ctrl+I)" title="Ctrl+I">{Ico.kb}</button>
          </div>
        </header>

        <ChatArea messages={messages} turn={turn}
          onPickRecent={id => { setActiveConvId(id); setEditCtx(null); }}
          onCrystallize={() => showToast('cristalizar → elemento 10 del runtime')}
          onEditMessage={t => setSeed(t)} />

        <Composer onSend={handleSend} onStop={() => turnRef.current?.stop()}
          generating={turn.active} seedText={seedText} />
      </main>

      <KBPanel open={kbOpen} onClose={() => setKbOpen(false)}
        conversationId={activeConvId} folderId={folderId} />

      <CommandPalette open={paletteOpen} onClose={() => setPalette(false)}
        onOpenConversation={id => { setActiveConvId(id); setEditCtx(null); }} />

      {toast && <div className="toast fade-in" role="status">{toast}</div>}
    </div>
  );
}

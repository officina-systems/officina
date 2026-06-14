import { useEffect, useRef } from 'react';
import Markdown from './Markdown';
import { selectRecent } from '../data/selectors';

const fmt = iso => new Date(iso).toLocaleTimeString('es',{ hour:'2-digit', minute:'2-digit' });

export default function ChatArea({ messages, turn, onPickRecent, onCrystallize, onEditMessage, t }) {
  const scrollerRef = useRef(null);
  const endRef      = useRef(null);
  const stick       = useRef(true);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    const fn = () => { stick.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80; };
    el.addEventListener('scroll', fn);
    return () => el.removeEventListener('scroll', fn);
  }, []);

  useEffect(() => {
    if (stick.current) endRef.current?.scrollIntoView({ behavior: 'instant' });
  }, [messages, turn.streamText]);

  const copy = txt => navigator.clipboard.writeText(txt);

  /* Empty state */
  if (!messages.length && !turn.active) {
    return (
      <div className="empty-state fade-in">
        <div className="empty-logo">officina</div>
        <div className="empty-title">{t.emptyTitle}</div>
        <div className="empty-chips">
          {selectRecent(3).map(c => (
            <button key={c.id} className="empty-chip" onClick={() => onPickRecent(c.id)}>
              {t.continueLabel} {c.title}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="chat-scroller" ref={scrollerRef} aria-live="polite">
      <div className="chat-inner">
        {messages.map(m => m.role === 'user' ? (
          <div key={m.id} className="msg-user fade-in">
            <div className="bubble">{m.content}</div>
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <div className="msg-actions">
                <button onClick={() => copy(m.content)}>copiar</button>
                <button onClick={() => onEditMessage(m.content)}>editar</button>
              </div>
              <span className="msg-meta">{fmt(m.created_at)}</span>
            </div>
          </div>
        ) : (
          <div key={m.id} className="msg-ai fade-in">
            <Markdown content={m.content} />
            <div style={{ display:'flex', alignItems:'center', gap:8 }}>
              <div className="msg-actions">
                <button onClick={() => copy(m.content)}>copiar</button>
                <button onClick={() => onCrystallize(m)}>{t.crystallize}</button>
                <button>reintentar</button>
              </div>
              {m.model_used && <span className="msg-meta">{m.model_used}</span>}
            </div>
          </div>
        ))}

        {/* Estados del turno B.5 */}
        {turn.active && (
          <div className="fade-in">
            {turn.phase === 'retrieving' && (
              <p className="turn-phase">consultando el grafo…</p>
            )}
            {turn.toolEvents.length > 0 && (
              <details className="turn-tools">
                <summary>{turn.toolEvents.length} tool call{turn.toolEvents.length > 1 ? 's' : ''} T2 ▸</summary>
                {turn.toolEvents.map((t, i) => (
                  <div key={i} className="tool-line">→ {t.tool}({JSON.stringify(t.args)})</div>
                ))}
              </details>
            )}
            {turn.streamText && <Markdown content={turn.streamText} streaming />}
          </div>
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}

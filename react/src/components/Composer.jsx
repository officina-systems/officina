import { useState, useRef, useEffect } from 'react';
import { selectModels } from '../data/selectors';

const Ico = {
  attach: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14"/></svg>,
  mic:    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2M12 19v4M8 23h8"/></svg>,
  send:   <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--oro)" strokeWidth="3"><path d="M12 19V5M5 12l7-7 7 7"/></svg>,
  stop:   <svg width="12" height="12" viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2" fill="var(--oro)"/></svg>,
};

export default function Composer({ onSend, onStop, generating, seedText = '' }) {
  const [text, setText]         = useState('');
  const [attachments, setAtts]  = useState([]);
  const [model, setModel]       = useState(selectModels()[0]);
  const [modelMenu, setMenu]    = useState(false);
  const [recording, setRec]     = useState(false);
  const taRef  = useRef(null);
  const recRef = useRef(null);
  const models = selectModels();

  /* Seed desde "editar mensaje" */
  useEffect(() => { if (seedText) { setText(seedText); taRef.current?.focus(); } }, [seedText]);

  /* Auto-resize textarea */
  useEffect(() => {
    const ta = taRef.current; if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 220) + 'px';
  }, [text]);

  const send = () => {
    if (generating) { onStop(); return; }
    if (!text.trim() && !attachments.length) return;
    onSend(text.trim(), attachments, model);
    setText(''); setAtts([]);
  };

  const addFiles = files => {
    setAtts(a => [...a, ...[...files].map(f => ({
      name: f.name, size_kb: (f.size/1024).toFixed(1), file: f,
    }))]);
  };

  const toggleVoice = () => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) return;
    if (recording) { recRef.current?.stop(); setRec(false); return; }
    const rec = new SR();
    rec.lang = 'es-ES'; rec.continuous = true; rec.interimResults = true;
    let base = text;
    rec.onresult = e => {
      let final = '', interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const t = e.results[i][0].transcript;
        e.results[i].isFinal ? (final += t + ' ') : (interim += t);
      }
      if (final) base += final;
      setText(base + interim);
    };
    rec.onend = () => setRec(false);
    rec.onerror = () => setRec(false);
    rec.start(); recRef.current = rec; setRec(true);
  };

  return (
    <div className="composer-wrap">
      <div className="composer-box"
        onDragOver={e => e.preventDefault()}
        onDrop={e => { e.preventDefault(); addFiles(e.dataTransfer.files); }}>

        {attachments.length > 0 && (
          <div className="composer-chips">
            {attachments.map((a, i) => (
              <div key={i} className="composer-chip">
                <span style={{ maxWidth:160, overflow:'hidden', textOverflow:'ellipsis',
                               whiteSpace:'nowrap' }}>{a.name}</span>
                <span style={{ color:'var(--text-lo)' }}>{a.size_kb} KB</span>
                <button onClick={() => setAtts(at => at.filter((_, j) => j !== i))}
                  aria-label={`quitar ${a.name}`}>×</button>
              </div>
            ))}
          </div>
        )}

        <textarea ref={taRef} rows={1} value={text}
          className="composer-ta"
          placeholder="Escribe o habla…"
          aria-label="mensaje"
          onChange={e => setText(e.target.value)}
          onPaste={e => {
            const fs = [...e.clipboardData.items]
              .filter(i => i.kind === 'file').map(i => i.getAsFile());
            if (fs.length) addFiles(fs);
          }}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }}} />

        <div className="composer-actions">
          <button className="c-btn" aria-label="adjuntar"
            onClick={() => { const i = document.createElement('input');
              i.type='file'; i.multiple=true; i.onchange=e=>addFiles(e.target.files); i.click(); }}>
            {Ico.attach}
          </button>

          <button className={'c-btn' + (recording ? ' active voice-pulse' : '')}
            onClick={toggleVoice} aria-label={recording ? 'detener dictado' : 'dictar'}>
            {Ico.mic}
          </button>

          {/* Selector de modelo */}
          <div style={{ position: 'relative' }}>
            <button className="model-btn" onClick={() => setMenu(m => !m)} aria-haspopup="menu">
              {model} ▾
            </button>
            {modelMenu && (
              <div className="model-menu" role="menu">
                {models.map(m => (
                  <button key={m} role="menuitem"
                    className={'model-item' + (m === model ? ' selected' : '')}
                    onClick={() => { setModel(m); setMenu(false); }}>
                    {m}
                  </button>
                ))}
              </div>
            )}
          </div>

          <button className="send-btn" onClick={send}
            aria-label={generating ? 'detener' : 'enviar'}>
            {generating ? Ico.stop : Ico.send}
          </button>
        </div>
      </div>
    </div>
  );
}

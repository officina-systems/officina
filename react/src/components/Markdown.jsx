import { useMemo, useEffect, useRef } from 'react';
import { marked } from 'marked';

marked.setOptions({ breaks: true, gfm: true });

// Render markdown del asistente (B.2) — code blocks con copiar.
export default function Markdown({ content, streaming }) {
  const ref = useRef(null);
  const html = useMemo(() => marked.parse(content || ''), [content]);

  // Botón copiar en cada <pre> (no durante streaming para evitar churn)
  useEffect(() => {
    if (streaming || !ref.current) return;
    ref.current.querySelectorAll('pre').forEach(pre => {
      if (pre.querySelector('.copy-btn')) return;
      const btn = document.createElement('button');
      btn.className = 'copy-btn absolute top-2 right-2 text-[11px] px-2 py-0.5 rounded-md cursor-pointer';
      btn.style.cssText = 'color:var(--text-lo);background:var(--bg-hover)';
      btn.textContent = 'copiar';
      btn.onclick = () => {
        navigator.clipboard.writeText(pre.querySelector('code')?.innerText ?? '');
        btn.textContent = 'copiado';
        setTimeout(() => (btn.textContent = 'copiar'), 1500);
      };
      pre.appendChild(btn);
    });
  }, [html, streaming]);

  return (
    <div
      ref={ref}
      className={`md ${streaming ? 'stream-cursor' : ''}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

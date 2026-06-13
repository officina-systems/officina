# OFFICINA UI v3 — Integración a react/

## Contenido
src/data/      → F1: SESSION (espejo schema session) + GRAPH (espejo nodes/edges)
                 + selectors/mutations (endpoints canónicos comentados)
                 + turn.js (simulador con interfaz idéntica al WS canónico)
src/components/→ Sidebar (rename inline D2), ChatArea (B.2+B.5),
                 Composer (B.4), Panels (KB + CommandPalette)
src/App.jsx    → layout 3 zonas, estado del turno, chat-driven (B.6), atajos (B.7)
src/index.css  → tokens v3 (dark/light), markdown, focus, reduced-motion

## Integración (PowerShell, desde officina/)
# Opción A — reemplazar el src del skeleton existente:
#   1. backup: Rename-Item react\src react\src-skeleton-bak
#   2. copiar src/, index.html, vite.config.js del paquete a react\
#   3. cd react; npm install marked @tailwindcss/vite tailwindcss
#   4. npm run dev   → http://localhost:5173

## DECs aplicadas (revocables)
D1 Inter cuerpo de mensajes / Nunito chrome · D2 cero modales
D3 tool_event soportado en UI · D4 SESSION.users + user_id propagado

## F7 — cutover a FastAPI (cuando S35 cierre)
- selectors.js: reemplazar cuerpos por fetch a los endpoints comentados
- turn.js: reemplazar openTurn por WebSocket /ws/{conversation_id}
  (los handlers de App.jsx no cambian — misma interfaz de eventos)

## Fuera de alcance F1-F6 (anotado)
- Búsqueda dentro del chat (la tenía el mockup vanilla) → F-posterior
- Preview de documentos en panel → cuando Document Agent sirva contenido

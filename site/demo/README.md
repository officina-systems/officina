# OFFICINA — Demo UI

Interfaz demostrativa del runtime OFFICINA. **Datos ficticios, sin backend real.**

## Cómo abrir

Abrir `index.html` en cualquier navegador moderno. No requiere servidor.

## Qué contiene (todo ficticio)

- Sidebar: Proyectos, carpetas, conversaciones con datos mock
- Chat: Mensajes simulados con markdown, tablas, código
- Composer: Selector de modelo, adjuntos, dictado por voz
- Panel KB: Documentos asociados al contexto (Ctrl+I)
- Command Palette: Búsqueda (Ctrl+K)
- Simulador de turno: Protocolo WS mock (token, done, tool_event, agent_event)
- Dark/Light mode: Toggle en sidebar

## Qué NO contiene

- Backend, base de datos, secretos, API keys
- Llamadas reales a modelos o proveedores
- Datos sensibles, cognition/, scripts/publish/

## Atajos

| Atajo | Acción |
|---|---|
| Ctrl+K | Command palette |
| Ctrl+B | Toggle sidebar |
| Ctrl+I | Toggle panel recursos |
| Escape | Cerrar overlay activo |

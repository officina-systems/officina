DEFAULT_SYSTEM_INSTRUCTION = """
Eres OFFICINA runtime.

Responde usando el contexto operacional disponible.
Si el contexto es insuficiente, dilo explícitamente.
No inventes hechos operacionales.

Prioridad de contexto:
1. Si la tarea pregunta por documentos, archivos adjuntos, documentos procesados o contenido documental, usa primero <session_documents>.
2. Si la tarea pregunta por continuidad conversacional, usa <episodic_memory> y el historial.
3. Si la tarea pregunta por reglas, configuración o gobernanza operacional, usa <knowledge_context>.
""".strip()


def _node_block(node: dict) -> str:
    name = node.get("name", "")
    node_type = node.get("node_type", "")
    contextual_type = node.get("contextual_type", "")
    fd = node.get("functional_definition", "")

    label = node_type
    if contextual_type:
        label = f"{node_type}/{contextual_type}"

    return f"### {name} [{label}]\n{fd}".strip()


def assemble_prompt(
    retrieval_result: dict,
    original_message: str,
    clarified_message: str,
    system_instruction: str | None = None,
    session_documents: list[str] | None = None,
    history: list[dict] | None = None,
) -> list[dict]:
    system_text = (system_instruction or DEFAULT_SYSTEM_INSTRUCTION).strip()

    final_nodes = retrieval_result.get("final_nodes", []) or []

    knowledge_nodes = []
    episodic_nodes = []

    for node in final_nodes:
        if node.get("contextual_type") == "episodic":
            episodic_nodes.append(node)
        else:
            knowledge_nodes.append(node)

    knowledge_context = "\n\n".join(_node_block(node) for node in knowledge_nodes).strip()
    episodic_memory = "\n\n".join(_node_block(node) for node in episodic_nodes).strip()
    session_docs = "\n\n".join(session_documents or []).strip()

    user_task = f"""
<knowledge_context>
{knowledge_context or "NO_KNOWLEDGE_CONTEXT"}
</knowledge_context>

<episodic_memory>
{episodic_memory or "NO_EPISODIC_MEMORY"}
</episodic_memory>

<session_documents>
{session_docs or "NO_SESSION_DOCUMENTS"}
</session_documents>

<task>
Original: {original_message}
Clarified: {clarified_message}
</task>
""".strip()

    messages = [{"role": "system", "content": system_text}]

    for item in history or []:
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_task})

    return messages

"""
Officina — MCP server de PostgreSQL.

Implementacion del MCP propio definido en DEC-016 con stack Python/FastMCP
(DEC-017). Expone operaciones contra la DB de Officina, con superficie
minima y validacion de inputs.

Operaciones:
    Inserciones (Metodo: decisions/pendientes):
        1. insertar_decision
        2. insertar_pendiente
    Cambios de estado (Metodo: decisions/pendientes):
        3. cambiar_estado_decision
        4. cambiar_estado_pendiente
    Actualizaciones selectivas con whitelist (Metodo: decisions/pendientes):
        5. actualizar_campos_decision
        6. actualizar_campos_pendiente
    Inserciones (Diccionario / Relaciones — DEC-086):
        7. insertar_termino
        8. insertar_relacion
    Actualizaciones selectivas con whitelist (Diccionario):
        9. actualizar_campos_termino
    Eliminacion (Relaciones — para calibracion iterativa):
        10. eliminar_relacion
    Lectura:
        11. query_select   (solo SELECT, validado con sqlglot)

Conexion: TCP a localhost:5433, DB officina, usuario officina_admin.
Password: leida desde el .env de Postgres siguiendo Principio X (DEC-018).
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Any

import psycopg
import sqlglot
from dotenv import load_dotenv
from fastmcp import FastMCP


# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------

# Ruta canonica del .env de Postgres. El .env es la copia de trabajo de la
# password que vive en Bitwarden (DEC-003, DEC-009, Principio X / DEC-018).
ENV_PATH = Path(r"C:\Users\Home\officina\.env")

# Defaults heredados de la imagen postgres:16-alpine y DEC-010.
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "officina"
DB_USER = "officina"

# Whitelist de campos editables via actualizar_campos_decision.
# Excluye campos auto-gestionados (codigo, fecha, proyecto, creada_en,
# actualizada_en) y de flujo propio (estado: usar cambiar_estado_decision).
DECISION_WHITELIST: frozenset[str] = frozenset({
    "titulo",
    "decision",
    "contexto",
    "razon",
    "implicaciones",
    "superada_por",
})

# Whitelist de campos editables via actualizar_campos_pendiente.
# Excluye id (autogenerado), proyecto, creada_en, actualizada_en, cerrada_en
# y estado (usar cambiar_estado_pendiente).
PENDIENTE_WHITELIST: frozenset[str] = frozenset({
    "titulo",
    "descripcion",
    "prioridad",
    "proximo_paso",
    "bloqueado_por",
})

# Whitelist de campos editables via actualizar_campos_termino.
# Excluye 'termino' (PK; renombrar requiere CASCADE de relaciones, no
# es operacion de calibracion estandar).
TERMINO_WHITELIST: frozenset[str] = frozenset({
    "tipo",
    "mapa",
    "flujo",
    "referencia",
    "forma",
    "definicion_funcional",
})

# Valores permitidos en columnas con CHECK (replicados aqui para validar
# antes de tocar la DB y dar mensajes claros).
TIPOS_VALIDOS: frozenset[str] = frozenset({"C", "M", "P"})
FORMAS_VALIDAS: frozenset[str] = frozenset({
    "rectangulo", "rombo", "cilindro", "ovalo",
    "paralelogramo", "documento", "circulo",
})
TIPOS_RELACION_VALIDOS: frozenset[str] = frozenset({
    "pertenece_a", "depende_de",
})


# ---------------------------------------------------------------------------
# Conexion a Postgres
# ---------------------------------------------------------------------------

def _load_password() -> str:
    """Carga POSTGRES_PASSWORD desde el .env. Falla con mensaje claro si no esta."""
    if not ENV_PATH.exists():
        raise RuntimeError(
            f"No existe el .env esperado en {ENV_PATH}. "
            "El MCP requiere la copia de trabajo de la password "
            "(Principio X: Bitwarden es fuente, .env es copia)."
        )
    load_dotenv(ENV_PATH)
    pwd = os.environ.get("POSTGRES_PASSWORD")
    if not pwd:
        raise RuntimeError(
            f"El .env existe pero no contiene POSTGRES_PASSWORD: {ENV_PATH}. "
            "Regenerar el .env desde Bitwarden con el patron canonico de "
            "referencias-bitwarden.md."
        )
    return pwd


def _conninfo() -> str:
    """Construye el connection string para psycopg."""
    pwd = _load_password()
    return (
        f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
        f"user={DB_USER} password={pwd}"
    )


def _connect() -> psycopg.Connection:
    """Abre una conexion nueva. Cada operacion abre y cierra la suya.

    Justificacion: el MCP es de bajo trafico (operaciones manuales del
    usuario via Claude Desktop). No vale la complejidad de un pool. Si en
    el futuro se observa latencia, se puede migrar a psycopg_pool.
    """
    return psycopg.connect(_conninfo())


# ---------------------------------------------------------------------------
# Validador de query_select
# ---------------------------------------------------------------------------

def _validate_select_only(sql: str) -> None:
    """Valida que el SQL sea exactamente un SELECT (no multi-statement,
    no DML, no DDL). Lanza ValueError con mensaje claro si no cumple.
    """
    if not sql or not sql.strip():
        raise ValueError("SQL vacio.")

    try:
        statements = sqlglot.parse(sql, dialect="postgres")
    except sqlglot.errors.ParseError as e:
        raise ValueError(f"SQL invalido: {e}") from e

    # Filtrar None que sqlglot inserta para statements vacios entre ;
    statements = [s for s in statements if s is not None]

    if len(statements) == 0:
        raise ValueError("SQL vacio o solo comentarios.")

    if len(statements) > 1:
        raise ValueError(
            f"query_select solo acepta UN statement; recibidos: {len(statements)}."
        )

    stmt = statements[0]
    # sqlglot etiqueta el tipo del statement raiz. Permitimos solo SELECT.
    # Tambien aceptamos UNION/EXCEPT/INTERSECT que son operaciones de SELECTs.
    allowed_types = {"Select", "Union", "Except", "Intersect"}
    stmt_type = type(stmt).__name__
    if stmt_type not in allowed_types:
        raise ValueError(
            f"query_select solo acepta SELECT (o UNION/EXCEPT/INTERSECT). "
            f"Recibido: {stmt_type}."
        )


# ---------------------------------------------------------------------------
# Helpers comunes
# ---------------------------------------------------------------------------

def _row_to_dict(cursor: psycopg.Cursor, row: tuple) -> dict[str, Any]:
    """Convierte una fila tupla a dict usando description del cursor."""
    return {desc.name: val for desc, val in zip(cursor.description, row)}


def _format_date(value: Any) -> Any:
    """Convierte date/datetime a ISO string para JSON. Otros tipos se
    devuelven tal cual.
    """
    if isinstance(value, date):
        return value.isoformat()
    return value


def _serialize_row(row_dict: dict[str, Any]) -> dict[str, Any]:
    """Aplica _format_date a todos los valores de un dict."""
    return {k: _format_date(v) for k, v in row_dict.items()}


# ---------------------------------------------------------------------------
# MCP server + operaciones
# ---------------------------------------------------------------------------

mcp = FastMCP("officina-postgres")


@mcp.tool
def insertar_decision(
    codigo: str,
    fecha: str,
    proyecto: str,
    titulo: str,
    decision: str,
    contexto: str,
    razon: str,
    implicaciones: str,
) -> dict[str, Any]:
    """Inserta una decision nueva en la tabla decisions con estado='vigente'.

    Args:
        codigo: Codigo unico DEC-NNN (ej: 'DEC-019').
        fecha: Fecha de la decision en formato ISO 'YYYY-MM-DD'.
        proyecto: Identificador del proyecto en kebab-case (ej: 'officina').
        titulo: Titulo corto.
        decision: Texto de la decision tomada.
        contexto: Contexto que motivo la decision.
        razon: Justificacion de por que esta decision.
        implicaciones: Consecuencias y proximos pasos derivados.

    Returns:
        Dict con la fila insertada (todos los campos).
    """
    sql = """
        INSERT INTO decisions
            (codigo, fecha, proyecto, titulo, decision, contexto,
             razon, implicaciones, estado)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, 'vigente')
        RETURNING *;
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            sql,
            (codigo, fecha, proyecto, titulo, decision, contexto,
             razon, implicaciones),
        )
        row = cur.fetchone()
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def insertar_pendiente(
    proyecto: str,
    titulo: str,
    descripcion: str,
    prioridad: str,
    proximo_paso: str,
) -> dict[str, Any]:
    """Inserta un pendiente nuevo con estado='abierto'.

    Args:
        proyecto: Identificador del proyecto en kebab-case.
        titulo: Titulo corto.
        descripcion: Descripcion detallada.
        prioridad: Una de 'alta', 'media', 'baja'.
        proximo_paso: Accion concreta proxima.

    Returns:
        Dict con la fila insertada (incluye id autogenerado).
    """
    sql = """
        INSERT INTO pendientes
            (proyecto, titulo, descripcion, prioridad, proximo_paso, estado)
        VALUES
            (%s, %s, %s, %s, %s, 'abierto')
        RETURNING *;
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, (proyecto, titulo, descripcion, prioridad, proximo_paso))
        row = cur.fetchone()
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def cambiar_estado_decision(
    codigo: str,
    nuevo_estado: str,
    superada_por: str | None = None,
) -> dict[str, Any]:
    """Cambia el estado de una decision. Sin validacion de transiciones
    (DEC-019: opcion permisiva).

    Args:
        codigo: Codigo DEC-NNN.
        nuevo_estado: Nuevo valor de estado (ej: 'vigente', 'superada',
            'archivada').
        superada_por: Codigo de la decision que la supera, si aplica.

    Returns:
        Dict con la fila actualizada.
    """
    sql = """
        UPDATE decisions
        SET estado = %s,
            superada_por = COALESCE(%s, superada_por)
        WHERE codigo = %s
        RETURNING *;
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, (nuevo_estado, superada_por, codigo))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"No existe decision con codigo='{codigo}'.")
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def cambiar_estado_pendiente(
    id: int,
    nuevo_estado: str,
    bloqueado_por: int | None = None,
) -> dict[str, Any]:
    """Cambia el estado de un pendiente. Sin validacion de transiciones
    (DEC-019: opcion permisiva).

    Args:
        id: ID del pendiente.
        nuevo_estado: Nuevo valor de estado (ej: 'abierto', 'en_curso',
            'bloqueado', 'cerrado').
        bloqueado_por: ID de otro pendiente que lo bloquea, si aplica.

    Returns:
        Dict con la fila actualizada.
    """
    sql = """
        UPDATE pendientes
        SET estado = %s,
            bloqueado_por = COALESCE(%s, bloqueado_por)
        WHERE id = %s
        RETURNING *;
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, (nuevo_estado, bloqueado_por, id))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"No existe pendiente con id={id}.")
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def actualizar_campos_decision(
    codigo: str,
    campos: dict[str, Any],
) -> dict[str, Any]:
    """Actualiza campos selectivos de una decision, validando whitelist.

    Campos permitidos: titulo, decision, contexto, razon, implicaciones,
    superada_por. Otros campos se rechazan.

    Args:
        codigo: Codigo DEC-NNN.
        campos: Dict {campo: nuevo_valor}.

    Returns:
        Dict con la fila actualizada.
    """
    if not campos:
        raise ValueError("campos vacio: nada que actualizar.")

    invalidos = set(campos) - DECISION_WHITELIST
    if invalidos:
        raise ValueError(
            f"Campos no permitidos: {sorted(invalidos)}. "
            f"Permitidos: {sorted(DECISION_WHITELIST)}."
        )

    set_clause = ", ".join(f"{k} = %s" for k in campos)
    valores = list(campos.values()) + [codigo]
    sql = f"UPDATE decisions SET {set_clause} WHERE codigo = %s RETURNING *;"

    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, valores)
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"No existe decision con codigo='{codigo}'.")
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def actualizar_campos_pendiente(
    id: int,
    campos: dict[str, Any],
) -> dict[str, Any]:
    """Actualiza campos selectivos de un pendiente, validando whitelist.

    Campos permitidos: titulo, descripcion, prioridad, proximo_paso,
    bloqueado_por. Otros campos se rechazan.

    Args:
        id: ID del pendiente.
        campos: Dict {campo: nuevo_valor}.

    Returns:
        Dict con la fila actualizada.
    """
    if not campos:
        raise ValueError("campos vacio: nada que actualizar.")

    invalidos = set(campos) - PENDIENTE_WHITELIST
    if invalidos:
        raise ValueError(
            f"Campos no permitidos: {sorted(invalidos)}. "
            f"Permitidos: {sorted(PENDIENTE_WHITELIST)}."
        )

    set_clause = ", ".join(f"{k} = %s" for k in campos)
    valores = list(campos.values()) + [id]
    sql = f"UPDATE pendientes SET {set_clause} WHERE id = %s RETURNING *;"

    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, valores)
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"No existe pendiente con id={id}.")
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def insertar_termino(
    termino: str,
    tipo: str,
    definicion_funcional: str,
    mapa: bool = False,
    flujo: bool = False,
    referencia: bool = False,
    forma: str | None = None,
) -> dict[str, Any]:
    """Inserta un Termino nuevo en la tabla diccionario (DEC-086).

    Args:
        termino: PK textual. No vacio.
        tipo: Uno de 'C' (Concepto), 'M' (Mecanismo), 'P' (Vocab. plataforma).
        definicion_funcional: Definicion operativa. No vacio.
        mapa: Si el Termino genera Nodo de Mapa. Default False.
        flujo: Si el Termino genera Nodo de Flujo. Default False.
        referencia: Si es Termino de referencia (no operativo). Default False.
        forma: Si flujo=True, una de 'rectangulo', 'rombo', 'cilindro',
            'ovalo', 'paralelogramo', 'documento', 'circulo'. None si no
            aplica.

    Returns:
        Dict con la fila insertada.
    """
    if not termino or not termino.strip():
        raise ValueError("termino vacio.")
    if not definicion_funcional or not definicion_funcional.strip():
        raise ValueError("definicion_funcional vacio.")
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(
            f"tipo invalido: '{tipo}'. Validos: {sorted(TIPOS_VALIDOS)}."
        )
    if forma is not None and forma not in FORMAS_VALIDAS:
        raise ValueError(
            f"forma invalida: '{forma}'. Validas: {sorted(FORMAS_VALIDAS)} o None."
        )

    sql = """
        INSERT INTO diccionario
            (termino, tipo, mapa, flujo, referencia, forma, definicion_funcional)
        VALUES
            (%s, %s, %s, %s, %s, %s, %s)
        RETURNING *;
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            sql,
            (termino, tipo, mapa, flujo, referencia, forma, definicion_funcional),
        )
        row = cur.fetchone()
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def actualizar_campos_termino(
    termino: str,
    campos: dict[str, Any],
) -> dict[str, Any]:
    """Actualiza campos selectivos de un Termino, validando whitelist.

    Campos permitidos: tipo, mapa, flujo, referencia, forma,
    definicion_funcional. NO permite cambiar 'termino' (renombrar la PK
    requiere CASCADE sobre relaciones; no es operacion estandar).

    Args:
        termino: PK del Termino a actualizar.
        campos: Dict {campo: nuevo_valor}. Para borrar 'forma' pasar None
            como valor.

    Returns:
        Dict con la fila actualizada.
    """
    if not campos:
        raise ValueError("campos vacio: nada que actualizar.")

    invalidos = set(campos) - TERMINO_WHITELIST
    if invalidos:
        raise ValueError(
            f"Campos no permitidos: {sorted(invalidos)}. "
            f"Permitidos: {sorted(TERMINO_WHITELIST)}."
        )

    # Validar valores en CHECK constraints replicados.
    if "tipo" in campos and campos["tipo"] not in TIPOS_VALIDOS:
        raise ValueError(
            f"tipo invalido: '{campos['tipo']}'. "
            f"Validos: {sorted(TIPOS_VALIDOS)}."
        )
    if "forma" in campos:
        v = campos["forma"]
        if v is not None and v not in FORMAS_VALIDAS:
            raise ValueError(
                f"forma invalida: '{v}'. "
                f"Validas: {sorted(FORMAS_VALIDAS)} o None."
            )

    set_clause = ", ".join(f"{k} = %s" for k in campos)
    valores = list(campos.values()) + [termino]
    sql = f"UPDATE diccionario SET {set_clause} WHERE termino = %s RETURNING *;"

    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, valores)
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"No existe termino='{termino}' en diccionario.")
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def insertar_relacion(
    termino: str,
    termino_relacionado: str,
    tipo_relacion: str,
) -> dict[str, Any] | None:
    """Inserta una relacion entre dos Terminos (DEC-086).

    Idempotente: si la relacion ya existe (UNIQUE constraint), devuelve
    None en vez de fallar. Esto permite reintentar bloques de carga
    durante calibracion sin envolver todo en transacciones grandes.

    Args:
        termino: PK del Termino origen.
        termino_relacionado: PK del Termino destino. Debe existir en
            diccionario (FK lo valida) y ser distinto de termino
            (CHECK relacion_no_autoreflexiva lo valida).
        tipo_relacion: Una de 'pertenece_a', 'depende_de'.

    Returns:
        Dict con la fila insertada, o None si ya existia.
    """
    if tipo_relacion not in TIPOS_RELACION_VALIDOS:
        raise ValueError(
            f"tipo_relacion invalido: '{tipo_relacion}'. "
            f"Validos: {sorted(TIPOS_RELACION_VALIDOS)}."
        )
    if termino == termino_relacionado:
        raise ValueError(
            "termino y termino_relacionado son iguales "
            "(relacion autoreflexiva no permitida)."
        )

    sql = """
        INSERT INTO relaciones
            (termino, termino_relacionado, tipo_relacion)
        VALUES
            (%s, %s, %s)
        ON CONFLICT (termino, termino_relacionado, tipo_relacion)
            DO NOTHING
        RETURNING *;
    """
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, (termino, termino_relacionado, tipo_relacion))
        row = cur.fetchone()
        if row is None:
            # Conflicto silencioso: la relacion ya existia.
            conn.commit()
            return None
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def eliminar_relacion(id_relacion: int) -> dict[str, Any]:
    """Elimina una relacion por id_relacion. Util durante calibracion
    iterativa cuando se descubre que un mapeo fue incorrecto.

    Args:
        id_relacion: PK serial de la relacion a eliminar.

    Returns:
        Dict con la fila eliminada (los campos retornados son los que
        tenia antes del DELETE).
    """
    sql = "DELETE FROM relaciones WHERE id_relacion = %s RETURNING *;"
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql, (id_relacion,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(
                f"No existe relacion con id_relacion={id_relacion}."
            )
        result = _serialize_row(_row_to_dict(cur, row))
        conn.commit()
        return result


@mcp.tool
def query_select(sql: str) -> list[dict[str, Any]]:
    """Ejecuta un SELECT contra la DB. Solo SELECT (validado con sqlglot).

    Acepta SELECT, UNION, EXCEPT, INTERSECT. Rechaza cualquier DML/DDL,
    multi-statement, o SQL invalido.

    Args:
        sql: Query SQL a ejecutar.

    Returns:
        Lista de filas como dicts.
    """
    _validate_select_only(sql)

    with _connect() as conn, conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
        return [_serialize_row(_row_to_dict(cur, row)) for row in rows]


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()

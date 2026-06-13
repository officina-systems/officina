# OFFICINA Scripts

Los scripts operativos de OFFICINA viven en este directorio.

Este README define la convención general de organización. No debe convertirse en un índice manual de funciones.

## Funciones simples

Una función simple vive como un solo archivo PowerShell dentro de un área operacional.

Formato:

scripts/<area>/<NombreFuncion>.ps1

Ejemplos:

scripts/runtime/Start-OfficinaStack.ps1
scripts/security/Test-OfficinaSecrets.ps1

El archivo debe incluir al inicio un comentario claro, detallado y explícito que explique qué hace la función, cuándo usarla, qué rutas toca y qué riesgos operativos existen.

## Funciones complejas o modulares

Una función compleja vive en su propia carpeta.

Formato:

scripts/<area>/<NombreFuncion>/<NombreFuncion>.ps1
scripts/<area>/<NombreFuncion>/<modulo-interno>.ps1

Ejemplo:

scripts/publish/Invoke-OfficinaPublishFlow/Invoke-OfficinaPublishFlow.ps1
scripts/publish/Invoke-OfficinaPublishFlow/config.ps1
scripts/publish/Invoke-OfficinaPublishFlow/git.ps1
scripts/publish/Invoke-OfficinaPublishFlow/sync-public.ps1
scripts/publish/Invoke-OfficinaPublishFlow/scan.ps1
scripts/publish/Invoke-OfficinaPublishFlow/confirm.ps1

El archivo principal debe ser el entrypoint ejecutable.

Los módulos internos no deben ejecutarse directamente. Solo existen para dividir una función compleja en partes más claras.

## Comentario descriptivo

Toda función principal debe incluir un bloque de comentario al inicio del archivo.

Ese comentario debe explicar de forma suficiente:

- qué hace la función;
- cuándo usarla;
- qué rutas toca;
- qué repositorios o sistemas afecta;
- qué archivos puede crear, modificar, borrar, commitear o publicar;
- qué acciones requieren confirmación;
- qué cosas nunca debe hacer;
- cuál es su modo seguro por defecto.

## Reglas operativas

- Una función simple puede vivir como un solo archivo .ps1.
- Una función compleja debe vivir en una carpeta propia.
- El script principal debe tener el mismo nombre que la función.
- No usar README por función salvo necesidad excepcional.
- La explicación operacional debe vivir dentro del .ps1 principal.
- Toda función debe ser segura por defecto.
- Toda acción destructiva, persistente o externa debe pedir confirmación explícita.
- No publicar secretos, archivos privados ni residuos locales.

# db/ — Schemas SQL canónicos

Orden de ejecución fresh install:

```
001_initial_schema.sql   → nodes + edges base
003_bootstrap_nodes.sql  → 28 nodos lote 1 (linaje)
004_phase1_schema.sql    → migraciones S30: node_chunks, session.*, usage
```

Ejecución vía PowerShell:
```powershell
Get-Content "db\001_initial_schema.sql" | docker exec -i officina-postgres psql -U officina -d officina
Get-Content "db\003_bootstrap_nodes.sql" | docker exec -i officina-postgres psql -U officina -d officina
Get-Content "db\004_phase1_schema.sql" | docker exec -i officina-postgres psql -U officina -d officina
```

FUV: officina-infra.md (PARTE II)

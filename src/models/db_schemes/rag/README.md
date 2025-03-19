## Run Alembic Migrations

### What is Alembic
Alembic is a lightweight database migration tool created by the author of SQLAlchemy. It's valuable with PostgreSQL databases because it:

1. Manages incremental schema changes without data loss
2. Version-controls your database structure
3. Supports reversible migrations (upgrades/downgrades)

Alembic uses a simple CLI interface and Python-based migration scripts. Each migration is stored as a separate file with a unique version identifier, creating a complete history of your schema changes. The tool focuses specifically on schema migrations rather than being a full ORM or database toolkit.
Without a migration tool like Alembic, you'd have to manually track and apply schema changes, which becomes increasingly difficult as your application evolves.

### Configration:
1. Navigate in terminal inside models folder
```bash
alembic init alembic
```
Note: - This command would create 1. a folder called `Alembic` under models folder, 2. alembic.ini file
- if you clone this repo the folder would be exist, you just need to take compy from alembic.ini.example file to create your onw version of alembic.ini

```bash
cp alembic.ini.example alembic.ini
```
2. Update the `alembic.ini` with your database credentials (`sqlalchemy.url`)

3. add base file for models in the `models/db_schemes/rag/alembic/env.py`
```python
from schemes import SQLAlchemyBase
```
assign value to `target_metadat`
```python
target_metadata = SQLAlchemyBase.metadata
```

4. Create a new migration (optional)

```bash
alembic revision --autogenerate -m "Add ..."
```

### Upgrade the database

```bash
alembic upgrade head
```

## Run Alembic Migrations

### What is Alembic
Alembic is a lightweight database migration tool created by the author of SQLAlchemy. It's valuable with PostgreSQL databases because it:

1. Manages incremental schema changes without data loss
2. Version-controls your database structure
3. Supports reversible migrations (upgrades/downgrades)

Alembic uses a simple CLI interface and Python-based migration scripts. Each migration is stored as a separate file with a unique version identifier, creating a complete history of your schema changes. The tool focuses specifically on schema migrations rather than being a full ORM or database toolkit.
Without a migration tool like Alembic, you'd have to manually track and apply schema changes, which becomes increasingly difficult as your application evolves.

### Configration:
1. Navigate in terminal inside `/src/models/db_schemes/rag`
- Run (Optional)
```bash
alembic init alembic
```
Note: - This command would create 2 things:
- a folder called `Alembic` under this folder
- `alembic.ini` file
If you cloned this repo the folder would be exist, you just need to take copy from alembic.ini.example file to create your onw version of `alembic.ini` using
```bash
cp alembic.ini.example alembic.ini
```
2. Update the `alembic.ini` with your database string connection in variable called(`sqlalchemy.url`)

3. Do some modification on the file `models/db_schemes/rag/alembic/env.py`:
- Add the base module for your schema as:
```python
from schemes import SQLAlchemyBase
```
- Assign value to `target_metadat` as
```python
target_metadata = SQLAlchemyBase.metadata
```

4. Create a new migration (optional)

```bash
alembic revision --autogenerate -m "Add ..."
```
Note: already there is a created version on the cloned repo

5. Upgrade the database with created version using:

```bash
alembic upgrade head
```

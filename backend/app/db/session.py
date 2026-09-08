from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect
from app.core.config import settings

# echo=False keeps the dev console readable; set SQL_ECHO=1 to trace statements.
engine = create_async_engine(settings.DATABASE_URL, echo=settings.SQL_ECHO, future=True)

async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def _literal_default(column):
    """Render a column's default as SQL literal, or None when it can't be expressed.

    Only scalar defaults can be used in ``ALTER TABLE ... ADD COLUMN``; callable
    defaults (e.g. ``list``/``datetime.now``) are skipped and the column is
    simply added as NULL-able.
    """
    default = column.default
    if default is None or not getattr(default, "is_scalar", False):
        return None
    value = default.arg
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    return None


def _add_missing_columns(sync_conn):
    """Bring already-created tables in line with the models.

    ``Base.metadata.create_all`` creates missing *tables* but never alters
    existing ones, so newly added model columns would be invisible to the ORM
    and every query would fail. This performs the additive part of a migration
    (safe + idempotent) which is what this project needs while it runs on a
    local SQLite file.
    """
    inspector = inspect(sync_conn)
    existing_tables = set(inspector.get_table_names())
    added = []

    for table in Base.metadata.sorted_tables:
        if table.name not in existing_tables:
            continue  # freshly created by create_all — already up to date

        existing_columns = {col["name"] for col in inspector.get_columns(table.name)}
        for column in table.columns:
            if column.name in existing_columns:
                continue

            type_sql = column.type.compile(dialect=sync_conn.dialect)
            statement = f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" {type_sql}'
            default_sql = _literal_default(column)
            if default_sql is not None:
                statement += f" DEFAULT {default_sql}"

            sync_conn.exec_driver_sql(statement)
            added.append(f"{table.name}.{column.name}")

    return added


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        added = await conn.run_sync(_add_missing_columns)

    if added:
        print(f"[INFO] Schema sync added {len(added)} column(s): {', '.join(added)}")

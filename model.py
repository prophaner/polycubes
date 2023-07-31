from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, Column, VARBINARY, Integer, func, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import declarative_base
from contextlib import contextmanager

Base = declarative_base()
BUFFER_SIZE = 10000
SERVER = ''
PORT = ''
DB = ''
USERNAME = ''
PASSWORD = ''


def create_polycube_table(size):
    return type(f"Polycube_{size}", (Base,), {
        '__tablename__': f"polycube_{size}",
        'id': Column(Integer, primary_key=True, autoincrement=True),
        'shape': Column(VARBINARY(30), unique=True, nullable=False)
    })


tables = {i: create_polycube_table(i) for i in range(1, 21)}


class Database:
    def __init__(self):
        self.engine = create_engine(f'mssql+pymssql://{USERNAME}:{PASSWORD}@{SERVER}:{PORT}/{DB}', echo=False, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = Session(bind=self.engine)
        try:
            yield session
            session.commit()
        except Exception as e:
            print(e)
            session.rollback()
        finally:
            session.close()

    def insert_first(self):
        with self.session_scope() as session:
            return session.bulk_insert_mappings(tables[1], [{'shape': b'\x07\x00\x80'}])

    def get_count(self, size):
        with self.session_scope() as session:
            return session.query(tables[size]).count()

    def get_max_id(self, size):
        with self.session_scope() as session:
            return session.query(func.max(tables[size].id)).scalar()

    def process(self, size, start=0):
        if self.get_max_id(size):
            return []
        with self.session_scope() as session:
            return [shape.shape for shape in session.query(tables[size - 1]).order_by(tables[size - 1].id).limit(BUFFER_SIZE).offset(start)]

    def postprocess(self, identities, size):
        with self.session_scope() as session:
            session.execute(insert(tables[size]).values([{'shape': identity} for identity in identities]).on_conflict_do_nothing(index_elements=['shape']))

    def drop_all_content(self, size):
        """Delete all content from the tables."""
        with self.session_scope() as session:
            session.execute(tables[size].__table__.delete())

    def table_size(self, size):
        size_query = text(f"""
            SELECT 
                SUM(reserved_page_count * 8.0 * 1024) 
            FROM 
                sys.dm_db_partition_stats 
            WHERE 
                object_id=OBJECT_ID('polycube_{size}')
            """)

        with self.session_scope() as session:
            size_in_bytes = session.execute(size_query).scalar()

        if size_in_bytes < 1024:
            return f"{size_in_bytes} B"
        elif size_in_bytes < 1024**2:
            return f"{int(size_in_bytes / 1024)} KB"
        elif size_in_bytes < 1024**3:
            return f"{int(size_in_bytes / 1024**2)} MB"
        elif size_in_bytes < 1024**4:
            return f"{int(size_in_bytes / 1024**3)} GB"
        elif size_in_bytes < 1024**5:
            return f"{int(size_in_bytes / 1024**4)} TB"
        else:
            return f"{int(size_in_bytes / 1024**5)} PB"

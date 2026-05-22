from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables:', tables)
for t in tables:
    cols = [(c['name'], str(c['type'])) for c in inspector.get_columns(t)]
    print(f'  {t}: {cols}')

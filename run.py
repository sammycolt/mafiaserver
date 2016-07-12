from app.api import *

def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()

# clear_data(session=db.session)
app.run()

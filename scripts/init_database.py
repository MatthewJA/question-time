"""Initialises the (temporary) SQLite3 database to dump location data into."""

import database

database.Base.metadata.drop_all(bind=database.engine)
database.Base.metadata.create_all(bind=database.engine)

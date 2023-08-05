chembl_migration_model
======

This is chembl_migrate package developed at Chembl group, EMBL-EBI, Cambridge, UK.

This package provides custom Django management command 'migrate'.
For usage type `python manage.py migrate help`.
'migrate' copies data from one database to another.
Both databases must be described by the same Django model.
By default django model being migrated is 'chembl_migration_model' but this can be changed in settings to any other django model.
If target database doesn't have tables required by the model they will be created, despite status of 'managed' meta flag.
All data is copied in order that should avoid any integration errors.
Migration process is done in chunks of 1000 records but this number can be configured.
Each chunk is copied within a transaction.
When interrupted, the migration process can be rerun and it will detect which data has already been migrated and start migration from the point where it finished.

# Demo Data

## Contents

- `anastasiia-database.json` — Full Django fixture (all apps: api, auth, contenttypes, token_blacklist)
- `schema.sql` — Database schema reference

## How to Load

1. Make sure PostgreSQL is running and migrations are applied:

   ```bash
   venv/bin/python manage.py migrate
   ```

2. Load the demo data:

   ```bash
   venv/bin/python manage.py loaddata sql/anastasiia-database.json
   ```

   This will populate your database with the shared demo dataset.

## How to Re-generate

If you've made changes to the data and want to share the updated version:

```bash
venv/bin/python manage.py dumpdata --indent 2 -o sql/anastasiia-database.json
```

Commit and push `sql/anastasiia-database.json` so other team members can pull and load it.

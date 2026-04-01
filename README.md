# Backend - Lost and Found Management System

**[Main Repositories](https://github.com/jui-wen-chiang/lost-and-found-GBC-main)**

This is the core engine of the Lost and Found Management System. It provides a robust and secure RESTful API to manage item reports, user authentication, and data persistence. Built with a focus on performance and scalability.

## Backend Development Setup
1. Clone the backend repository
2. Navigate to the project directory: `cd lost-and-found-backend`
3. Set up Python Virtual Environment:
    - Using `venv`: `python -m venv venv`
    - Or use Miniconda to create and activate the environment.
4. Install dependencies:`pip install -r requirements.txt`
5. Configure environment variables. Create and set up your `.env.production` and `.env.development` file.
6. Initialize the local database and update your local database settings in the `.env.development` file. It should look like this: `Local DB = postgresql://[username]:[password]@localhost:5432/lost_and_found_management_system`.
7. (Optional) After modifying the models, please generate and apply the migrations. 
8. Start the development server: `python manage.py runserver`

## DB Migration
If necessary, you can delete all existing migration files (keeping only __init__.py) by running:
```bash
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
```

Run the following commands to generate new migration files and actually create the tables in the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

##  Load Demo Data
- `sql/anastasiia-database.json` — Full Django fixture (all apps: api, auth, contenttypes, token_blacklist)
- `sql/schema.sql` — Database schema reference

### How to Load
```bash
# After PostgreSQL is running and migrations are applied
python manage.py migrate

# Load the demo data
python manage.py loaddata sql/anastasiia-database.json
```

### How to Re-generate
If you've made changes to the data and want to share the updated version:
```bash
python manage.py dumpdata --indent 2 -o sql/anastasiia-database.json
```

## API Documentation
- Production (Render): [Swagger Docs](https://lost-and-found-backend-gbc.onrender.com/api/docs/)
- Local Development URL: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

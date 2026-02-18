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
6. Initialize the database (Currently no database tables).
7. Start the development server: `python manage.py runserver`

## API Documentation
- Production (Render): [Swagger Docs](https://lost-and-found-backend-gbc.onrender.com/api/docs/)
- Local Development URL: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)

# Construction Project Management System

A web-based system for managing construction project bids and documentation, built with FastAPI and Streamlit.

## Features

- Project bid form management
- Real-time data validation
- Document review workflow
- Project status tracking
- Multi-branch office support

## Tech Stack

### Backend
- FastAPI (REST API)
- SQLAlchemy (ORM)
- SQLite (Database)
- Python-dotenv (Environment Configuration)

### Frontend
- Streamlit (Web Interface)
- Requests (API Communication)

## Project Structure

```
st_docx/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py (FastAPI application)
│   ├── models.py (Database models)
│   ├── schemas.py (Pydantic models)
│   └── database.py (Database configuration)
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── view_bidform.py (Streamlit interface)
├── data/ (Database files)
├── docker-compose.yml
├── .env (Environment variables)
└── .env.example (Environment template)
```

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd st_docx
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

3. Start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

## Accessing the Application

- Frontend (Streamlit): http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```env
DBPATH=sqlite:///./data/sql_app.db
```

## Development

### Running in Development Mode

1. Start the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   pip install -r requirements.txt
   streamlit run view_bidform.py
   ```

## Docker Support

The application is containerized using Docker:
- Separate containers for frontend and backend
- Volume mounting for database persistence
- Internal network for service communication

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

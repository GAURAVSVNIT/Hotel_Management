# Hotel Management System

A comprehensive hotel management system built with Django and Tailwind CSS.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Python](https://www.python.org/downloads/) (3.8 or higher)
- [pip](https://pip.pypa.io/en/stable/installation/) (Python package manager)
- [Git](https://git-scm.com/downloads) (for cloning the repository)
- [Node.js](https://nodejs.org/) (14.0 or higher)
- [npm](https://www.npmjs.com/get-npm) (Node.js package manager)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Hotel_Management
```

### 2. Create and Activate Virtual Environment

#### For Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### For macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Node.js Dependencies

```bash
npm install
```

### 5. Database Setup

The project uses SQLite by default. Run the following commands to set up the database:

```bash
python manage.py migrate
```

If you need to apply specific migrations as mentioned in the `migration_instructions.md`, follow those steps.

### 6. Compile Tailwind CSS

```bash
npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --watch
```

### 7. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### 8. Run the Development Server

```bash
python manage.py runserver
```

The development server will start at `http://127.0.0.1:8000/`.

## Project Structure

- `hotel_management/` - Main Django project directory
- `main/` - Django app for core functionality
- `ratings/` - Django app for ratings system
- `static/` - Static files (CSS, JavaScript, images)
- `media/` - Media files (user uploads)
- `theme/` - Theme-related files
- `staticfiles/` - Collected static files

## Deployment

For deploying to a production environment, follow these additional steps:

1. Set the `DEBUG` setting to `False` in your settings file
2. Configure your web server (Nginx, Apache, etc.)
3. Set up a production-ready database (PostgreSQL recommended)
4. Set up proper environment variables for sensitive information

## Troubleshooting

If you encounter any issues during setup:

1. Ensure all prerequisites are correctly installed
2. Check that your virtual environment is activated
3. Verify that all dependencies are installed
4. Check the Django error logs

## License

[Include license information here]

## Contributing

[Include contribution guidelines here]


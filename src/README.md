# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Admin dashboard for managing users and activities (role-based access)

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

### Public Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                    |

### Admin Endpoints

All admin endpoints require HTTP Basic Auth with an admin account.

**Default admin credentials:** `admin@mergington.edu` / `admin123`

> ⚠️ **Security Warning:** Change the default admin passwords before deploying to any non-development environment.

#### User Management

| Method | Endpoint                        | Description                     |
| ------ | ------------------------------- | ------------------------------- |
| GET    | `/admin/users`                  | List all users                  |
| POST   | `/admin/users`                  | Create a new user               |
| PUT    | `/admin/users/{email}`          | Update an existing user         |
| DELETE | `/admin/users/{email}`          | Delete a user                   |

#### Activity Management

| Method | Endpoint                                  | Description                     |
| ------ | ----------------------------------------- | ------------------------------- |
| POST   | `/admin/activities`                       | Create a new activity           |
| PUT    | `/admin/activities/{activity_name}`       | Update an existing activity     |
| DELETE | `/admin/activities/{activity_name}`       | Delete an activity              |

### Error Responses

- `401 Unauthorized` — Missing or invalid credentials
- `403 Forbidden` — Valid credentials but insufficient role (non-admin user)
- `404 Not Found` — Requested resource does not exist
- `400 Bad Request` — Validation error (e.g. duplicate email, invalid role)

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Users** - Uses email as identifier:
   - Name
   - Password
   - Role (`admin`, `teacher`, or `student`)
   - Grade level (for students)

All data is stored in memory, which means data will be reset when the server restarts.

# Development Credentials

## Admin User

Use these credentials to login to the application:

**Email:** `admin@salesbot.dev`
**Password:** `admin123`

> **Note:** This user was created with email auto-confirmed for development.

## Creating Additional Test Users

Run the provided scripts to create more users:

```bash
# From apps/api directory
../../venv/Scripts/python.exe setup_admin_user.py
```

## Password Requirements

- Minimum 6 characters (Supabase requirement)
- Must use valid email domains (no example.com, test.com, etc.)
- Email must be confirmed (use admin API for dev users)

## Troubleshooting Login Issues

If login fails with "Email not confirmed":
1. Users created via `/auth/signup` need email confirmation
2. For dev, use the admin API to create users with `email_confirm: True`
3. See `setup_admin_user.py` for reference

## API Endpoints

- **Login:** `POST /auth/login`
- **Signup:** `POST /auth/signup`
- **Get Profile:** `GET /auth/me` (requires Bearer token)
- **Refresh Token:** `POST /auth/refresh`
- **Logout:** `POST /auth/logout`

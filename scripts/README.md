# Scripts Directory

Utility scripts for the Neroxia project.

## 📁 Organization

### `tests/`
Utility test scripts for database, Supabase, and integration testing:

- `test_db_connection.py` - Test database connectivity
- `test_db_only.py` - Database-only tests
- `test_integration.py` - Integration testing
- `test_supabase.py` - Supabase connection tests
- `test_supabase_simple.py` - Simple Supabase tests

### `utils/`
Utility scripts for project management:

- `create_test_user.py` - Create test users in database

### Other Scripts

- `check_supabase_auth.py` - Verify Supabase authentication
- `create_admin_user.py` - Create admin user
- `init_database.py` - Initialize database
- `start_dev.sh` / `start_dev.ps1` - Development server startup
- `verify_supabase_connection.py` - Verify Supabase connection
- `supabase_schema.sql` - Database schema
- `enable_rls.sql` - Enable Row Level Security

## 🚀 Usage

### Running Test Scripts

```bash
cd scripts/tests

# Test database connection
python test_db_connection.py

# Test Supabase
python test_supabase.py

# Run integration tests
python test_integration.py
```

### Using Utility Scripts

```bash
cd scripts/utils

# Create a test user
python create_test_user.py
```

### Development Scripts

```bash
# Start development servers (Linux/Mac)
./scripts/start_dev.sh

# Start development servers (Windows)
.\scripts\start_dev.ps1
```

## 📝 Notes

- Test scripts are standalone and don't require pytest
- Utility scripts may require specific environment variables
- Check individual script documentation for requirements

## 🔗 Related

- [Main Test Guide](../TEST_GUIDE.md)
- [API Tests](../apps/api/tests/README.md)
- [Bot Engine Tests](../apps/bot-engine/tests/README.md)

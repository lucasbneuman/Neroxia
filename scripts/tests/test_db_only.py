#!/usr/bin/env python
"""Test solo de la conexión a la base de datos."""

import os
import sys
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
env_path = project_root / '.env'
load_dotenv(env_path)

SUPABASE_DATABASE_URL = os.getenv("SUPABASE_DATABASE_URL")

print("=" * 80)
print("TEST DE CONEXION A BASE DE DATOS")
print("=" * 80)
print()

print(f"Database URL: {SUPABASE_DATABASE_URL}")
print()

try:
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    # Create engine
    print("1. Creando engine de SQLAlchemy...")
    engine = create_async_engine(SUPABASE_DATABASE_URL, echo=False)
    print("   [OK] Engine creado")
    print()

    async def test_connection():
        print("2. Probando conexión a la base de datos...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"   [OK] Consulta ejecutada: SELECT 1 = {test_value}")

            # Get PostgreSQL version
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"   [OK] PostgreSQL version: {version[:50]}...")

            # Check if we can see tables
            result = await conn.execute(text("""
                SELECT count(*) FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            table_count = result.scalar()
            print(f"   [OK] Tablas en schema public: {table_count}")

            return True

    # Run test
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_connection())

    # Cleanup
    print()
    print("3. Cerrando conexión...")
    loop.run_until_complete(engine.dispose())
    print("   [OK] Conexión cerrada")
    print()

    if success:
        print("=" * 80)
        print("[EXITO] CONEXION A BASE DE DATOS FUNCIONA CORRECTAMENTE!")
        print("=" * 80)
        print()
        print("Ahora puedes:")
        print("1. Reiniciar el API")
        print("2. Probar el endpoint /config/")
        print("3. Probar el endpoint /bot/process")
        sys.exit(0)

except Exception as e:
    print()
    print("=" * 80)
    print(f"[ERROR] FALLO LA CONEXION: {e}")
    print("=" * 80)
    print()
    print("Posibles causas:")
    print("1. La contraseña es incorrecta")
    print("2. El hostname del pooler es incorrecto")
    print("3. El puerto es incorrecto")
    print("4. La base de datos no existe")
    print()
    import traceback
    print("Detalles técnicos:")
    traceback.print_exc()
    sys.exit(1)

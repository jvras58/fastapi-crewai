#!/bin/bash
# Script para auto gerar a migration usando o alembic lembre-se de importar o modelo no **/models/__init__.py
# Uso: ./scripts/migrate.sh "minha mensagem de migração" ou dentro do ambiente virtual task automate_migrations "minha mensagem de migração"

if [ -z "$1" ]; then
    echo "Usage: ./scripts/migrate.sh 'migration message'"
    exit 1
fi

alembic revision --autogenerate -m "$1"

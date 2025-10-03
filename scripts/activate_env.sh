#!/bin/bash
# Script para ativar o ambiente virtual do uv
# Uso: source activate_env.sh

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    echo "✅ Ambiente virtual ativado! Agora você pode usar 'task' diretamente."
    echo ""
    echo "📋 Tasks disponíveis para o core:"
    echo "  task test     - Executar testes"
    echo "  task run      - Executar a aplicação"
    echo "  task format   - Formatar código"
    echo "  task lint     - Verificar linting"
    echo "  task -l       - Listar todas as tasks"
    echo "  task migrate  - Aplicar migrações de banco de dados"
    echo "  task automate_migrations 'mensagem' - Criar nova migração com mensagem"
    echo "  task seed_super_user - rodar seed do super usuário"
    echo "  task seed_transactions - rodar seed de transações"
    echo "  setup_db - Configurar banco de dados (migrações + seeds)"
    echo ""
    echo "💡 Ou use sempre: uv run task <comando>"
else
    echo "❌ Ambiente virtual não encontrado. Execute 'uv sync' primeiro."
fi

"""Exemplos de uso do sistema de chat com IA."""


from apps.ia.agents.conversation_agent import (
    ConversationAgent,
    SimpleConversationAgent,
)
from apps.ia.services.rag_service import RAGService


def exemplo_rag_basico():
    """Exemplo básico de uso do RAG."""
    print('\n=== Exemplo RAG Básico ===')

    # Criar serviço RAG
    rag_service = RAGService()

    # Adicionar alguns documentos de exemplo
    documentos = [
        {
            'texto': (
                'FastAPI é um framework web moderno e rápido para construir APIs '
                'com Python. É baseado em Starlette para as partes web e '
                'Pydantic para as partes de dados.'
            ),
            'metadados': {
                'fonte': 'documentacao_fastapi',
                'categoria': 'framework',
            },
        },
        {
            'texto': (
                'CrewAI é uma plataforma para orquestração de agentes de IA. '
                'Permite criar equipes de agentes que trabalham juntos para '
                'resolver problemas complexos.'
            ),
            'metadados': {'fonte': 'documentacao_crewai', 'categoria': 'ia'},
        },
        {
            'texto': (
                'SQLAlchemy é o kit de ferramentas SQL Python e Object '
                'Relational Mapping (ORM) que oferece aos desenvolvedores de '
                'aplicações toda a potência e flexibilidade do SQL.'
            ),
            'metadados': {
                'fonte': 'documentacao_sqlalchemy',
                'categoria': 'database',
            },
        },
    ]

    # Adicionar documentos ao RAG
    for doc in documentos:
        rag_service.add_document_from_text(doc['texto'], doc['metadados'])

    print(f'Documentos adicionados: {rag_service.get_document_count()}')

    # Fazer algumas buscas
    consultas = [
        'O que é FastAPI?',
        'Como funciona a orquestração de agentes?',
        'ORM Python',
    ]

    for consulta in consultas:
        print(f'\n🔍 Consulta: {consulta}')
        resultados = rag_service.similarity_search(consulta, k=2)

        for i, resultado in enumerate(resultados, 1):
            fonte = resultado.metadata.get('fonte', 'desconhecida')
            print(f'  {i}. Fonte: {fonte}')
            print(f'     Conteúdo: {resultado.page_content[:100]}...')


def exemplo_agent_simples():
    """Exemplo de uso do agent de conversação simples."""
    print('\n=== Exemplo Agent Simples ===')

    try:
        # Criar agent simples
        agent = SimpleConversationAgent()

        # Fazer algumas perguntas
        perguntas = [
            'Olá, como você está?',
            'Explique o que é FastAPI em uma frase',
            'Qual é a capital do Brasil?',
        ]

        for pergunta in perguntas:
            print(f'\n💬 Pergunta: {pergunta}')
            try:
                resposta = agent.chat(pergunta)
                print(f'🤖 Resposta: {resposta}')
            except Exception as e:
                print(f'⚠️  Erro: {e}')

    except Exception as e:
        print(f'⚠️  Agent simples não disponível: {e}')


def exemplo_agent_com_rag():
    """Exemplo de uso do agent com RAG."""
    print('\n=== Exemplo Agent com RAG ===')

    try:
        # Criar serviço RAG
        rag_service = RAGService()

        # Adicionar conhecimento
        conhecimento = [
            (
                'Nossa empresa oferece três planos: Básico (R$ 29/mês), '
                'Premium (R$ 59/mês) e Enterprise (R$ 129/mês).'
            ),
            (
                'O suporte técnico está disponível de segunda a sexta, '
                'das 9h às 18h, através do email suporte@empresa.com.'
            ),
            (
                'Para cancelar sua assinatura, acesse a área do cliente ou '
                'entre em contato conosco com 30 dias de antecedência.'
            ),
            (
                'Oferecemos integração com mais de 50 ferramentas, incluindo '
                'Slack, Discord, Teams e WhatsApp.'
            ),
            (
                'Nossa política de reembolso permite devolução em até 7 dias '
                'após a compra, sem questionamentos.'
            ),
        ]

        for i, texto in enumerate(conhecimento):
            rag_service.add_document_from_text(
                texto, {'fonte': f'base_conhecimento_{i}', 'tipo': 'faq'}
            )

        # Criar agent com RAG
        agent = ConversationAgent(rag_service)

        # Fazer perguntas relacionadas ao conhecimento
        perguntas_rag = [
            'Quais são os planos disponíveis?',
            'Como posso entrar em contato com o suporte?',
            'Qual é a política de cancelamento?',
            'Vocês têm integração com Slack?',
        ]

        for pergunta in perguntas_rag:
            print(f'\n💬 Pergunta: {pergunta}')
            try:
                resposta = agent.chat(pergunta)
                print(f'🤖 Resposta: {resposta}')
            except Exception as e:
                print(f'⚠️  Erro: {e}')

    except Exception as e:
        print(f'⚠️  Agent com RAG não disponível: {e}')


def exemplo_busca_conhecimento():
    """Exemplo de busca direta na base de conhecimento."""
    print('\n=== Exemplo Busca Conhecimento ===')

    rag_service = RAGService()

    # Adicionar documentos técnicos
    docs_tecnicos = [
        {
            'texto': (
                'Para configurar o banco de dados PostgreSQL, defina a '
                'variável DB_URL no formato postgresql://user:pass@host:port/dbname'
            ),
            'metadados': {
                'categoria': 'configuracao',
                'tecnologia': 'postgresql',
            },
        },
        {
            'texto': (
                'As migrações do Alembic devem ser executadas com '
                "'alembic upgrade head' após criar com "
                "'alembic revision --autogenerate'"
            ),
            'metadados': {
                'categoria': 'configuracao',
                'tecnologia': 'alembic',
            },
        },
        {
            'texto': (
                'Para autenticação JWT, configure SECURITY_API_SECRET_KEY e '
                'SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES no arquivo .env'
            ),
            'metadados': {'categoria': 'seguranca', 'tecnologia': 'jwt'},
        },
    ]

    # Adicionar documentos
    textos = [doc['texto'] for doc in docs_tecnicos]
    metadados = [doc['metadados'] for doc in docs_tecnicos]
    rag_service.add_documents(textos, metadados)

    # Buscar com scores de similaridade
    consulta = 'Como configurar autenticação'
    print(f'🔍 Buscando: {consulta}')

    resultados_com_score = rag_service.similarity_search_with_score(
        consulta, k=3
    )

    for resultado, score in resultados_com_score:
        categoria = resultado.metadata.get('categoria', 'N/A')
        tecnologia = resultado.metadata.get('tecnologia', 'N/A')
        print(f'\n📄 Score: {score:.3f}')
        print(f'   Categoria: {categoria} | Tecnologia: {tecnologia}')
        print(f'   Conteúdo: {resultado.page_content}')


def main():
    """Executar todos os exemplos."""
    print('🚀 Exemplos de uso do Sistema de Chat com IA')
    print('=' * 50)

    try:
        exemplo_rag_basico()
        exemplo_agent_simples()
        exemplo_agent_com_rag()
        exemplo_busca_conhecimento()

        print('\n✅ Todos os exemplos foram executados!')
        print('\n📚 Para usar em produção:')
        print('1. Configure GROQ_API_KEY no arquivo .env')
        print('2. Execute as migrações do banco de dados')
        print("3. Inicie o servidor FastAPI com 'task run'")
        print('4. Acesse a documentação em http://localhost:8000/api/v1/docs')

    except Exception as e:
        print(f'\n❌ Erro durante execução: {e}')


if __name__ == '__main__':
    main()

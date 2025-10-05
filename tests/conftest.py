"""Fixture and environment configurations for testing."""
import hashlib
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.core.database.session import get_session
from apps.core.models.assignment import Assignment
from apps.core.models.authorization import Authorization
from apps.core.models.role import Role
from apps.core.models.transaction import Transaction
from apps.core.models.user import User
from apps.core.startup import app
from apps.core.utils.security import get_password_hash
from apps.ia.models.conversation import Conversation
from apps.ia.models.document import Document
from apps.ia.models.message import Message
from apps.packpage.base_model import Base
from tests.factory.assignment_factory import (
    AssignmentFactory,
    create_assignment,
)
from tests.factory.authorization_factory import (
    AuthorizationFactory,
    create_authorization,
)
from tests.factory.role_factory import RoleFactory
from tests.factory.trasaction_factory import TransactonFactory
from tests.factory.user_factory import UserFactory
from tests.mock.mock_embeddings import MockEmbeddings


@pytest.fixture
def client(session):
    """
    Webclient context for APIRest testing

    Returns:
        TestClient: A FastAPI TestClient instance
    """

    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()

    return TestClient(app)


@pytest.fixture
def session():
    """
    Database session context for testing.

    Yields:
        Session: A SQLAlchemy Session instance
    """
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        # echo=True,
    )

    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    yield Session()
    Base.metadata.drop_all(engine)


@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, _connection_record):
    """
    Defines the foreign keys pragma for SQLite database connections.

    Args:
        dbapi_connection: The database connection object.
        _connection_record: The connection record object.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


@pytest.fixture
def user(session):
    """
    Create a User ingestion for testing.

    Args:
        session (Session): A SQLAlchemy Session instance.

    Returns:
        User: A User instance from the system.
    """
    clr_password = 'testtest'
    user = User(
        username='Teste',
        display_name='User Teste',
        email='teste@test.com',
        password=get_password_hash(clr_password),
        audit_user_ip='0.0.0.0',
        audit_user_login='tester',
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clear_password = clr_password  # type: ignore[attr-defined]
    return user


@pytest.fixture
def other_user(session):
    """
    Create another User ingestion for testing.

    Args:
        session (Session): A SQLAlchemy Session instance.

    Returns:
        User: A User instance from the system.
    """
    clr_password = 'Qwert123'
    user = User(
        username='TesteOutro',
        email='teste_outro@test.com',
        display_name='User Teste Outro',
        password=get_password_hash(clr_password),
        audit_user_ip='0.0.0.0',
        audit_user_login='tester',
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    user.clear_password = clr_password  # type: ignore[attr-defined]
    return user


@pytest.fixture
def user_10(session):
    """
    Create a list of 10 User objects for testing.
    """
    UserFactory.reset_sequence()
    user: list[User] = UserFactory.build_batch(10)
    session.add_all(user)
    session.commit()

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clear_password},
    )
    return response.json()['access_token']


@pytest.fixture
def trasaction(session) -> Transaction:
    """
    Creates a transaction in the database.
    """
    trasaction = TransactonFactory.build()
    session.add(trasaction)
    session.commit()
    session.refresh(trasaction)
    return trasaction


@pytest.fixture
def transaction_200(session):
    """
    Creates 200 transactions in the database.
    """
    TransactonFactory.reset_sequence()
    trasactions: list[Transaction] = TransactonFactory.build_batch(200)
    session.add_all(trasactions)
    session.commit()

    return trasactions


@pytest.fixture
def transaction_10_plus_one(session):
    """
    Creates 10 transactions + 1 with a specific code in the database.
    """
    TransactonFactory.reset_sequence()
    trasactions: list[Transaction] = TransactonFactory.build_batch(10)
    session.add_all(trasactions)
    session.commit()

    trans_test666 = Transaction(
        name='Transação TEST666',
        description='Descrição TEST666',
        operation_code='TEST666',
        audit_user_ip='localhost',
        audit_user_login='tester',
    )

    session.add(trans_test666)
    session.commit()
    trasactions.append(trans_test666)

    return trasactions


@pytest.fixture
def role_10(session):
    """Creates 10 roles in the database."""
    RoleFactory.reset_sequence()
    roles: list[Role] = RoleFactory.build_batch(10)
    session.add_all(roles)
    session.commit()

    return roles


@pytest.fixture
def role(session):
    """
    Creates a role in the database.
    """
    new_role = Role(
        name='ROLE_TEST',
        description='ROLE_TEST',
        audit_user_ip='localhost',
        audit_user_login='tester',
    )
    session.add(new_role)
    session.commit()
    session.refresh(new_role)
    return new_role


@pytest.fixture
def assignment_10(session, user, role_10):
    """
    Creates 10 assignments in the database.
    """
    AssignmentFactory.reset_sequence()
    assignments: list[Assignment] = []

    with session.no_autoflush:
        db_user = session.get(User, user.id)

        for role in role_10:
            db_role = session.get(Role, role.id)
            new_assignment = create_assignment(db_role, db_user)
            assignments.append(new_assignment)

    session.add_all(assignments)
    session.commit()
    return assignments


@pytest.fixture
def authorization_10_plus_one(session, role, transaction_10_plus_one):
    """
    Creates 10 Authorizations in the database.
    """
    AuthorizationFactory.reset_sequence()
    authorizations: list[Authorization] = []

    with session.no_autoflush:
        db_role = session.get(Role, role.id)

        for transaction in transaction_10_plus_one:
            db_transaction = session.get(Transaction, transaction.id)
            new_authorization = create_authorization(db_role, db_transaction)
            authorizations.append(new_authorization)

    session.add_all(authorizations)
    session.commit()
    return authorizations


@pytest.fixture
def conversation(session, user):
    """Create a test conversation."""
    conversation = Conversation(
        str_title="Conversa de Teste",
        str_description="Uma conversa para testes",
        user_id=user.id,
        str_status="active",
        audit_user_ip="127.0.0.1",
        audit_user_login=user.username,
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@pytest.fixture
def conversation_with_messages(session, user):
    """Create a conversation with several messages for testing."""
    conversation = Conversation(
        str_title="Conversa com Mensagens",
        str_description="Conversa com múltiplas mensagens",
        user_id=user.id,
        str_status="active",
        audit_user_ip="127.0.0.1",
        audit_user_login=user.username,
    )
    session.add(conversation)
    session.flush()

    messages = [
        Message(
            txt_content="Primeira mensagem do usuário",
            str_role="user",
            conversation_id=conversation.id,
            str_status="active",
            audit_user_ip="127.0.0.1",
            audit_user_login=user.username,
        ),
        Message(
            txt_content="Resposta do assistente",
            str_role="assistant",
            conversation_id=conversation.id,
            str_status="active",
            audit_user_ip="127.0.0.1",
            audit_user_login=user.username,
        ),
        Message(
            txt_content="Segunda mensagem do usuário",
            str_role="user",
            conversation_id=conversation.id,
            str_status="active",
            audit_user_ip="127.0.0.1",
            audit_user_login=user.username,
        ),
    ]

    session.add_all(messages)
    session.commit()
    session.refresh(conversation)
    return conversation


@pytest.fixture
def document(session, user):
    """Create a test document."""
    content = "Este é um documento de teste para o sistema de RAG."
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    document = Document(
        str_title="Documento de Teste",
        str_filename="teste.txt",
        txt_content=content,
        str_content_type="text/plain",
        json_metadata='{"source": "test", "category": "example"}',
        int_size_bytes=len(content.encode("utf-8")),
        str_content_hash=content_hash,
        str_status="active",
        audit_user_ip="127.0.0.1",
        audit_user_login=user.username,
    )
    session.add(document)
    session.commit()
    session.refresh(document)
    return document


@pytest.fixture
def multiple_conversations(session, user):
    """Create multiple conversations for pagination testing."""
    conversations = []
    for i in range(15):
        conversation = Conversation(
            str_title=f"Conversa {i + 1}",
            str_description=f"Descrição da conversa {i + 1}",
            user_id=user.id,
            str_status="active" if i % 2 == 0 else "archived",
            audit_user_ip="127.0.0.1",
            audit_user_login=user.username,
        )
        conversations.append(conversation)

    session.add_all(conversations)
    session.commit()
    return conversations


@pytest.fixture
def multiple_documents(session, user):
    """Create multiple documents for testing."""
    documents = []
    for i in range(10):
        document = Document(
            str_title=f"Documento {i + 1}",
            str_filename=f"doc_{i + 1}.txt",
            txt_content=f"Conteúdo do documento {i + 1} com informações importantes.",
            str_content_type="text/plain",
            json_metadata=f'{{"source": "test", "index": {i + 1}}}',
            int_size_bytes=len(f"Conteúdo do documento {i + 1}"),
            str_content_hash=f"hash{i + 1}",
            str_status="active",
            audit_user_ip="127.0.0.1",
            audit_user_login=user.username,
        )
        documents.append(document)

    session.add_all(documents)
    session.commit()
    return documents


@pytest.fixture
def mock_rag_embeddings():
    """Mock embeddings for RAG tests that don't call external APIs."""
    with patch(
        "apps.ia.services.rag_service.RAGService._setup_embeddings"
    ) as mock_setup:
        mock_setup.return_value = MockEmbeddings()
        yield

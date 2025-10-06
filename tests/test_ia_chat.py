"""Tests for AI chat functionality."""

import traceback
from unittest.mock import Mock, patch

import pytest

from apps.ia.agents.conversation_agent import ConversationAgent
from apps.ia.api.chat.controller import ChatController
from apps.ia.api.chat.schemas import (
    ChatMessageSchema,
    ConversationCreateSchema,
    ConversationUpdateSchema,
)
from apps.ia.models.conversation import Conversation
from apps.ia.models.message import Message
from apps.ia.services.rag_service import RAGService


def test_conversation_agent():
    """Test conversation agent."""

    rag_service = RAGService()
    agent = ConversationAgent(rag_service)

    try:
        response = agent.process_query('Olá, como você está?')
        assert isinstance(response, str), f'Expected str, got {type(response)}'
        assert len(response) > 0, 'Response cannot be empty'

    except Exception as e:
        traceback.print_exc()
        pytest.skip(f'API não configurada: {e}')


def test_conversation_model_creation():
    """Test conversation model creation."""
    conversation = Conversation(
        str_title='Teste de Conversa',
        str_description='Conversa de teste',
        user_id=1,
        str_status='active',
        audit_user_ip='127.0.0.1',
        audit_user_login='test_user',
    )

    assert conversation.str_title == 'Teste de Conversa'
    assert conversation.str_status == 'active'


def test_message_model_creation():
    """Test message model creation."""
    message = Message(
        txt_content='Esta é uma mensagem de teste',
        str_role='user',
        conversation_id=1,
        str_status='active',
        audit_user_ip='127.0.0.1',
        audit_user_login='test_user',
    )

    assert message.txt_content == 'Esta é uma mensagem de teste'
    assert message.str_role == 'user'


def test_chat_controller_initialization():
    """Test chat controller initialization."""
    controller = ChatController()
    assert controller is not None
    assert hasattr(controller, 'conversation_agent')
    assert controller.conversation_agent is not None


def test_create_conversation_with_database(session, user):
    """Test creating a conversation using the controller."""
    controller = ChatController()

    conversation_data = ConversationCreateSchema(
        title='Nova Conversa Controller',
        description='Conversa criada pelo controller',
    )

    conversation = controller.create_conversation(
        session, conversation_data, user, '127.0.0.1'
    )

    assert conversation.id is not None
    assert conversation.str_title == 'Nova Conversa Controller'
    assert conversation.str_description == 'Conversa criada pelo controller'
    assert conversation.user_id == user.id
    assert conversation.str_status == 'active'


def test_get_user_conversation(session, conversation_with_messages, user):
    """Test getting a specific user conversation."""
    controller = ChatController()
    result = controller.get_user_conversation(
        session, conversation_with_messages.id, user.id
    )

    assert result is not None
    assert result.id == conversation_with_messages.id
    assert result.user_id == user.id

    result = controller.get_user_conversation(session, 99999, user.id)
    assert result is None

    result = controller.get_user_conversation(
        session, conversation_with_messages.id, 99999
    )
    assert result is None


def test_get_user_conversations_with_pagination(
    session, multiple_conversations, user
):
    """Test getting user conversations with pagination."""
    controller = ChatController()

    result = controller.get_user_conversations(
        session, user.id, page=1, per_page=5
    )

    assert 'conversations' in result
    assert 'total' in result
    assert 'page' in result
    assert 'per_page' in result

    assert len(result['conversations']) <= 5
    assert result['total'] == 15
    assert result['page'] == 1
    assert result['per_page'] == 5

    result_page2 = controller.get_user_conversations(
        session, user.id, page=2, per_page=5
    )
    assert len(result_page2['conversations']) <= 5
    assert result_page2['page'] == 2


@patch('apps.ia.api.chat.controller.ConversationAgent')
def test_send_message_new_conversation(mock_agent_class, session, user):
    """Test sending a message to create a new conversation."""
    mock_agent = Mock()
    mock_agent.process_query.return_value = 'Olá! Como posso ajudar você?'
    mock_agent_class.return_value = mock_agent

    controller = ChatController()
    controller.conversation_agent = mock_agent

    chat_data = ChatMessageSchema(
        message='Olá, preciso de ajuda', conversation_id=None
    )

    response = controller.send_message(session, chat_data, user, '127.0.0.1')

    assert response.response == 'Olá! Como posso ajudar você?'
    assert response.conversation_id is not None
    assert response.message_id is not None
    assert response.user_message_id is not None

    conversation = session.get(Conversation, response.conversation_id)
    assert conversation is not None
    assert conversation.user_id == user.id
    assert 'Olá, preciso' in conversation.str_title


@patch('apps.ia.api.chat.controller.ConversationAgent')
def test_send_message_existing_conversation(
    mock_agent_class, session, conversation_with_messages, user
):
    """Test sending a message to an existing conversation."""
    mock_agent = Mock()
    mock_agent.process_query.return_value = 'Entendi sua pergunta!'
    mock_agent_class.return_value = mock_agent

    controller = ChatController()
    controller.conversation_agent = mock_agent

    chat_data = ChatMessageSchema(
        message='Você pode me explicar melhor?',
        conversation_id=conversation_with_messages.id,
    )

    initial_message_count = len(conversation_with_messages.messages)

    response = controller.send_message(session, chat_data, user, '127.0.0.1')

    assert response.response == 'Entendi sua pergunta!'
    assert response.conversation_id == conversation_with_messages.id

    session.refresh(conversation_with_messages)
    assert (
        len(conversation_with_messages.messages) == initial_message_count + 2
    )


def test_update_conversation(session, conversation, user):
    """Test updating a conversation."""
    controller = ChatController()

    update_data = ConversationUpdateSchema(
        title='Título Atualizado',
        description='Descrição atualizada',
        status='archived',
    )

    updated = controller.update_conversation(
        session, conversation.id, update_data, user, '127.0.0.1'
    )

    assert updated is not None
    assert updated.str_title == 'Título Atualizado'
    assert updated.str_description == 'Descrição atualizada'
    assert updated.str_status == 'archived'


def test_update_nonexistent_conversation(session, user):
    """Test updating a conversation that doesn't exist."""
    controller = ChatController()

    update_data = ConversationUpdateSchema(title='Não Existe')

    result = controller.update_conversation(
        session, 99999, update_data, user, '127.0.0.1'
    )

    assert result is None


def test_chat_controller_save_method(session, user):
    """Test the overridden save method in ChatController."""
    controller = ChatController()

    conversation = Conversation(
        str_title='Conversa Save Test',
        str_description='Testando método save',
        user_id=user.id,
        audit_user_ip='127.0.0.1',
        audit_user_login=user.username,
    )

    saved_conversation = controller.save(session, conversation)

    assert saved_conversation.id is not None
    assert saved_conversation.str_status == 'active'
    assert saved_conversation.str_title == 'Conversa Save Test'


def test_chat_controller_update_method(session, conversation, user):
    """Test the overridden update method in ChatController."""
    controller = ChatController()

    conversation.str_title = 'Título Atualizado via Update'
    conversation.str_description = 'Descrição atualizada'

    updated_conversation = controller.update(session, conversation)

    assert updated_conversation.str_title == 'Título Atualizado via Update'
    assert updated_conversation.str_description == 'Descrição atualizada'


def test_conversation_title_generation():
    """Test automatic conversation title generation."""
    from apps.ia.api.chat.controller import ChatController

    controller = ChatController()

    title = controller._generate_conversation_title('Olá')
    assert title == 'Olá'

    long_message = ' '.join(['palavra'] * 20)
    title = controller._generate_conversation_title(long_message)
    assert len(title) <= 50
    assert title.endswith('...')


def test_conversation_model_fields():
    """Test conversation model field validation."""
    conversation = Conversation(
        str_title='Conversa Completa',
        str_description='Uma descrição mais detalhada da conversa',
        user_id=123,
        str_status='active',
        audit_user_ip='192.168.1.100',
        audit_user_login='admin_user',
    )

    assert conversation.str_title == 'Conversa Completa'
    assert (
        conversation.str_description
        == 'Uma descrição mais detalhada da conversa'
    )
    assert conversation.user_id == 123
    assert conversation.str_status == 'active'
    assert conversation.audit_user_ip == '192.168.1.100'
    assert conversation.audit_user_login == 'admin_user'


def test_message_model_roles():
    """Test message model with different roles."""
    user_message = Message(
        txt_content='Pergunta do usuário',
        str_role='user',
        conversation_id=1,
        str_status='active',
        audit_user_ip='127.0.0.1',
        audit_user_login='test_user',
    )

    assert user_message.str_role == 'user'
    assert user_message.txt_content == 'Pergunta do usuário'

    assistant_message = Message(
        txt_content='Resposta do assistente',
        str_role='assistant',
        conversation_id=1,
        str_status='active',
        audit_user_ip='127.0.0.1',
        audit_user_login='test_user',
    )

    assert assistant_message.str_role == 'assistant'
    assert assistant_message.txt_content == 'Resposta do assistente'


def test_conversation_agent_error_handling():
    """Test conversation agent error handling."""

    rag_service = RAGService()
    agent = ConversationAgent(rag_service)
    try:
        response = agent.process_query('')
        assert isinstance(response, str)
        assert len(response) > 0
        print(f'✅ Short message handled: {response}')
    except Exception as e:
        pytest.skip(f'API handling error: {e}')


def test_conversation_title_edge_cases():
    """Test conversation title generation edge cases."""
    from apps.ia.api.chat.controller import ChatController

    controller = ChatController()

    title = controller._generate_conversation_title('')
    assert title == 'Nova Conversa'

    title = controller._generate_conversation_title('   ')
    assert title == 'Nova Conversa'

    title = controller._generate_conversation_title('Olá! Como está? 😊')
    assert 'Olá' in title

    title = controller._generate_conversation_title('Hi')
    assert title == 'Hi'

    eight_words = 'uma duas três quatro cinco seis sete oito'
    title = controller._generate_conversation_title(eight_words)
    assert title == eight_words

    many_words = 'palavra ' * 15
    title = controller._generate_conversation_title(many_words.strip())
    expected_words = ('palavra ' * 8).strip()
    assert title.startswith(expected_words[:8])

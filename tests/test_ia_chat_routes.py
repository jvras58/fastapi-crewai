"""Tests for AI chat routes and endpoints."""

from unittest.mock import Mock, patch

from fastapi import status

# =============================================================================
# Chat Endpoint Tests
# =============================================================================


@patch('apps.ia.api.chat.controller.ConversationAgent')
def test_send_chat_message_new_conversation(mock_agent_class, client, token, user):
    """Test sending a chat message to create a new conversation."""
    mock_agent = Mock()
    mock_agent.chat.return_value = "Olá! Como posso ajudar você hoje?"
    mock_agent_class.return_value = mock_agent

    chat_data = {
        "message": "Olá, preciso de ajuda com FastAPI",
        "conversation_id": None
    }

    response = client.post(
        "/ia/chat",
        json=chat_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "response" in data
    assert "conversation_id" in data
    assert "message_id" in data
    assert "user_message_id" in data
    assert data["response"] == "Olá! Como posso ajudar você hoje?"
    assert isinstance(data["conversation_id"], int)


@patch('apps.ia.api.chat.controller.ConversationAgent')
def test_send_chat_message_existing_conversation(
    mock_agent_class, client, token, user, conversation
):
    """Test sending a message to an existing conversation."""
    mock_agent = Mock()
    mock_agent.chat.return_value = "Entendi sua pergunta!"
    mock_agent_class.return_value = mock_agent

    chat_data = {
        "message": "Você pode me explicar melhor?",
        "conversation_id": conversation.id
    }

    response = client.post(
        "/ia/chat",
        json=chat_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["conversation_id"] == conversation.id
    assert data["response"] == "Entendi sua pergunta!"


def test_send_chat_message_unauthorized(client):
    """Test sending a chat message without authentication."""
    chat_data = {
        "message": "Olá, preciso de ajuda",
    }

    response = client.post("/ia/chat", json=chat_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_send_chat_message_invalid_data(client, token):
    """Test sending invalid chat data."""
    response = client.post(
        "/ia/chat",
        json={"message": ""},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = client.post(
        "/ia/chat",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_send_chat_message_invalid_conversation_id(client, token):
    """Test sending message to non-existent conversation."""
    chat_data = {
        "message": "Olá, preciso de ajuda",
        "conversation_id": 99999
    }

    response = client.post(
        "/ia/chat",
        json=chat_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# =============================================================================
# Conversation Management Tests
# =============================================================================


def test_create_conversation(client, token):
    """Test creating a new conversation."""
    conversation_data = {
        "title": "Nova Conversa via API",
        "description": "Conversa criada através da API"
    }

    response = client.post(
        "/ia/conversations",
        json=conversation_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["str_title"] == "Nova Conversa via API"
    assert data["str_description"] == "Conversa criada através da API"
    assert "id" in data
    assert data["str_status"] == "active"


def test_create_conversation_unauthorized(client):
    """Test creating a conversation without authentication."""
    conversation_data = {
        "title": "Conversa não autorizada",
        "description": "Esta deve falhar"
    }

    response = client.post("/ia/conversations", json=conversation_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_conversation_invalid_data(client, token):
    """Test creating conversation with invalid data."""
    # Empty title
    response = client.post(
        "/ia/conversations",
        json={"title": "", "description": "Teste"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Missing title
    response = client.post(
        "/ia/conversations",
        json={"description": "Teste"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_list_conversations(client, token, multiple_conversations):
    """Test listing user conversations."""
    response = client.get(
        "/ia/conversations",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert "conversations" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data

    assert data["total"] == 15  # Created in fixture
    assert len(data["conversations"]) <= 20  # Default page size


def test_list_conversations_pagination(client, token, multiple_conversations):
    """Test conversation pagination."""
    response = client.get(
        "/ia/conversations?page=1&per_page=5",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["page"] == 1
    assert data["per_page"] == 5
    assert len(data["conversations"]) <= 5


def test_list_conversations_unauthorized(client):
    """Test listing conversations without authentication."""
    response = client.get("/ia/conversations")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_conversation_with_messages(client, token, conversation_with_messages):
    """Test getting a specific conversation with messages."""
    response = client.get(
        f"/ia/conversations/{conversation_with_messages.id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["id"] == conversation_with_messages.id
    assert "messages" in data
    assert len(data["messages"]) == 3  # Created in fixture


def test_get_nonexistent_conversation(client, token):
    """Test getting a conversation that doesn't exist."""
    response = client.get(
        "/ia/conversations/99999",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_conversation_unauthorized(client, conversation):
    """Test getting conversation without authentication."""
    response = client.get(f"/ia/conversations/{conversation.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_conversation(client, token, conversation):
    """Test updating a conversation."""
    update_data = {
        "title": "Título Atualizado via API",
        "description": "Descrição atualizada",
        "status": "archived"
    }

    response = client.put(
        f"/ia/conversations/{conversation.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["str_title"] == "Título Atualizado via API"
    assert data["str_description"] == "Descrição atualizada"
    assert data["str_status"] == "archived"


def test_update_nonexistent_conversation(client, token):
    """Test updating a conversation that doesn't exist."""
    update_data = {
        "title": "Não existe"
    }

    response = client.put(
        "/ia/conversations/99999",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_conversation_unauthorized(client, conversation):
    """Test updating conversation without authentication."""
    update_data = {
        "title": "Não autorizado"
    }

    response = client.put(
        f"/ia/conversations/{conversation.id}",
        json=update_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_conversation_invalid_data(client, token, conversation):
    """Test updating conversation with invalid data."""
    # Invalid status
    response = client.put(
        f"/ia/conversations/{conversation.id}",
        json={"status": "invalid_status"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Title too long (> 255 chars)
    long_title = "a" * 256
    response = client.put(
        f"/ia/conversations/{conversation.id}",
        json={"title": long_title},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# =============================================================================
# Integration Tests
# =============================================================================


@patch('apps.ia.api.chat.controller.ConversationAgent')
def test_full_conversation_flow(mock_agent_class, client, token, user):
    """Test complete conversation flow: create, send messages, update."""
    # Mock the agent response
    mock_agent = Mock()
    mock_agent.chat.return_value = "Resposta da IA"
    mock_agent_class.return_value = mock_agent

    # 1. Create conversation
    conversation_data = {
        "title": "Conversa Completa",
        "description": "Teste do fluxo completo"
    }

    response = client.post(
        "/ia/conversations",
        json=conversation_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    conversation_id = response.json()["id"]

    # 2. Send first message
    chat_data = {
        "message": "Primeira mensagem",
        "conversation_id": conversation_id
    }

    response = client.post(
        "/ia/chat",
        json=chat_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["conversation_id"] == conversation_id

    # 3. Send second message
    chat_data = {
        "message": "Segunda mensagem",
        "conversation_id": conversation_id
    }

    response = client.post(
        "/ia/chat",
        json=chat_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK

    # 4. Get conversation with messages
    response = client.get(
        f"/ia/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["messages"]) == 4  # 2 user + 2 assistant messages

    # 5. Update conversation
    update_data = {
        "title": "Conversa Finalizada",
        "status": "archived"
    }

    response = client.put(
        f"/ia/conversations/{conversation_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["str_title"] == "Conversa Finalizada"
    assert response.json()["str_status"] == "archived"

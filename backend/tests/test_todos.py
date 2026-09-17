"""Todo tests."""

import pytest
from httpx import AsyncClient
from app.core.security import get_password_hash
from app.models.user import User


async def get_auth_token(client: AsyncClient, email: str = "todo@example.com") -> str:
    """Helper to register and get auth token."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_todo(client: AsyncClient):
    """Test creating a new todo."""
    token = await get_auth_token(client, "create@example.com")

    response = await client.post(
        "/api/v1/todos",
        json={"title": "Test Todo", "description": "A test todo item"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "A test todo item"
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_get_todos(client: AsyncClient):
    """Test getting todo list."""
    token = await get_auth_token(client, "list@example.com")

    # Create a todo first
    await client.post(
        "/api/v1/todos",
        json={"title": "List Todo"},
        headers={"Authorization": f"Bearer {token}"},
    )

    # Get todos
    response = await client.get(
        "/api/v1/todos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient):
    """Test updating a todo."""
    token = await get_auth_token(client, "update@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Update Me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Update it
    response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Updated Title", "completed": True},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient):
    """Test deleting a todo."""
    token = await get_auth_token(client, "delete@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Delete Me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Delete it
    response = await client.delete(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_single_todo(client: AsyncClient):
    """Test getting a single todo by ID."""
    token = await get_auth_token(client, "single@example.com")

    # Create a todo
    create_response = await client.post(
        "/api/v1/todos",
        json={"title": "Single Todo", "description": "Get me"},
        headers={"Authorization": f"Bearer {token}"},
    )
    todo_id = create_response.json()["id"]

    # Get it
    response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Single Todo"


@pytest.mark.asyncio
async def test_user_cannot_access_another_users_todo(
    client: AsyncClient,
    user,
    auth_headers_for,
    db_session,
):
    # User A creates a todo
    user_a_headers = auth_headers_for(user)

    create_response = await client.post(
        "/api/v1/todos",
        json={
            "title": "Private Todo",
            "description": "User A's private todo",
        },
        headers=user_a_headers,
    )

    assert create_response.status_code == 201
    todo_id = create_response.json()["id"]

    # Create User B
    user_b = User(
        email="user-b@example.com",
        hashed_password=get_password_hash("password123"),
    )
    db_session.add(user_b)
    await db_session.commit()
    await db_session.refresh(user_b)

    user_b_headers = auth_headers_for(user_b)

    # User B cannot read User A's todo
    get_response = await client.get(
        f"/api/v1/todos/{todo_id}",
        headers=user_b_headers,
    )
    assert get_response.status_code == 404

    # User B cannot update User A's todo
    update_response = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Hacked Todo"},
        headers=user_b_headers,
    )
    assert update_response.status_code == 404

    # User B cannot delete User A's todo
    delete_response = await client.delete(
        f"/api/v1/todos/{todo_id}",
        headers=user_b_headers,
    )
    assert delete_response.status_code == 404
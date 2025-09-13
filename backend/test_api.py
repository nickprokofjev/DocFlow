"""
Basic API tests for DocFlow backend.
"""
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
import tempfile

from main import app
from models import Base
from auth import get_db

# Test database URL - use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)

async def get_test_db():
    """Override database dependency for testing."""
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Override the dependency
app.dependency_overrides[get_db] = get_test_db

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def setup_database():
    """Set up test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(setup_database):
    """Create test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

class TestAPI:
    """Test class for API endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "DocFlow backend is running"
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    @pytest.mark.asyncio
    async def test_create_party(self, client: AsyncClient):
        """Test party creation."""
        party_data = {
            "name": "Test Company",
            "inn": "1234567890",
            "kpp": "123456789",
            "address": "Test Address",
            "role": "customer"
        }
        response = await client.post("/api/v1/parties/", json=party_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == party_data["name"]
        assert data["role"] == party_data["role"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_get_parties(self, client: AsyncClient):
        """Test getting parties list."""
        # First create a party
        party_data = {
            "name": "Test Company 2",
            "role": "contractor"
        }
        await client.post("/api/v1/parties/", json=party_data)
        
        # Then get parties list
        response = await client.get("/api/v1/parties/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_party_validation(self, client: AsyncClient):
        """Test party validation."""
        # Test invalid role
        invalid_party = {
            "name": "Test Company",
            "role": "invalid_role"
        }
        response = await client.post("/api/v1/parties/", json=invalid_party)
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_party(self, client: AsyncClient):
        """Test getting non-existent party."""
        response = await client.get("/api/v1/parties/99999")
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__])
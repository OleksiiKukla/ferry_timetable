from fastapi import status
from httpx import AsyncClient

TEST_URL = "/example/"


async def test_example_endpoint(ac: AsyncClient):
    response = await ac.get(TEST_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["example"] == "Hi, teammates!"

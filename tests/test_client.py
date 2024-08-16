from unittest.mock import AsyncMock

import aiohttp
import pytest

from tastytrade.client import TastyTradeClient


class TestTastyTradeClient:
    # Creating a TastyTradeClient instance with sandbox mode enabled
    @pytest.mark.asyncio
    async def test_create_instance_sandbox_enabled(self, mocker):
        mocker.patch(
            "tastytrade.client._get_base_url", return_value="https://sandbox.api"
        )
        client = await TastyTradeClient.create(sandbox=True)
        assert client.base_url == "https://sandbox.api"
        await client.close()

    # Creating a TastyTradeClient instance with sandbox mode disabled
    @pytest.mark.asyncio
    async def test_create_instance_sandbox_disabled(self, mocker):
        mocker.patch("tastytrade.client._get_base_url", return_value="https://api")
        client = await TastyTradeClient.create(sandbox=False)
        assert client.base_url == "https://api"
        await client.close()

    # Successfully making a GET request to an endpoint
    @pytest.mark.asyncio
    async def test_get_request_success(self, mocker):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"key": "value"}
        mock_session = mocker.patch("aiohttp.ClientSession", autospec=True)
        mock_session.return_value.request.return_value.__aenter__.return_value = (
            mock_response
        )

        client = await TastyTradeClient.create(sandbox=True)
        response = await client.get("/test-endpoint")
        assert response == {"key": "value"}
        await client.close()

    # Successfully making a POST request to an endpoint with JSON data
    @pytest.mark.asyncio
    async def test_post_request_success(self, mocker):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"key": "value"}
        mock_session = mocker.patch("aiohttp.ClientSession")
        mock_session.return_value.request.return_value.__aenter__.return_value = (
            mock_response
        )

        client = await TastyTradeClient.create(sandbox=True)
        response = await client.post("/test-endpoint", json={"data": "test"})
        assert response == {"key": "value"}
        await client.close()

    # Successfully making a PUT request to an endpoint with JSON data
    @pytest.mark.asyncio
    async def test_put_request_success(self, mocker):
        mock_response = AsyncMock()
        mock_response.json.return_value = {"key": "value"}
        mock_session = mocker.patch("aiohttp.ClientSession")
        mock_session.return_value.request.return_value.__aenter__.return_value = (
            mock_response
        )

        client = await TastyTradeClient.create(sandbox=True)
        response = await client.put("/test-endpoint", json={"data": "test"})
        assert response == {"key": "value"}
        await client.close()

    # Handling the session being already closed when close() is called
    @pytest.mark.asyncio
    async def test_close_already_closed_session(self, mocker):
        client = await TastyTradeClient.create(sandbox=True)
        await client.session.close()

        result = await client.close()
        assert result is None

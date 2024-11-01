import asyncio
from database import AsyncSessionLocal, init_db
from models import QueueRequest


async def populate():
    await init_db()
    async with AsyncSessionLocal() as session:
        test_requests = [
            QueueRequest(uri="/wiki/Main_Page", method="GET", params=None, headers={"Accept": "text/html"}),
            QueueRequest(
                uri="/wiki/Python_(programming_language)",
                method="GET",
                params=None,
                headers={"Accept": "application/json"},
            ),
            QueueRequest(uri="/nonexistent_page", method="GET", params=None, headers={"Accept": "text/html"}),
            QueueRequest(uri="/wiki/SQL", method="GET", params=None, headers={"Accept": "text/html"}),
            QueueRequest(uri="/wiki/Database", method="GET", params=None, headers={"Accept": "text/html"}),
            QueueRequest(
                uri="/wiki/Web_service",
                method="GET",
                params={"section": "REST"},
                headers={"Accept": "application/json"},
            ),
            QueueRequest(
                uri="/wiki/HTTP", method="POST", params=None, headers={"Content-Type": "application/json"}
            ),
            QueueRequest(
                uri="/wiki/API",
                method="GET",
                params={"format": "json"},
                headers={"Accept": "application/json"},
            ),
            QueueRequest(
                uri="/wiki/Microservices",
                method="GET",
                params={"section": "Architecture"},
                headers={"Accept": "application/json"},
            ),
            QueueRequest(
                uri="/wiki/REST",
                method="GET",
                params={"format": "json"},
                headers={"Accept": "application/json"},
            ),
            QueueRequest(
                uri="/wiki/GraphQL",
                method="POST",
                params=None,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
            ),
            QueueRequest(
                uri="/wiki/Docker",
                method="GET",
                params={"section": "Containers"},
                headers={"Accept": "text/html"},
            ),
            QueueRequest(
                uri="/wiki/Kubernetes", method="GET", params=None, headers={"Accept": "application/json"}
            ),
        ]
        session.add_all(test_requests)
        await session.commit()
        print("Test data populated.")


if __name__ == "__main__":
    asyncio.run(populate())

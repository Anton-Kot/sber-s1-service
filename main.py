import asyncio
import logging
from typing import Optional, NamedTuple
import aiohttp
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from database import AsyncSessionLocal, init_db, config
from models import QueueRequest, QueueResponse


logging.basicConfig(level=getattr(logging, config["logging"]["level"].upper(), logging.INFO))
logger = logging.getLogger(__name__)


service_s2 = config["service_s2"]
concurrency_limit = config["concurrency"]["max_concurrent_requests"]
fetch_timeout = service_s2["timeout"]


semaphore = asyncio.Semaphore(concurrency_limit)


class FetchResult(NamedTuple):
    status_code: Optional[int]
    body: Optional[str]
    error: Optional[str]


async def fetch(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    params: Optional[dict],
    headers: Optional[dict],
    timeout: int,
) -> FetchResult:
    try:
        async with session.request(
            method=method, url=url, params=params, headers=headers, timeout=timeout
        ) as response:
            return FetchResult(status_code=response.status, body=await response.text(), error=None)
    except asyncio.TimeoutError:
        return FetchResult(status_code=None, body=None, error="Timeout")
    except Exception as e:
        return FetchResult(status_code=None, body=None, error=str(e))


async def update_request_status(request: QueueRequest, error: str | None) -> None:
    if not error:
        request.status = "completed"
        logger.info("Request ID %s completed", request.id)
        return

    request.retries += 1
    request.status = "failed" if request.retries >= 3 else "pending"
    logger.error("Request ID %s failed with error: %s", request.id, error)


async def process_request(request: QueueRequest, db_session):
    async with semaphore:
        async with aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(service_s2["login"], service_s2["password"])
        ) as session:
            full_url = service_s2["url"].rstrip("/") + "/" + request.uri.lstrip("/")
            logger.info("Processing Request ID %s: %s", request.id, full_url)

            result = await fetch(
                session, request.method.upper(), full_url, request.params, request.headers, fetch_timeout
            )

            response = QueueResponse(
                request_id=request.id, status_code=result.status_code, body=result.body, error=result.error
            )
            db_session.add(response)

            await update_request_status(request, result.error)
            await db_session.commit()


async def worker():
    async with AsyncSessionLocal() as db_session:
        while True:
            try:
                # sqlite3: блокирует всю базу для UPDATE
                # postgresql: блокирует через WITH FOR UPDATE
                subquery = (
                    select(QueueRequest.id)
                    .where(QueueRequest.status == "pending")
                    .limit(1)
                    .with_for_update(skip_locked=True)
                    .scalar_subquery()
                )
                stmt = (
                    update(QueueRequest)
                    .where(QueueRequest.id == subquery)
                    .values(status="processing")
                    .returning(QueueRequest)
                )
                result = await db_session.execute(stmt)
                request = result.scalar()

                if request is None:
                    logger.info("Worker %s: No pending requests. Closing.", id(asyncio.current_task()))
                    break

                await db_session.commit()

                await process_request(request, db_session)

            except SQLAlchemyError as e:
                logger.error("Database error: %s", e)
                await db_session.rollback()
            except Exception as e:
                logger.exception("Unexpected error: %s", e)


async def main():
    await init_db()
    tasks = []
    for _ in range(concurrency_limit):
        task = asyncio.create_task(worker())
        tasks.append(task)
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service stopped by user.")

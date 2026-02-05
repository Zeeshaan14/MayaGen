import asyncio
import os
import logging
from datetime import datetime
from sqlmodel import select
from sqlalchemy import text
from app.database import get_session_context
from app.models import Image, JobStatus
from app.core import config
from app.services.comfy_client import ComfyUIProvider

# Setup Logging
logger = logging.getLogger("worker")

provider = ComfyUIProvider(config.COMFYUI["server_address"])

async def process_job(image_id: int):
    """
    Processes a single image job.
    """
    async with get_session_context() as session:
        # Re-fetch image to get details
        result = await session.execute(select(Image).where(Image.id == image_id))
        job = result.scalars().first()
        
        if not job:
            logger.error(f"Job {image_id} not found after locking.")
            return

        logger.info(f"Starting Job {job.id} | Prompt: {job.prompt[:30]}...")
        
        try:
            # 1. Prepare Paths
            safe_category = job.category
            category_dir = os.path.join(config.OUTPUT_FOLDER, safe_category)
            os.makedirs(category_dir, exist_ok=True)
            
            # Construct full absolute path
            full_output_path = os.path.join(category_dir, job.filename)
            
            # 2. Check Provider
            if job.provider == "comfyui":
                workflow_path = config.WORKFLOWS.get(job.model, config.WORKFLOWS["sd15"])
                
                # EXECUTE GENERATION
                # We pass the full path so ComfyClient saves it in the right folder
                await asyncio.to_thread(
                    provider.generate, 
                    job.prompt, 
                    full_output_path, 
                    job.width, 
                    job.height, 
                    workflow_path
                )
                
            else:
                # Mock
                await asyncio.sleep(2)
                logger.info("Mock generation complete")

            # 3. Update Success
            job.status = JobStatus.COMPLETED
            job.file_path = full_output_path # Save the absolute path
            job.updated_at = datetime.utcnow()
            session.add(job)
            await session.commit()
            logger.info(f"Job {job.id} COMPLETED.")

        except Exception as e:
            logger.error(f"Job {job.id} FAILED: {e}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            session.add(job)
            await session.commit()

async def worker_loop():
    logger.info("Worker started inside Server Process...")
    
    while True:
        try:
            async with get_session_context() as session:
                # ACID Transaction for Queue Popping
                statement = text("""
                    UPDATE image
                    SET status = 'PROCESSING'
                    WHERE id = (
                        SELECT id
                        FROM image
                        WHERE status = 'PENDING'
                        ORDER BY created_at ASC
                        LIMIT 1
                        FOR UPDATE SKIP LOCKED
                    )
                    RETURNING id;
                """)
                
                result = await session.execute(statement)
                row = result.first()
                
                if row:
                    job_id = row[0]
                    await session.commit() 
                    
                    # Process as a background task so we don't block the loop from picking up others?
                    # User request: "picks that calls the comfyui... until it gets response"
                    # If we wait, we process 1 by 1. That seems to be the request "simple approach".
                    await process_job(job_id)
                else:
                    await session.commit()
                    # No jobs, sleep
                    await asyncio.sleep(1)
                    
        except Exception as e:
            logger.error(f"Worker Loop Error: {e}")
            await asyncio.sleep(5)

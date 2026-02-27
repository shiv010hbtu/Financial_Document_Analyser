# tasks_worker.py
## Celery Tasks — Background me CrewAI run karega

import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from celery_worker import celery_app
from database import db_manager
from crewai import Crew, Process
from agents import financial_analyst
from tasks import analyze_financial_document as analyze_task


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_document_task(self, job_id: str, query: str, file_path: str):
    """
    Background Celery task — financial document analysis karta hai.
    
    Args:
        job_id: Unique ID for tracking in MongoDB
        query: User ka analysis query
        file_path: PDF file ka path
    
    Returns:
        dict: Analysis result
    """
    try:
        # Status: processing mein update karo
        db_manager.update_job_status(job_id, "processing")

        # CrewAI Crew banao aur run karo
        financial_crew = Crew(
            agents=[financial_analyst],
            tasks=[analyze_task],
            process=Process.sequential,
        )

        result = financial_crew.kickoff({
            'query': query,
            'file_path': file_path
        })

        analysis_text = str(result)

        # Success result MongoDB mein save karo
        db_manager.update_job_result(
            job_id=job_id,
            status="completed",
            result=analysis_text
        )

        # Uploaded file cleanup
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "job_id": job_id,
            "status": "completed",
            "analysis": analysis_text
        }

    except Exception as exc:
        # Failure MongoDB mein save karo
        db_manager.update_job_status(
            job_id,
            "failed",
            error=str(exc)
        )

        # File cleanup on failure bhi
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

        # Retry karo agar retries baaki hain
        raise self.retry(exc=exc)

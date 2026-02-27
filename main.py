# from fastapi import FastAPI, File, UploadFile, Form, HTTPException
# import os
# import uuid
# import asyncio

# from crewai import Crew, Process
# from agents import financial_analyst
# from tasks import analyze_financial_document as analyze_task  # FIX 1: "task" → "tasks" (correct filename) + alias to avoid name conflict with endpoint

# app = FastAPI(title="Financial Document Analyzer")

# def run_crew(query: str, file_path: str = "data/sample.pdf"):
#     """To run the whole crew"""
#     financial_crew = Crew(
#         agents=[financial_analyst],
#         tasks=[analyze_task],  # FIX 2: use aliased task name — was conflicting with endpoint function name
#         process=Process.sequential,
#     )

#     result = financial_crew.kickoff({'query': query, 'file_path': file_path})  # FIX 3: file_path was accepted but never passed to crew — now included
#     return result

# @app.get("/")
# async def root():
#     """Health check endpoint"""
#     return {"message": "Financial Document Analyzer API is running"}

# @app.post("/analyze")
# async def analyze_document(  # FIX 4: renamed from "analyze_financial_document" → "analyze_document" to avoid conflict with imported task
#     file: UploadFile = File(...),
#     query: str = Form(default="Analyze this financial document for investment insights")
# ):
#     """Analyze financial document and provide comprehensive investment recommendations"""

#     file_id = str(uuid.uuid4())
#     file_path = f"data/financial_document_{file_id}.pdf"

#     try:
#         # Ensure data directory exists
#         os.makedirs("data", exist_ok=True)

#         # Save uploaded file
#         with open(file_path, "wb") as f:
#             content = await file.read()
#             f.write(content)

#         # FIX 5: Validate query properly — check None first, then empty string
#         if query is None or query.strip() == "":
#             query = "Analyze this financial document for investment insights"

#         # Process the financial document with all analysts
#         response = run_crew(query=query.strip(), file_path=file_path)

#         return {
#             "status": "success",
#             "query": query,
#             "analysis": str(response),
#             "file_processed": file.filename
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")

#     finally:
#         # Clean up uploaded file
#         if os.path.exists(file_path):
#             try:
#                 os.remove(file_path)
#             except:
#                 pass  # Ignore cleanup errors

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)  # FIX 6: pass "main:app" as string — reload=True requires string reference, not app object directly
# main.py
## FastAPI Application — Queue Worker + MongoDB Integration ke saath

import os
import uuid
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from crewai import Crew, Process
from agents import financial_analyst
from tasks import analyze_financial_document as analyze_task

# Bonus Feature imports
from database import db_manager                        # MongoDB manager
from tasks_worker import analyze_document_task         # Celery background task

app = FastAPI(
    title="Financial Document Analyzer",
    description="AI-powered financial analysis with Queue Worker + MongoDB",
    version="2.0.0"
)


# ─── ORIGINAL SYNC FUNCTION (Backward Compatibility) ─────────────────────────

def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """Synchronous crew run — direct analysis (no queue)"""
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_task],
        process=Process.sequential,
    )
    result = financial_crew.kickoff({'query': query, 'file_path': file_path})
    return result


# ─── HEALTH CHECK ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}


# ─── ORIGINAL ENDPOINT (Synchronous — Direct Analysis) ───────────────────────

@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """
    Synchronous analysis — result seedha return karta hai.
    Ek request ke liye theek hai, concurrent requests ke liye /analyze/async use karo.
    """
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        if query is None or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # MongoDB mein job create karo
        job_id = db_manager.create_job(
            query=query.strip(),
            filename=file.filename
        )
        db_manager.save_user_query(
            query=query.strip(),
            filename=file.filename,
            job_id=job_id
        )

        # Direct CrewAI run karo
        response = run_crew(query=query.strip(), file_path=file_path)
        analysis_text = str(response)

        # Result MongoDB mein save karo
        db_manager.update_job_result(
            job_id=job_id,
            status="completed",
            result=analysis_text
        )

        return {
            "status": "success",
            "job_id": job_id,
            "query": query,
            "analysis": analysis_text,
            "file_processed": file.filename
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing financial document: {str(e)}"
        )

    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass


# ─── BONUS: ASYNC QUEUE ENDPOINT ─────────────────────────────────────────────

@app.post("/analyze/async")
async def analyze_document_async(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """
    BONUS FEATURE: Async Queue-based analysis.
    
    - File upload hote hi job_id return karta hai
    - Analysis background mein Celery worker karta hai
    - Multiple concurrent requests handle kar sakta hai
    - /jobs/{job_id} se result check karo
    """
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"

    try:
        os.makedirs("data", exist_ok=True)

        # File save karo
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        if query is None or query.strip() == "":
            query = "Analyze this financial document for investment insights"

        # MongoDB mein job create karo
        job_id = db_manager.create_job(
            query=query.strip(),
            filename=file.filename
        )
        db_manager.save_user_query(
            query=query.strip(),
            filename=file.filename,
            job_id=job_id
        )

        # Celery queue mein task submit karo — background mein chalega
        analyze_document_task.apply_async(
            args=[job_id, query.strip(), file_path],
            queue="financial_analysis"
        )

        # Turant job_id return karo — wait nahi karna
        return {
            "status": "queued",
            "job_id": job_id,
            "message": "Analysis queued successfully. Use /jobs/{job_id} to check status.",
            "check_status_url": f"/jobs/{job_id}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error queuing analysis: {str(e)}"
        )


# ─── BONUS: JOB STATUS ENDPOINTS ─────────────────────────────────────────────

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    BONUS FEATURE: Job status aur result check karo.
    
    Status flow: queued → processing → completed/failed
    """
    job = db_manager.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return job


@app.get("/jobs")
async def get_all_jobs(limit: int = 50):
    """
    BONUS FEATURE: Saare recent analysis jobs dekho.
    """
    jobs = db_manager.get_all_jobs(limit=limit)
    return {
        "total": len(jobs),
        "jobs": jobs
    }


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    BONUS FEATURE: Job delete karo database se.
    """
    deleted = db_manager.delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {"message": f"Job {job_id} deleted successfully"}


# ─── BONUS: HISTORY + STATS ENDPOINTS ────────────────────────────────────────

@app.get("/history")
async def get_query_history(limit: int = 20):
    """
    BONUS FEATURE: User query history dekho MongoDB se.
    """
    history = db_manager.get_query_history(limit=limit)
    return {
        "total": len(history),
        "history": history
    }


@app.get("/stats")
async def get_stats():
    """
    BONUS FEATURE: System statistics — total jobs, success rate, etc.
    """
    stats = db_manager.get_stats()
    return stats


# ─── SERVER START ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
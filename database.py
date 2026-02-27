# database.py
## MongoDB Database Manager — Analysis results aur user data store karta hai

import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import uuid


class DatabaseManager:
    """MongoDB ke saath saari database operations handle karta hai"""

    def __init__(self):
        self.client = None
        self.db = None
        self._connect()

    def _connect(self):
        """MongoDB se connect karo"""
        mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("MONGODB_DB_NAME", "financial_analyzer")

        try:
            self.client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            # Connection test karo
            self.client.admin.command('ping')
            self.db = self.client[db_name]
            print(f"✅ MongoDB connected: {db_name}")
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise

    # ─── ANALYSIS JOBS ────────────────────────────────────────────────────────

    def create_job(self, query: str, filename: str) -> str:
        """
        Naya analysis job create karo.
        
        Returns:
            str: Unique job_id
        """
        job_id = str(uuid.uuid4())
        job = {
            "job_id": job_id,
            "query": query,
            "filename": filename,
            "status": "queued",        # queued → processing → completed/failed
            "result": None,
            "error": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "completed_at": None
        }
        self.db.analysis_jobs.insert_one(job)
        return job_id

    def get_job(self, job_id: str) -> dict:
        """Job details fetch karo job_id se"""
        job = self.db.analysis_jobs.find_one(
            {"job_id": job_id},
            {"_id": 0}  # MongoDB _id hide karo response mein
        )
        return job

    def update_job_status(self, job_id: str, status: str, error: str = None):
        """Job ka status update karo"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if error:
            update_data["error"] = error
        
        self.db.analysis_jobs.update_one(
            {"job_id": job_id},
            {"$set": update_data}
        )

    def update_job_result(self, job_id: str, status: str, result: str):
        """Job ka final result save karo"""
        self.db.analysis_jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "status": status,
                "result": result,
                "updated_at": datetime.utcnow(),
                "completed_at": datetime.utcnow()
            }}
        )

    def get_all_jobs(self, limit: int = 50) -> list:
        """Saare recent jobs fetch karo"""
        jobs = list(
            self.db.analysis_jobs
            .find({}, {"_id": 0})
            .sort("created_at", -1)
            .limit(limit)
        )
        return jobs

    def delete_job(self, job_id: str) -> bool:
        """Job delete karo"""
        result = self.db.analysis_jobs.delete_one({"job_id": job_id})
        return result.deleted_count > 0

    # ─── USER DATA ────────────────────────────────────────────────────────────

    def save_user_query(self, query: str, filename: str, job_id: str):
        """User query history save karo"""
        user_query = {
            "job_id": job_id,
            "query": query,
            "filename": filename,
            "timestamp": datetime.utcnow()
        }
        self.db.user_queries.insert_one(user_query)

    def get_query_history(self, limit: int = 20) -> list:
        """Recent query history fetch karo"""
        history = list(
            self.db.user_queries
            .find({}, {"_id": 0})
            .sort("timestamp", -1)
            .limit(limit)
        )
        return history

    # ─── STATS ────────────────────────────────────────────────────────────────

    def get_stats(self) -> dict:
        """System statistics fetch karo"""
        total = self.db.analysis_jobs.count_documents({})
        completed = self.db.analysis_jobs.count_documents({"status": "completed"})
        failed = self.db.analysis_jobs.count_documents({"status": "failed"})
        queued = self.db.analysis_jobs.count_documents({"status": "queued"})
        processing = self.db.analysis_jobs.count_documents({"status": "processing"})

        return {
            "total_jobs": total,
            "completed": completed,
            "failed": failed,
            "queued": queued,
            "processing": processing,
            "success_rate": f"{(completed/total*100):.1f}%" if total > 0 else "0%"
        }


# Singleton instance — poore app mein ek hi connection
db_manager = DatabaseManager()

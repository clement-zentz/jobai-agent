# app/services/job_services.py

class JobService:
    @staticmethod
    def apply(job_data):
        # logic for applying to a job offer
        # example: call an extern API here, save in db
        return {"status": "applied", "job_title": job_data.title}
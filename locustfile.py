from locust import HttpUser, SequentialTaskSet, task, between
import os
import uuid
from urllib.parse import quote
from dotenv import load_dotenv

# Load variables from .env.dev
load_dotenv(".env.dev")

API_KEY = os.getenv("TEST_API_KEY")
INVITATION_CODE = os.getenv("TEST_INVITATION_CODE")

class SurveyFlow(SequentialTaskSet):
    def on_start(self):
        # Generate a clean, unique email for every user session
        self.email = f"test-performance-{uuid.uuid4().hex[:8]}@gmail.com"
        self.survey_id = 1
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {API_KEY}"
        }

    @task
    def view_survey(self):
        # User opens the survey
        self.client.get(f"/api/surveys/{self.survey_id}/", headers=self.headers)

    @task
    def check_progress(self):
        # User checks if they have previous progress
        encoded_email = quote(self.email)
        with self.client.get(
            f"/api/progress/?email={encoded_email}&survey_id={self.survey_id}", 
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200 or response.status_code == 404:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task
    def complete_screens(self):
        # Simulate moving through multiple screens
        for screen_num in range(1, 5):
            # Simulate the time it takes to read and answer survey questions
            self.wait() 
            self.client.post(
                "/api/progress/",
                headers=self.headers,
                json={
                    "email": self.email,
                    "survey_id": self.survey_id,
                    "current_screen": screen_num,
                    "data": {"guestCodeResponse": {"guestCode": INVITATION_CODE}}
                }
            )

    @task
    def final_submit(self):
        # The high-cost operation at the very end
        with self.client.post(
            "/api/response/", 
            headers=self.headers,
            json={
                "invitation_code": INVITATION_CODE,
                "survey_id": self.survey_id,
                "participant": {
                    "name": "Load Test Participant",
                    "email": self.email,
                    "gender": "m",
                    "birth_range": "1981-1996",
                    "position": "manager"
                },
                "answers": [101, 102, 103, 104] 
            },
            catch_response=True
        ) as response:
            if response.status_code == 400:
                errors = response.json().get("data", {})
                if "non_field_errors" in errors and "already submitted" in str(errors["non_field_errors"]).lower():
                    response.success()
            elif response.status_code == 201:
                response.success()
        
        # End the session for this user after submission
        self.interrupt()

class WebsiteUser(HttpUser):
    tasks = [SurveyFlow]
    # Realistic wait between task executions
    wait_time = between(5, 15) 

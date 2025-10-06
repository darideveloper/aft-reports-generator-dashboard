import os
import uuid
import random

from django.core.management.base import BaseCommand
from django.conf import settings

from rest_framework.authtoken.models import Token

from survey import models

import requests

BASE_FILE = os.path.basename(__file__)


class Command(BaseCommand):
    help = "Simulate responses from users calling the API."
    help += "You must have the project running at the setup host"

    def handle(self, *args, **kwargs):

        # Get random company and survey
        survey = models.Survey.objects.all().first()

        # Get number of users to create
        users_num = input("Enter the number of users to create: ")
        users_num = int(users_num)
        min_score = input("Enter the minimum score: ")
        min_score = int(min_score)
        max_score = input("Enter the maximum score: ")
        max_score = int(max_score)

        # Get api key from db (rest_framework.authtoken)
        api_key = Token.objects.order_by("?").first()

        for _ in range(users_num):
            random_company = models.Company.objects.order_by("?").first()
            random_string = str(uuid.uuid4())

            # Initial api data
            api_data = {
                "invitation_code": random_company.invitation_code,
                "survey_id": survey.id,
                "participant": {
                    "gender": random.choice(["m", "f", "o"]),
                    "birth_range": random.choice(
                        ["1946-1964", "1965-1980", "1981-1996", "1997-2012"]
                    ),
                    "email": f"user_{random_string}@test.com",
                    "name": f"User {random_string}",
                    "position": random.choice(
                        ["director", "manager", "supervisor", "other"]
                    ),
                },
                "answers": [],
            }

            # Set random andswers in each question group
            for question_group in models.QuestionGroup.objects.filter(survey=survey):

                # Calculate correct options number to match score
                questions = models.Question.objects.filter(
                    question_group=question_group
                )
                score = random.randint(min_score, max_score)
                correct_options_num = int(score * len(questions) / 100)

                # Add correct options to answers
                for question in questions[:correct_options_num]:
                    options = models.QuestionOption.objects.filter(question=question)
                    correct_options = options.filter(points=1)
                    for correct_option in correct_options:
                        api_data["answers"].append(correct_option.id)

                # Add incorrect options to answers
                for question in questions[correct_options_num:]:
                    options = models.QuestionOption.objects.filter(question=question)
                    incorrect_options = options.filter(points=0)
                    for incorrect_option in incorrect_options:
                        api_data["answers"].append(incorrect_option.id)

            # Call the API
            response = requests.post(
                f"{settings.HOST}/api/response/",
                json=api_data,
                headers={"Authorization": f"Token {api_key.key}"},
            )
            response.raise_for_status()
            if response.status_code == 201:
                print(response.json())
            else:
                raise Exception("Error creating test response" + response.json())

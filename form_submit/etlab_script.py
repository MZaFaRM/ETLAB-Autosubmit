from bs4 import BeautifulSoup
import requests
from django.core.cache import cache

BASE_URL = "https://kmctce.etlab.app"
SURVEY_BASE = "survey/user"


class ETLab:
    def __init__(self, username, password, cache_key):
        self.cache_key = cache_key
        self.print_status("Starting up everything...")

        self.username = username
        self.password = password
        self.session = requests.Session()
        self.login()

    def login(self):
        login_url = f"{BASE_URL}/user/login"
        login_payload = {
            "LoginForm[username]": self.username,
            "LoginForm[password]": self.password,
        }
        response = self.session.post(login_url, data=login_payload)
        if response.url != f"{BASE_URL}/user/login":
            self.print_status("Logged in successfully...")
        else:
            self.print_status("Login failed...")

    def get_surveys(self):
        response = self.session.get(f"{BASE_URL}/{SURVEY_BASE}/viewall")
        if response.ok:
            with open("formPage.html", "w") as f:
                f.write(response.content.decode("utf-8"))

            with open("formPage.html", "r") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")
            survey_links = soup.find_all("a", string="Do the Survey")
            if survey_links:
                for survey_link in survey_links:
                    survey_url = survey_link.get("href")
                    yield survey_url
            else:
                self.print_status("Survey link not found.")
        else:
            self.print_status("Login failed")

    def complete_surveys(self):
        survey_urls = self.get_surveys()
        for survey_url in survey_urls:
            data_payload = self.get_answers(survey_url)
            if data_payload:
                response = self.session.post(
                    f"{BASE_URL}{survey_url}", data=data_payload
                )
                if response.ok:
                    self.print_status("Survey completed successfully")
                else:
                    self.print_status("Survey completion failed")
            else:
                self.print_status("No data payload found")

    def get_answers(self, survey_url):
        h = f"{BASE_URL}/{survey_url}"
        html_content = self.session.get(f"{BASE_URL}{survey_url}").content.decode(
            "utf-8"
        )
        soup = BeautifulSoup(html_content, "html.parser")
        answer_classes = soup.find_all(class_="answer")
        questions = soup.find_all(class_='question')

        data_payload = {}

        for i, answer_class in enumerate(answer_classes):
            # Find the first radio input within the current "answer" class
            first_radio_input = answer_class.find("input", {"type": "radio"})

            # Check if a radio input is found in the current "answer" class
            if first_radio_input:
                # Extract or simulate selection for the first radio input
                self.print_status("Selected option:")
                self.print_status(f"Question : {questions[i].text.strip()}")
                self.print_status(
                    "Response:", first_radio_input.next_sibling.strip()
                )

                data_payload.update(
                    {first_radio_input["name"]: first_radio_input["value"]}
                )
            else:
                self.print_status(
                    "No radio inputs found in the current 'answer' class."
                )
            self.print_status()

        return data_payload

    def print_status(self, *string):
        current_status = cache.get(self.cache_key, "")
        updated_status = current_status + " ".join(map(str, string)) + "\n"
        cache.set(self.cache_key, updated_status)
        print(updated_status)

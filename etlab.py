from bs4 import BeautifulSoup
import requests
from time import sleep

BASE_URL = "https://kmctce.etlab.app"
SURVEY_BASE = "survey/user"


def print_typing(*joined_text, delay=0.027):
    joined_text = " ".join(joined_text)
    for letter in joined_text:
        print(letter, end="", flush=True)
        sleep(delay)
    print()


def input_typing(*joined_text, delay=0.027):
    joined_text = " ".join(joined_text)
    for letter in joined_text:
        print(letter, end="", flush=True)
        sleep(delay)
    return input()


class ETLab:
    def __init__(self, username, password):
        print_typing("\n\nSetting up everything...")

        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
            }
        )
        self.login()

    def login(self):
        print_typing(f"Contacting {BASE_URL}...")
        login_url = f"{BASE_URL}/user/login"
        login_payload = {
            "LoginForm[username]": self.username,
            "LoginForm[password]": self.password,
        }
        response = self.session.post(login_url, data=login_payload)
        print_typing("Trying to log in...")
        name = self.get_name(response.content.decode("utf-8"))

        if name:
            print_typing(f"Login successful...!")
            print_typing(f"\n\nHello {name.title()}!")
        else:
            print_typing("Login failed...")
            print_typing("Check your credentials and try again.")
            raise ValueError

    def get_name(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        icon_user_tag = soup.find("i", class_="icon-user")
        if icon_user_tag and icon_user_tag.parent:
            name_tag = icon_user_tag.parent.find("span", class_="text")
            if name_tag:
                return name_tag.get_text()
        else:
            return False

    def get_surveys(self):
        print_typing(f"Fetching all the forms for you to fill at {BASE_URL}...")
        response = self.session.get(f"{BASE_URL}/{SURVEY_BASE}/viewall")
        html_content = response.content.decode("utf-8")

        soup = BeautifulSoup(html_content, "html.parser")
        survey_links = soup.find_all("a", string="Do the Survey")
        if survey_links:
            print_typing(f"You have {len(survey_links)} form(s) to fill")
            for survey_link in survey_links:
                survey_url = survey_link.get("href")
                yield survey_url
        else:
            print_typing("No fillable forms found...")

    def complete_surveys(self):
        survey_urls = self.get_surveys()
        for survey_url in survey_urls:
            data_payload = self.get_answers(survey_url)
            if data_payload:
                response = self.session.post(
                    f"{BASE_URL}{survey_url}", data=data_payload
                )
                if response.ok:
                    print_typing("Survey submitted successfully....")
                else:
                    print_typing("Survey submission failed...")
            else:
                print_typing("No questions found to answer...")

    def get_answers(self, survey_url):
        print_typing("Generating answers...\n")
        html_content = self.session.get(f"{BASE_URL}{survey_url}").content.decode(
            "utf-8"
        )
        soup = BeautifulSoup(html_content, "html.parser")
        answer_classes = soup.find_all(class_="answer")
        questions = soup.find_all(class_="question")

        data_payload = {}

        for i, answer_class in enumerate(answer_classes):
            # Find the first radio input within the current "answer" class
            first_radio_input = answer_class.find("input", {"type": "radio"})
            print_typing("Question:", questions[i].text.strip(), delay=0)

            # Check if a radio input is found in the current "answer" class
            if first_radio_input:
                # Extract or simulate selection for the first radio input
                print_typing(
                    "Input:", first_radio_input.next_sibling.strip(), "\n", delay=0
                )  # Extracting the text content

                data_payload.update(
                    {first_radio_input["name"]: first_radio_input["value"]}
                )
            else:
                print_typing("No radio inputs found in the current 'answer' class.\n")
            print_typing()

        return data_payload


if __name__ == "__main__":
    try:
        print_typing("Hi there!\n")
        print_typing("Enter your creds to start auto filling the form...!")
        ETLab(input_typing("Username: "), input_typing("Password: ")).complete_surveys()
    except Exception as e:
        pass

    input_typing("\n\nInput any key to quit...")

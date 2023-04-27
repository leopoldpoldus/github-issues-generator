from github_api import create_issue, create_project_card, get_project_id, add_draft_item_to_project
import os
import openai
import dotenv
import ast
import argparse

working_dir = os.path.dirname(os.path.abspath(__file__))

# import API key from .env file
dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_chat_gpt_response(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages)
    text = response['choices'][0]['message']["content"].strip()  # get the generated text
    return text


def create_message_from_text(text, role: str):
    # check role is valid
    if role not in ["assistant", "user", "system"]:
        raise ValueError(f"Invalid role: {role}, must be one of 'assistant', 'user', 'system'")
    return {
        "role": role,
        "content": text
    }


def generate_project_issue(idea, project_num):
    user_prompt = f"Generate a project task for the following idea:\n\n{idea}\n\n"
    system_prompt = """The task should be in the following format:
    {
        "title": "Task title",
        "body": "Task body",
    }
    Stick to this format as closely as possible.
    The title should be a short, concise summary of the issue.
    The body should be a more detailed description of the issue. It should also include a user story, if possible.
    Dont forget to include quotes around the title and body.
    The body should be nicely formatted using markdown.
    """

    messages = [create_message_from_text(user_prompt, "user"), create_message_from_text(system_prompt, "system")]
    issue_dict_str = get_chat_gpt_response(messages)
    issue_dict = ast.literal_eval(issue_dict_str)

    print(f'Title: {issue_dict["title"]}\nBody: {issue_dict["body"]}')
    return add_draft_item_to_project(project_num, issue_dict["title"], issue_dict["body"])


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser(description='Generate a project issue from an idea')
    parser.add_argument('idea', type=str, help='The idea to generate an issue from')
    # optional arguments
    parser.add_argument('-p', '--project', type=int, help='The project number to add the issue to')
    args = parser.parse_args()

    # get project number
    if args.project:
        project_num = args.project
    else:
        project_num = 1  # get first project by default

    generate_project_issue(args.idea, project_num)

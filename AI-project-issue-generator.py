from github_api import create_issue, create_project_card, get_project_id, add_draft_item_to_project
import os
import openai
import dotenv
import ast
import argparse
import asyncio

working_dir = os.path.dirname(os.path.abspath(__file__))

# import API key from .env file
dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_chat_gpt_response(messages, model="gpt-3.5-turbo"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.1)
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


async def generate_project_issue(idea, project_num, task_context=''):
    print(f"Generating issue for idea: {idea}")
    user_prompt = f"Generate a project task for the following idea:\n\n{idea}\n\n"
    if task_context:
        user_prompt += f"Context: {task_context}\n\n"
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

    # print(f'Title: {issue_dict["title"]}\nBody: {issue_dict["body"]}')
    return await add_draft_item_to_project(project_num, issue_dict["title"], issue_dict["body"])


async def main():
    project_num = input("Enter your Project Number (it shows up in the url of your project page): ")
    task_context = input("Enter the context of your task (optional): ")
    create_new = True

    loop = asyncio.get_running_loop()  # Get the event loop

    while create_new:
        user_idea = await asyncio.get_event_loop().run_in_executor(None, input, "Enter your Task: ")
        user_idea = user_idea.strip()
        if user_idea == "exit":  # exit the program
            create_new = False
        else:
            # generate the issue in a new task
            loop.create_task(generate_project_issue(user_idea, project_num, task_context=task_context))


if __name__ == "__main__":
    asyncio.run(main())

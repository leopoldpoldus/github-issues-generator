import requests
import json
import dotenv
import os

# import ENV variables from .env file
dotenv.load_dotenv()

# Fill in your own values for these variables
owner = os.getenv("OWNER")
repo = os.getenv("REPO")
access_token = os.getenv("ACCESS_TOKEN")


def create_issue(title: str, body: str | None = None, assignee: str | None = None, labels: list[str] | None = None):
    if labels is None:
        labels = []

    # Create a dictionary with the details of the issue you want to create
    issue_data = {
        "title": title,
        "body": body,
        "assignee": assignee,
        "labels": labels
    }

    # Convert the issue data to a JSON string
    json_data = json.dumps(issue_data)

    # Set up the headers for the API request
    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Make the API request to create the issue
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    response = requests.post(url, headers=headers, data=json_data)

    # Check the response status code
    if response.status_code == 201:
        print("Issue created successfully!")
    else:
        print(f"Failed to create issue. Response code: {response.status_code}")

    return response


def create_project_card(note: str, column_id: int = 1):
    # Create a dictionary with the details of the issue you want to create
    data = {
        "note": note
    }

    # Convert the data to a JSON string
    json_data = json.dumps(data)

    # Set up the headers for the API request
    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Make the API request to create the issue
    url = f"https://api.github.com/projects/columns/{column_id}/cards"
    response = requests.post(url, headers=headers, data=json_data)
    print(response.status_code)
    return response


# querys:
# get project id: query = """query {user(login: \"leopoldpoldus\") {projectV2(number: 1){id}}}"""
# get column id


def graphql_request(query: str):
    data = {
        "query": query
    }

    # Convert the data to a JSON string
    json_data = json.dumps(data)

    # Set up the headers for the API request
    headers = {
        "Authorization": f"Token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Make the API request to create the issue
    url = f"https://api.github.com/graphql"
    response = requests.post(url, headers=headers, data=json_data)
    if response.status_code == 200:
        print("GraphQL request successful!")
        print(response.json())
    return response


def get_project_id(project_num: int):
    res = graphql_request(f"query {{user(login: \"{owner}\") {{projectV2(number: {project_num}){{id}}}}}}")
    return res.json()["data"]["user"]["projectV2"]["id"]


def add_draft_item_to_project(project_num: int, title: str, body: str | None = None):
    project_id = get_project_id(project_num)

    query = f"mutation {{addProjectV2DraftIssue(input: {{projectId: \"{project_id}\" title: \"{title}\" body: \"{body}\"}}) {{projectItem {{id}} }} }}"

    return graphql_request(query)

import os
import sys
import json
from anthropic import Anthropic
from github import Github
import base64

def get_file_content(repo, path):
    """Retrieve content of a file from the repository."""
    try:
        file_content = repo.get_contents(path)
        return base64.b64decode(file_content.content).decode('utf-8')
    except Exception as e:
        return f"Error retrieving {path}: {str(e)}"

def list_directory(repo, path=""):
    """List contents of a directory in the repository."""
    try:
        contents = repo.get_contents(path)
        if not isinstance(contents, list):
            contents = [contents]
        return json.dumps([{"name": c.name, "path": c.path, "type": c.type} for c in contents])
    except Exception as e:
        return f"Error listing directory {path}: {str(e)}"

def main():
    # Load environment variables
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
    github_token = os.environ.get("GITHUB_TOKEN")
    github_repo = os.environ.get("GITHUB_REPOSITORY")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event_name = os.environ.get("GITHUB_EVENT_NAME")

    if not anthropic_api_key or not github_token or not github_repo or not event_path:
        print("Error: Required environment variables are missing.")
        sys.exit(1)

    # Initialize clients
    client = Anthropic(api_key=anthropic_api_key)
    g = Github(github_token)
    repo = g.get_repo(github_repo)

    # Read event data to understand context
    with open(event_path, 'r') as f:
        event_data = json.load(f)

    user_prompt = ""
    issue_number = None

    if event_name == "issues" or event_name == "issue_comment":
        issue = event_data.get("issue", {})
        issue_number = issue.get("number")
        if event_name == "issue_comment":
            comment = event_data.get("comment", {}).get("body", "")
            user_prompt = f"Issue: {issue.get('title')}\nBody: {issue.get('body')}\nNew Comment: {comment}"
        else:
            user_prompt = f"Issue: {issue.get('title')}\nBody: {issue.get('body')}"

    elif event_name == "pull_request":
        pr = event_data.get("pull_request", {})
        issue_number = pr.get("number")
        user_prompt = f"PR: {pr.get('title')}\nBody: {pr.get('body')}"

    else:
        print(f"Unsupported event: {event_name}")
        sys.exit(0)

    print(f"Triggered by {event_name} #{issue_number}")

    # Define tools for Claude
    tools = [
        {
            "name": "get_file_content",
            "description": "Read the contents of a file in the repository.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file, e.g., 'src/main.py'"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "list_directory",
            "description": "List the contents of a directory in the repository.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the directory. Leave empty for root."}
                },
                "required": ["path"]
            }
        }
    ]

    messages = [{"role": "user", "content": user_prompt}]

    try:
        # Step 1: Send initial prompt and tools to Claude
        # Using claude-3-5-sonnet as requested (4.6 doesn't exist yet, 3.5 is the latest Sonnet)
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system="You are an AI software engineer. You have tools to read the repository codebase. Help the user by investigating issues or PRs.",
            messages=messages,
            tools=tools
        )

        # Keep track of conversation
        messages.append({"role": "assistant", "content": response.content})

        # Step 2: Check if Claude wants to use tools
        while response.stop_reason == "tool_use":
            tool_results = []

            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_id = content_block.id

                    print(f"Claude is calling tool: {tool_name} with {tool_input}")

                    if tool_name == "get_file_content":
                        result = get_file_content(repo, tool_input["path"])
                    elif tool_name == "list_directory":
                        result = list_directory(repo, tool_input["path"])
                    else:
                        result = f"Unknown tool: {tool_name}"

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

            # Send tool results back to Claude
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system="You are an AI software engineer. You have tools to read the repository codebase. Help the user by investigating issues or PRs.",
                messages=messages,
                tools=tools
            )
            messages.append({"role": "assistant", "content": response.content})

        # Extract final text response
        final_text = ""
        for block in response.content:
            if block.type == "text":
                final_text += block.text

        # Post the reply back to the GitHub issue or PR
        if issue_number and final_text:
            issue = repo.get_issue(number=issue_number)
            issue.create_comment(f"**Claude Sonnet Response:**\n\n{final_text}")
            print(f"Successfully posted comment to #{issue_number}")

    except Exception as e:
        print(f"Error during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

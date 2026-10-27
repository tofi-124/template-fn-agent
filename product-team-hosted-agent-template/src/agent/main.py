"""Minimal Microsoft Agent Framework app meeting Foundry's Responses contract.

Runtime adapter provides GET /readiness and POST /responses on port 8088.
See: https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/framework-hosted-agents
"""
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential

from prompt import INSTRUCTIONS


def create_agent() -> Agent:
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )
    return Agent(
        client=client,
        instructions=INSTRUCTIONS,
        default_options={"store": False},
    )


def main() -> None:
    ResponsesHostServer(create_agent()).run()


if __name__ == "__main__":
    main()

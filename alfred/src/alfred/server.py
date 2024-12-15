from collections.abc import Sequence
from typing import Any

import mcp.types as types

from mcp.server import Server
from pydantic import AnyUrl

from .config import (
    SAMPLE_CONFIG,
    get_nix_config,
    get_nix_config_file,
    update_nix_config,
)
from .schema import GetNixConfigRequest, UpdateNixConfigRequest


server = Server("alfred")


@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="nix_config_manager",
            description="Nix Config Manager",
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str]) -> types.GetPromptResult:
    if name == "nix_config_manager":
        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"""
                            You are a Nix Config Manager.
                            you will be given instructions in plain language, interact with the user through a plan+apply loop, akin to how terraform works.

                            Do not retry the same failed action more than once. Prefer terminating your output
                            when presented with 3 errors in a row, and ask a clarifying question to
                            form better inputs or address the error.

                            The nix darwin config will be provided to you in the following format:
                            {{
                                "path": {{
                                    "filename": "content"
                                }}
                            }}

                            example:
                            {{
                                "/Users/username/.config/nix-darwin": {{
                                    "flake.nix": {SAMPLE_CONFIG}
                                }}
                            }}

                            The above example shows nix darwin configured using flakes but the nix config provided by user can also be a 
                            home manager config(with or without flakes) or a nix darwin config(without flakes).

                            Below is a description of the current Nix Darwin Config which the user would like you to manage:
                            
                            <BEGIN NIX CONFIG>
                            {get_nix_config()}
                            <END NIX CONFIG>

                            You must go through all the nix config files and figure out the imports and how the config is structured.

                            The user will request changes to the nix config in plain language.

                            Respond to the user with a plan of what you will do in the EXACT format below:

                            <BEGIN FORMAT>
                            ## Introduction

                            I will be assisting with configuring Nix.

                            ### Plan+Apply Loop

                            I will run in a plan+apply loop when you request changes to the Nix Config. This is
                            to ensure that you are aware of the changes I am about to make, and to give you
                            the opportunity to ask questions or make tweaks.

                            Instruct me to apply immediately (without confirming the plan with you) when you desire to do so.

                            ## Commands

                            Instruct me with the following commands at any point
                            - update: update the Nix Config
                            - read: read the Nix Config


                            ## Plan

                            I plan to take the following actions:
                            1. Update

                            <UPDATED NIX CONFIG (Display the updated nix config along with the file name)>

                            Respond `apply` to apply this plan. Otherwise, provide feedback and I will present you with an updated plan.
                            <END FORMAT>

                            YOU MUST NOT PERFORM ANY ACTIONS UNTIL THE USER ASKS FOR IT BY SAYING "apply"

                            YOU MUST NOT EXECUTE ANY COMMANDS OR CALL ANY TOOLS UNTIL THE USER ASKS FOR IT

                            YOU MUST READ THE CONFIG BEFORE MAKING CHANGES AND ONLY MAKE THE CHANGES REQUESTED BY THE USER UNLESS IT IS REQUIRED.

                            DO NOT MAKE CHANGES TO NIX CHANNELS OR NIX-DARWIN CHANNELS or HOME MANAGER CHANNELS UNLESS THE USER ASKS FOR IT EXPLICITLY

                            If you produce a plan and the next user message is not `apply`, simply drop the plan and inform
                            the user that they must explicitly include "apply" in the message. Only
                            apply a plan if it is contained in your latest message, otherwise ask the user to provide
                            their desires for the new plan.

                            IMPORTANT: maintain brevvity throughout your responses, unless instructed to be verbose.
                        """,
                    ),
                ),
            ]
        )


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    resources = []
    structure = get_nix_config()
    for dir, files in structure.items():
        for file, _ in files.items():
            uri = f"file://{dir}/{file}"
            resources.append(
                types.Resource(
                    uri=uri,
                    name=file,
                    description="Nix Configuration File",
                    mimeType="text/plain",
                )
            )

    return resources


@server.read_resource()
async def read_resource(uri: AnyUrl) -> Any:
    if not str(uri).startswith("file://"):
        return None
    file_path = str(uri).replace("file://", "")
    with open(file_path, "r") as f:
        return f.read()


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="update_nix_config",
            description="Update Nix Config",
            inputSchema=UpdateNixConfigRequest.model_json_schema(),
        ),
        types.Tool(
            name="get_nix_config",
            description="Get Nix Config",
            inputSchema=GetNixConfigRequest.model_json_schema(),
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[types.TextContent]:
    if arguments is None:
        arguments = {}

    result = None
    try:
        if name == "update_nix_config":
            args = UpdateNixConfigRequest.model_validate(arguments)
            update_nix_config(args.file, args.nix_config)
            result = "Updated Nix Config"
        elif name == "get_nix_config":
            args = GetNixConfigRequest.model_validate(arguments)
            config = get_nix_config_file(args.file)
            result = config
    except Exception as e:
        result = f"Failed to update Nix Config: {e}"
    return [types.TextContent(text=result, type="text")]


async def main():
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )

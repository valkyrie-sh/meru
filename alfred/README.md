## Alfred

Alfred is an mcp server that you can use with claude desktop to modify your nix darwin or home-manager configs

### Setup

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Clone this Repo
- Add the below config to Claude Desktop (/Users/<username>/Library/Application Support/Claude/claude_desktop_config.json)

```json
{
  "mcpServers": {
    "alfred": {
      "command": "uv",
      "args": ["--directory", "<path_to_repo>/meru/alfred", "run", "alfred"]
    }
  }
}
```

**Note:** Currently only MacOS is supported

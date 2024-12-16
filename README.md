# Meru

Meru is a collection of projects to make using nix easier

## Alfred

Alfred is an mcp server that you can use with claude desktop to modify your nix darwin or home-manager configs

### Setup

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Clone this Repo
- Add the below config to Claude Desktop

path - `/Users/<username>/Library/Application Support/Claude/claude_desktop_config.json`

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

- Include the nix file that you want to update and the nix config manager prompt in claude desktop

**Note:** Currently only MacOS is supported

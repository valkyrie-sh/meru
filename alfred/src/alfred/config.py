import os

from pathlib import Path


BASE_DIR = os.path.join(Path.home(), ".config", "nix-darwin")

if not os.path.exists(BASE_DIR):
    BASE_DIR = os.path.join(Path.home(), ".config", "home-manager")


def get_nix_config():
    structure = {}
    for root, _dirs, files in os.walk(BASE_DIR):
        structure[root] = {
            f: open(os.path.join(root, f), "r").read()
            for f in files
            if f != "flake.lock"
        }
    return structure


def update_nix_config(file: str, nix_config: str):
    file_path = os.path.join(BASE_DIR, file)
    with open(file_path, "w") as f:
        f.write(nix_config)


def get_nix_config_file(file: str = "flake.nix"):
    file_path = os.path.join(BASE_DIR, file)
    with open(file_path, "r") as f:
        return f.read()


SAMPLE_CONFIG = """
{
  description = "Example nix-darwin system flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    nix-darwin.url = "github:LnL7/nix-darwin";
    nix-darwin.inputs.nixpkgs.follows = "nixpkgs";
    home-manager.url = "github:nix-community/home-manager/release-24.11";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = inputs@{ self, nix-darwin, home-manager, nixpkgs }:
  let
    username = "some-username";
    useremail = "nVnX4@example.com";
    system = "aarch64-darwin";
    hostname = "some-hostname";

    specialArgs =
      inputs
      // {
        inherit username useremail hostname;
      };


    configuration = { pkgs, ... }: {
      environment.systemPackages =
        with pkgs; [ 
          elixir
          erlang
        ];

      # Necessary for using flakes on this system.
      nix.settings.experimental-features = "nix-command flakes";

      # Enable alternative shell support in nix-darwin.
      # programs.fish.enable = true;

      # Set Git commit hash for darwin-version.
      system.configurationRevision = self.rev or self.dirtyRev or null;

      # Used for backwards compatibility, please read the changelog before changing.
      # $ darwin-rebuild changelog
      system.stateVersion = 5;

      # The platform the configuration will be used on.
      nixpkgs.hostPlatform = system;
    };
  in
  {
    # Build darwin flake using:
    # $ darwin-rebuild build --flake .#${hostname}
    darwinConfigurations."${hostname}" = nix-darwin.lib.darwinSystem {
      inherit system specialArgs;
      modules = [ 
        configuration
        home-manager.darwinModules.home-manager
        {
          home-manager.useGlobalPkgs = true;
          home-manager.useUserPackages = true;
          home-manager.extraSpecialArgs = specialArgs;
          home-manager.users.${username} = import ./home;
        }
      ];
    };

    formatter.${system} = nixpkgs.legacyPackages.${system}.alejandra;
  };
}

"""

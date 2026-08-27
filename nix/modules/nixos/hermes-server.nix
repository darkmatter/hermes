{ config, lib, pkgs, ... }:

let
  cfg = config.services.hermesServer;
  hermesHome = "${cfg.stateDir}/.hermes";
  managedSettings = lib.recursiveUpdate cfg.settings (
    lib.optionalAttrs (cfg.publicUrl != null) {
      dashboard.public_url = cfg.publicUrl;
    }
    // lib.optionalAttrs (cfg.sharedSkillsDir != null) {
      skills.external_dirs = [ cfg.sharedSkillsDir ];
    }
  );
in
{
  options.services.hermesServer = {
    enable = lib.mkEnableOption "a Hermes Agent server";

    user = lib.mkOption {
      type = lib.types.str;
      default = "hermes";
      description = "User that runs Hermes services.";
    };

    group = lib.mkOption {
      type = lib.types.str;
      default = "hermes";
      description = "Group that runs Hermes services.";
    };
    createUser = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Create the Hermes service user and group.";
    };

    addToSystemPackages = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Expose Hermes and HERMES_HOME in system shells.";
    };

    stateDir = lib.mkOption {
      type = lib.types.str;
      default = "/var/lib/hermes";
      description = "Persistent state directory for Hermes.";
    };

    workingDirectory = lib.mkOption {
      type = lib.types.str;
      default = "${cfg.stateDir}/workspace";
      defaultText = lib.literalExpression ''"${cfg.stateDir}/workspace"'';
      description = "Working directory for Hermes terminal commands.";
    };

    publicUrl = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      example = "https://hermes.example.com";
      description = "Public dashboard URL, or null when the dashboard is private.";
    };

    settings = lib.mkOption {
      type = lib.types.attrsOf lib.types.anything;
      default = { };
      description = "Additional Hermes config.yaml settings.";
    };

    environment = lib.mkOption {
      type = lib.types.attrsOf lib.types.str;
      default = { };
      description = "Non-secret Hermes environment variables.";
    };

    environmentFiles = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      description = "Secret environment files consumed by the official Hermes NixOS module.";
    };

    sharedSkillsDir = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      example = "/etc/hermes/skills";
      description = "Read-only external skill directory shared with Hermes.";
    };

    dashboard = {
      enable = lib.mkEnableOption "the Hermes dashboard service";

      host = lib.mkOption {
        type = lib.types.str;
        default = "127.0.0.1";
        description = "Dashboard bind address.";
      };

      port = lib.mkOption {
        type = lib.types.port;
        default = 9119;
        description = "Dashboard listen port.";
      };

      environmentFile = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Optional systemd EnvironmentFile for dashboard-only secrets.";
      };

      extraEnvironment = lib.mkOption {
        type = lib.types.attrsOf lib.types.str;
        default = { };
        description = "Additional non-secret environment variables for the dashboard.";
      };
    };

    cloudflared = {
      enable = lib.mkEnableOption "a Cloudflare Tunnel connector";

      environmentFile = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "EnvironmentFile containing TUNNEL_TOKEN for cloudflared.";
      };
    };
  };

  config = lib.mkIf cfg.enable {
    assertions = [
      {
        assertion = !cfg.cloudflared.enable || cfg.cloudflared.environmentFile != null;
        message = "services.hermesServer.cloudflared.environmentFile must provide TUNNEL_TOKEN.";
      }
    ];

    services.hermes-agent = {
      enable = true;
      inherit (cfg)
        user
        group
        createUser
        addToSystemPackages
        stateDir
        workingDirectory
        environment
        environmentFiles
        ;
      settings = managedSettings;
    };

    systemd.services.hermes-dashboard = lib.mkIf cfg.dashboard.enable {
      description = "Hermes Agent Dashboard";
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" "hermes-agent.service" ];
      wants = [ "network-online.target" ];
      requires = [ "hermes-agent.service" ];

      environment = {
        HOME = cfg.stateDir;
        HERMES_HOME = hermesHome;
        HERMES_MANAGED = "true";
      } // cfg.dashboard.extraEnvironment;

      serviceConfig = {
        User = cfg.user;
        Group = cfg.group;
        WorkingDirectory = cfg.workingDirectory;
        EnvironmentFile = lib.optional (cfg.dashboard.environmentFile != null) cfg.dashboard.environmentFile;
        ExecStart = "${config.services.hermes-agent.package}/bin/hermes dashboard --no-open --host ${cfg.dashboard.host} --port ${toString cfg.dashboard.port}";
        Restart = "always";
        RestartSec = 5;
        KillMode = "mixed";
        KillSignal = "SIGTERM";
        TimeoutStopSec = 210;
      };
    };

    systemd.services.hermes-cloudflared = lib.mkIf cfg.cloudflared.enable {
      description = "Cloudflare Tunnel connector for Hermes";
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];

      serviceConfig = {
        EnvironmentFile = cfg.cloudflared.environmentFile;
        ExecStart = "${pkgs.cloudflared}/bin/cloudflared tunnel --no-autoupdate run";
        DynamicUser = true;
        Restart = "always";
        RestartSec = 5;
      };
    };
  };
}

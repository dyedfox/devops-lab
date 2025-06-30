# Service Discovery Lite 😀
This is a basic hardcoded replacement for proper service discovery—useful if you don't need the full setup. 😀
Docker container initialization script that configures inter-container communication and starts services.

## What it does

1. **Detects container IP** - Gets current container's IP address
2. **Sets peer container URL** - Configures URL to communicate with other container:
   - If IP is `172.17.0.3` → connects to `172.17.0.2:8123`
   - Otherwise → connects to `172.17.0.3:8123`
3. **Waits for peer service** - Polls until other container returns HTTP 404
4. **Starts supervisord** - Begins main service processes

## Usage

Run as container entrypoint script. Ensures proper startup order between paired containers.
"""Serve the packaged HIQS MCP tools on stdio."""

from hsas.core.facade import build_port

from .server import build_mcp_server


def main() -> None:
    build_mcp_server(build_port()).run()


if __name__ == "__main__":
    main()

"""CLI for scitex-template.

Subcommands follow the verb-noun convention (general/03_interface_02_cli):

    scitex-template list-templates          # list registered templates
    scitex-template show-info <id>          # show one template
    scitex-template clone <id> <target>     # populate target from cache
    scitex-template refresh-cache           # force re-clone of monorepo cache
    scitex-template list-python-apis        # introspect public Python API
    scitex-template mcp list-tools          # introspect MCP tool surface
    scitex-template mcp start               # launch the MCP server
"""

from __future__ import annotations

import json as _json
import sys
from pathlib import Path

import click
from scitex_logging import get_level, getConsole, getLogger, getPlainConsole

logger = getLogger(__name__)
console = getConsole(__name__ + ".console", level=get_level())
plain = getPlainConsole(__name__)


def _version() -> str:
    try:
        from importlib.metadata import version

        return version("scitex-template")
    except Exception:  # pragma: no cover
        return "unknown"


def _show_recursive_help(ctx: click.Context) -> None:
    """Print help for the root group plus every subcommand recursively."""
    click.echo(ctx.get_help())
    click.echo()
    group = ctx.command
    if isinstance(group, click.Group):
        for name in sorted(group.list_commands(ctx)):
            cmd = group.get_command(ctx, name)
            if cmd is None or cmd.hidden:
                continue
            sub_ctx = click.Context(cmd, parent=ctx, info_name=name)
            click.echo("=" * 60)
            click.echo(f"Command: {name}")
            click.echo("=" * 60)
            click.echo(sub_ctx.get_help())
            click.echo()
            if isinstance(cmd, click.Group):
                for sub_name in sorted(cmd.list_commands(sub_ctx)):
                    sub_cmd = cmd.get_command(sub_ctx, sub_name)
                    if sub_cmd is None or sub_cmd.hidden:
                        continue
                    sub_sub_ctx = click.Context(
                        sub_cmd, parent=sub_ctx, info_name=sub_name
                    )
                    click.echo("-" * 60)
                    click.echo(f"Command: {name} {sub_name}")
                    click.echo("-" * 60)
                    click.echo(sub_sub_ctx.get_help())
                    click.echo()


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(_version(), "-V", "--version", prog_name="scitex-template")
@click.option("--help-recursive", is_flag=True, help="Show help for all subcommands.")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit structured JSON output (propagates to subcommands that honour it).",
)
@click.pass_context
def main(ctx: click.Context, help_recursive: bool, as_json: bool) -> None:
    """scitex-template — clone scitex-* project templates from the monorepo cache.

    Resources resolve through scitex-config project/user scopes.
    Output uses the shared scitex_logging settings.
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    # Reuse the shared handler and honor the current ecosystem log threshold.
    getConsole(__name__ + ".console", level=get_level())
    if help_recursive:
        _show_recursive_help(ctx)
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command("list-templates")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Output as JSON instead of a human-readable table.",
)
@click.pass_context
def list_cmd(ctx: click.Context, as_json: bool) -> None:
    """List all registered templates.

    \b
    Example:
      $ scitex-template list-templates
      $ scitex-template list-templates --json
    """
    from .registry import load_registry

    as_json = as_json or bool(ctx.obj.get("as_json"))

    entries = load_registry()
    if as_json:
        plain.emit(
            _json.dumps(
                [
                    {
                        "id": e.id,
                        "version": e.version,
                        "description": e.description,
                        "path": str(e.path),
                    }
                    for e in entries
                ],
                indent=2,
            )
        )
        return

    width = max((len(e.id) for e in entries), default=12)
    for e in entries:
        console.info(f"{e.id:<{width}}  v{e.version}  {e.description}")


@main.command("show-info")
@click.argument("template_id")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.pass_context
def info_cmd(ctx: click.Context, template_id: str, as_json: bool) -> None:
    """Print details for a single template.

    \b
    Example:
      $ scitex-template show-info minimal
      $ scitex-template show-info research --json
    """
    from .registry import find_template

    as_json = as_json or bool(ctx.obj.get("as_json"))

    e = find_template(template_id)
    if e is None:
        if as_json:
            plain.emit(_json.dumps({"error": f"unknown template id: {template_id}"}))
        else:
            logger.fail(f"Unknown template id: {template_id}")
        sys.exit(1)
    if as_json:
        plain.emit(
            _json.dumps(
                {
                    "id": e.id,
                    "version": e.version,
                    "description": e.description,
                    "path": str(e.path),
                },
                indent=2,
            )
        )
        return
    console.info(f"id          : {e.id}")
    console.info(f"version     : {e.version}")
    console.info(f"description : {e.description}")
    console.info(f"path        : {e.path}")


@main.command("clone")
@click.argument("template_id")
@click.argument("target", type=click.Path(path_type=Path))
@click.option(
    "--force-refresh",
    is_flag=True,
    help="Wipe and re-clone the monorepo cache before populating target.",
)
@click.option(
    "--branch",
    default="develop",
    show_default=True,
    help="Branch of the scitex-template monorepo to track in the cache.",
)
@click.option("--dry-run", is_flag=True, help="Print clone plan without writing.")
@click.option(
    "-y", "--yes", is_flag=True, help="Suppress interactive confirmation (assume yes)."
)
def clone_cmd(
    template_id: str,
    target: Path,
    force_refresh: bool,
    branch: str,
    dry_run: bool,
    yes: bool,
) -> None:
    """Populate TARGET with the contents of TEMPLATE_ID.

    \b
    Example:
      $ scitex-template clone minimal ./my-paper
      $ scitex-template clone research ./my-project --branch develop
      $ scitex-template clone app ./my-app --dry-run
    """
    if dry_run:
        console.info(
            f"DRY RUN — would clone template '{template_id}' to {target} "
            f"(branch={branch}, force_refresh={force_refresh})"
        )
        return
    from ._cache import clone_template_from_cache

    try:
        out = clone_template_from_cache(
            template_id, target, branch=branch, force_refresh=force_refresh
        )
    except KeyError as e:
        logger.fail(str(e))
        sys.exit(1)
    except FileExistsError as e:
        logger.fail(str(e))
        sys.exit(2)
    console.success(f"cloned {template_id} → {out}")


@main.command("refresh-cache")
@click.option("--branch", default="develop", show_default=True)
@click.option("--dry-run", is_flag=True, help="Print refresh plan without writing.")
@click.option(
    "-y", "--yes", is_flag=True, help="Suppress interactive confirmation (assume yes)."
)
def cache_refresh_cmd(branch: str, dry_run: bool, yes: bool) -> None:
    """Force-refresh the ~/.scitex/template/runtime/cache/ shallow clone.

    \b
    Example:
      $ scitex-template refresh-cache
      $ scitex-template refresh-cache --branch develop
      $ scitex-template refresh-cache --dry-run
    """
    if dry_run:
        console.info(f"DRY RUN — would refresh cache (branch={branch})")
        return
    from ._cache import ensure_cache

    root = ensure_cache(branch=branch, force_refresh=True)
    console.success(f"refreshed cache at {root}")


@main.command(
    "version",
    hidden=True,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
def version_cmd(ctx) -> None:
    """(deprecated) Use `scitex-template --version` instead."""
    logger.error(
        "`scitex-template version` was replaced by "
        "`scitex-template --version`.\n"
        "Re-run with: scitex-template --version",
    )
    ctx.exit(2)


# -- Deprecated aliases (hidden, exit non-zero with redirect message) ------


@main.command(
    "list",
    hidden=True,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
def _deprecated_list(ctx) -> None:
    """(deprecated) renamed to `list-templates`."""
    logger.error(
        "`scitex-template list` was renamed to "
        "`scitex-template list-templates`.\n"
        "Re-run with: scitex-template list-templates",
    )
    ctx.exit(2)


@main.command(
    "info",
    hidden=True,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
def _deprecated_info(ctx) -> None:
    """(deprecated) renamed to `show-info`."""
    logger.error(
        "`scitex-template info` was renamed to "
        "`scitex-template show-info`.\n"
        "Re-run with: scitex-template show-info <id>",
    )
    ctx.exit(2)


@main.command(
    "cache-refresh",
    hidden=True,
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.pass_context
def _deprecated_cache_refresh(ctx) -> None:
    """(deprecated) renamed to `refresh-cache`."""
    logger.error(
        "`scitex-template cache-refresh` was renamed to "
        "`scitex-template refresh-cache`.\n"
        "Re-run with: scitex-template refresh-cache",
    )
    ctx.exit(2)


# -- Introspection ----------------------------------------------------------


@main.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="-v names, -vv +sigs, -vvv +docs")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.pass_context
def list_python_apis(ctx: click.Context, verbose: int, as_json: bool) -> None:
    """List public Python APIs in scitex-template.

    \b
    Example:
      $ scitex-template list-python-apis
      $ scitex-template list-python-apis -vv
      $ scitex-template list-python-apis --json
    """
    import inspect

    import scitex_template

    as_json = as_json or bool(ctx.obj.get("as_json"))

    names = sorted(getattr(scitex_template, "__all__", []))
    apis = []
    for name in names:
        obj = getattr(scitex_template, name, None)
        if obj is None:
            continue
        entry = {"name": name, "type": type(obj).__name__}
        if callable(obj):
            try:
                entry["signature"] = str(inspect.signature(obj))
            except (TypeError, ValueError):
                pass
        doc = inspect.getdoc(obj) or ""
        if doc:
            entry["doc"] = doc.strip().split("\n")[0]
        apis.append(entry)

    if as_json:
        plain.emit(_json.dumps({"module": "scitex_template", "apis": apis}, indent=2))
        return

    console.info("scitex_template Python APIs")
    for api in apis:
        sig = api.get("signature", "")
        console.info(f"{api['name']}{sig}", indent=1)
        if verbose >= 2 and api.get("doc"):
            console.info(api["doc"], indent=2)


# -- MCP --------------------------------------------------------------------


@main.group(invoke_without_command=True)
@click.pass_context
def mcp(ctx: click.Context) -> None:
    """MCP (Model Context Protocol) server commands."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@mcp.command("start")
@click.option("--dry-run", is_flag=True, help="Print launch plan without starting.")
@click.option(
    "-y", "--yes", is_flag=True, help="Suppress interactive confirmation (assume yes)."
)
def mcp_start(dry_run: bool, yes: bool) -> None:
    """Start the scitex-template MCP server.

    \b
    Example:
      $ scitex-template mcp start
      $ scitex-template mcp start --dry-run
    """
    if dry_run:
        console.info(
            "DRY RUN — would start scitex-template MCP server (stdio transport)"
        )
        return
    from scitex_template.mcp_server import main as mcp_main

    mcp_main()


@mcp.command("list-tools")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +desc, -vv full doc")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
@click.pass_context
def mcp_list_tools(ctx: click.Context, verbose: int, as_json: bool) -> None:
    """List available MCP tools.

    \b
    Example:
      $ scitex-template mcp list-tools
      $ scitex-template mcp list-tools -vv
      $ scitex-template mcp list-tools --json
    """
    from scitex_template._mcp.tool_schemas import get_tool_schemas

    as_json = as_json or bool(ctx.obj.get("as_json"))

    try:
        tools = get_tool_schemas()
    except ImportError as exc:
        logger.fail(str(exc))
        raise click.exceptions.Exit(1) from exc

    if as_json:
        payload = {
            "total": len(tools),
            "tools": [
                {
                    "name": getattr(t, "name", str(t)),
                    "description": getattr(t, "description", "") or "",
                }
                for t in tools
            ],
        }
        plain.emit(_json.dumps(payload, indent=2))
        return

    console.info(f"scitex-template MCP: {len(tools)} tools")
    for t in sorted(tools, key=lambda x: getattr(x, "name", str(x))):
        name = getattr(t, "name", str(t))
        desc = getattr(t, "description", "") or ""
        console.info(name, indent=1)
        if verbose >= 1 and desc:
            line = desc.split("\n")[0] if verbose == 1 else desc.strip()
            console.info(line, indent=2)


@mcp.command("doctor")
def mcp_doctor() -> None:
    """Check MCP server dependencies.

    \b
    Example:
      $ scitex-template mcp doctor
    """
    console.info("Checking MCP dependencies...")

    try:
        from importlib.metadata import version

        import mcp as mcp_package

        console.success(f"mcp {version(mcp_package.__name__)}", indent=1)
    except ImportError:
        logger.fail("MCP not installed. Install: pip install scitex-template[mcp]")
        raise click.exceptions.Exit(1)

    try:
        from scitex_template._mcp.tool_schemas import get_tool_schemas

        n_tools = len(get_tool_schemas())
        console.success(f"scitex-template MCP server ({n_tools} tools)", indent=1)
    except Exception as exc:
        logger.fail(f"MCP server error: {exc}")
        raise click.exceptions.Exit(1)

    console.success("MCP server ready.")
    console.info("Run: scitex-template mcp start")


@mcp.command("install")
@click.option("--claude-code", is_flag=True, help="Show Claude Code config.")
def mcp_install(claude_code: bool) -> None:
    """Show MCP installation instructions.

    \b
    Example:
      $ scitex-template mcp install
      $ scitex-template mcp install --claude-code
    """
    if claude_code:
        plain.emit(
            _json.dumps(
                {
                    "scitex-template": {
                        "command": "scitex-template",
                        "args": ["mcp", "start"],
                    }
                },
                indent=2,
            )
        )
        return

    console.info("scitex-template MCP Server Installation")
    console.info("1. Install: pip install scitex-template[mcp]", indent=1)
    console.info("2. Config:  scitex-template mcp install --claude-code", indent=1)
    console.info("3. Test:    scitex-template mcp doctor", indent=1)


# §1a: install-shell-completion + print-shell-completion (canonical leaves)
try:
    from scitex_dev._cli._completion import attach_shell_completion

    attach_shell_completion(main, prog_name="scitex-template")
except ImportError:
    pass


if __name__ == "__main__":
    main()

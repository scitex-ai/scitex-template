# SciTeX project files

Use `<project-root>/.scitex/<package>/` for project configuration and
`~/.scitex/<package>/` for user configuration. Packages resolve their own
configuration; the template does not write user settings or credentials.

Commit configuration and research sources. Ignore generated `runtime/`
contents while retaining `.gitkeep` and `README.md`. Writer creates its
workspace under `.scitex/writer/` when explicitly requested.

Packages using the ecosystem state store use `scitex_dev.store` and the
managed PostgreSQL service on port 55432. A directory is not a database
locator. Database provisioning and access grants belong to the deployment,
not a research template.

On SciTeX Hub/Cloud, the deployment must map the authenticated user's stable
identity to an authorized store and enforce read and write permissions there.
Shared writer-role membership alone is not per-user authorization. Missing
identity, missing grants, or an inaccessible ACL must fail closed. Do not
place a deployment/admin credential in a project or grant all users access
to the host's fleet store. Verify cross-user denial before enabling access.

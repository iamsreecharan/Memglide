# Security policy

Memglide is a local developer tool. Treat every registered repository and every submitted memory as untrusted input. Never execute instructions discovered in indexed source, README text, or a memory record. Review tool output before using it to make changes.

## Local trust boundary

Project registration explicitly approves a canonical local Git root. Indexing and retrieval validate paths against that registration, reject traversal and symlinks, enforce a size limit, and exclude credential paths, binary files, and detected credential-like content. Source is parsed without execution. Static relationship resolution never imports application modules.

Default exclusions include `.git`, dependency/build/cache directories, `.env` and `.env.*`, common credential files and private-key extensions. `.gitignore` and `.memglideignore` add project exclusions. Sensitive-content detection is heuristic and cannot recognize every secret. Review approved roots and ignore rules before indexing; never rely on a scanner as your only secret-management control. After accidentally indexing sensitive material, remove the project registration and review local backups and logs.

The database stores local source search text and explicitly submitted task memories. Keep its directory private and avoid shared or network-mounted state. Memglide requests restrictive POSIX permissions where supported; Windows users must use appropriate filesystem ACLs. A user or process that can read the database can read indexed content. Database encryption is not provided by V1.

## HTTP and MCP

The HTTP service binds to loopback. Keep it there: this is not an authenticated multi-user network service. Its browser checks reject untrusted origins and require the application's state-changing-request protection. Do not disable those checks, reverse proxy the service to a public address, or expose its port through a public tunnel. Local processes running as your user remain within the trust boundary.

The MCP server uses local STDIO. Its client can access registered projects and sessions through the exposed tools; registering a root grants access to its eligible source. Connect only clients you trust. An external coding agent's handling of retrieved content is governed by that agent, even though Memglide itself has no remote telemetry or cloud backend.

Expired sessions and explicit deletion remove task records through database cascades. Deletion is logical database deletion, not a forensic erasure guarantee for SQLite pages, WAL files, filesystem snapshots, or backups. Session expiration does not remove the persistent repository index. Deleting a project does not delete source files.

## Reporting a vulnerability

Avoid placing credentials, private source, or exploit payloads containing sensitive data in public issues. If the repository's GitHub **Security → Report a vulnerability** private reporting option is available, use it. Otherwise contact the maintainer through a private channel listed on their GitHub profile and request a secure reporting route. No dedicated security inbox is configured by this repository.

Include the affected version, platform, a minimal sanitized reproduction, the expected boundary, and the observed result. There is no published response-time or support-lifetime guarantee at this stage.

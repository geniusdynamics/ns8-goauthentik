# Authentik upgrades on NS8

From module 2.1.0, apply each version in order in Software Center.

**2.1.0 → 2.1.1 → 2.2.0 → 2.3.0 → 2.4.0**

For the directory integration described in this branch, start from module 2.4.0
or later on NS8 core 3.23.0 or later. Upgrading the module and opting in to a
managed directory are separate operations. You can upgrade and keep your
existing sign-in setup.

The compatibility release on Authentik 2025.12.6 accepts upgrades from
NS8 module 2.0.3 or later. Back up the module before switching versions.
For an existing 2025.8 installation, install module 2.0.3 (Authentik
2025.10.4) before moving to the 2025.12 line. Review duplicate group names
in Authentik before moving from 2025.10 to 2025.12. The preflight reports
duplicates without changing group or policy assignments.

The module persists new files under `/data` and mounts the existing media
volume under `/data/media`. The upgrade copies files from the previous
containers and keeps existing volume files if their names collide. The old
Redis data volume is retained on disk. Authentik uses PostgreSQL for its
cache and tasks.

Restore the pre-upgrade backup to go back to an earlier Authentik version.
Reinstalling the earlier image over a migrated database is unsupported.

### NS8 module 2.2.0

Upgrade from module 2.1.1 (Authentik 2025.12.6) to Authentik 2026.2.7.
The 2026.2 line deprecates `User.ak_groups` in custom expressions and property mappings. Review those expressions and switch to `User.groups`.

### NS8 module 2.3.0

Upgrade from module 2.2.0 (Authentik 2026.2.7) to Authentik 2026.5.8.
Keep this 2026.5.8 waypoint before 2026.8. The 2026.5.7 → 2026.8.2 route had an upstream migration-history regression.

### NS8 module 2.4.0

Upgrade from module 2.3.0 (Authentik 2026.5.8) to Authentik 2026.8.5.
The ingress remains bound to the module node loopback. Authentik trusts forwarded headers only from the loopback and the dedicated slirp4netns pod subnet.

## Verify after upgrading

1. Confirm the Authentik admin interface loads and a local administrator can
   sign in in a fresh session.
2. If you use LDAP, verify a directory sync completes and test fresh sign-ins
   to representative apps. Check the expected account and group permissions.
3. For module troubleshooting, check the [service logs](../README.md#service-logs),
   including the worker service for background jobs.

QEMU covered the staged upgrade using the published tags and checked existing
database credentials, a seeded group, and a media file. The directory tests on
NS8 core 3.25.1 covered a fresh Debian 13 installation and a Rocky Linux 9
upgrade from module 2.4.0. They exercised OpenLDAP and AD side by side, a manual
source, and selective removal. [Staged upgrade results](https://github.com/geniusdynamics/ns8-goauthentik/actions/runs/44487063891) · [Directory test results](https://github.com/geniusdynamics/ns8-goauthentik/actions/runs/44589879988)

For a directory-only rollback on the current version, follow the
[directory rollback procedure](ns8-directory-login.md#roll-back-the-directory-switch).

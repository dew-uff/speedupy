# Security policy

## Supported versions

The current release line is supported: 1.7.x (latest release 1.7.1). The next
line, 2.0, is in development on `main`.

## Reporting a vulnerability

Do not open a public issue. Report it in a
[private security advisory](https://github.com/dew-uff/speedupy/security/advisories/new)
on GitHub (the "Security" tab, "Report a vulnerability").

Private vulnerability reporting is not enabled on this repository yet
([#141](https://github.com/dew-uff/speedupy/issues/141)). Until it is, write to
the maintainers listed in [`.github/CODEOWNERS`](.github/CODEOWNERS), without
posting the details in public.

## Threat model

The cache is local data, written and read by the same user who runs the
experiment. SpeeduPy deserializes it with `pickle` (or `cloudpickle`), and
loading a crafted pickle runs arbitrary code, so never use a cache directory that
comes from an untrusted source. The server backends are optional and the user
administers them: whoever can write to a storage that SpeeduPy reads can run code
as that user, so restrict who can reach it.

# ROCm Directory Map

This document maps out where all ROCm-related directories live on this system.

**Update the paths below to match your actual setup.**

## Repository Aliases

| Alias | Path | Notes |
|-------|------|-------|
| workspace | C:\Dev\claude-rocm-workspace | This meta-workspace |
| therock_pub | C:\Dev\TheRock-pub | Public TheRock clone used for day-to-day automation |
| rocm-systems_pub | C:\Dev\rocm-sys-pub | Public ROCm Systems super-repo (standalone clone, not a submodule) |
| rocm-libraries_pub | C:\Dev\rocm-libs-pub | Public ROCm Libraries super-repo (standalone clone, not a submodule) |
| rocm-systems_emu | C:\Dev\rocm-sys-emu | EMU/NPI ROCm Systems super-repo clone |
| rocm-libraries_emu | C:\Dev\rocm-libs-emu | EMU/NPI ROCm Libraries super-repo clone |
| rocm_npi_dev | C:\Dev\rocm-npi-dev | Private/NPI integration workspace (hosts _rockit and related tooling) |

**Cloning pattern:** super-repos live beside the meta-workspace instead of under `TheRock-*`. Each TheRock checkout is kept lean so multiple instances can reference whichever systems/libraries clone matches the task (public vs EMU/NPI).

## Build Trees

### Active Builds

- _None recorded yet._ Add entries here as build directories spin up (for example `C:\Dev\TheRock-pub-build`, `C:\Dev\TheRock-npi-build`, etc.), including configuration, target GPU families, and install destinations.

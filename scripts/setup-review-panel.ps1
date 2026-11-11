[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$SessionRoot
)

$ErrorActionPreference = 'Stop'
$workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$skillSource = Join-Path $workspaceRoot 'skills\review-panel'
if (-not (Test-Path -LiteralPath (Join-Path $skillSource 'SKILL.md') -PathType Leaf)) {
    throw "Review panel source is missing: $skillSource"
}

$discoveryRoots = @($workspaceRoot)
if ($SessionRoot) {
    $resolvedSessionRoot = (Resolve-Path -LiteralPath $SessionRoot).ProviderPath
    if (-not (Test-Path -LiteralPath $resolvedSessionRoot -PathType Container)) {
        throw 'SessionRoot must be an existing directory.'
    }
    $discoveryRoots += $resolvedSessionRoot
}

# Plan every link before writing so a conflict cannot leave a partial setup.
$plannedLinks = @()
foreach ($discoveryRoot in ($discoveryRoots | Select-Object -Unique)) {
    foreach ($runtime in @('.agents', '.claude')) {
        $linkPath = Join-Path $discoveryRoot "$runtime\skills\review-panel"
        $existingLink = Get-Item -LiteralPath $linkPath -Force -ErrorAction SilentlyContinue
        if ($existingLink) {
            $sameTarget = $false
            if ($existingLink.LinkType -in @('Junction', 'SymbolicLink')) {
                $linkTarget = @($existingLink.Target)[0]
                if (-not [System.IO.Path]::IsPathRooted($linkTarget)) {
                    $linkTarget = Join-Path $existingLink.Parent.FullName $linkTarget
                }
                $sameTarget = [System.IO.Path]::GetFullPath($linkTarget).TrimEnd('\') -eq $skillSource.TrimEnd('\')
            }
            if (-not $sameTarget) {
                throw "Existing path has another owner; nothing was replaced: $linkPath"
            }
        } else {
            $plannedLinks += $linkPath
        }
    }
}

foreach ($linkPath in $plannedLinks) {
    if ($PSCmdlet.ShouldProcess($linkPath, "Create junction to $skillSource")) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $linkPath) -Force | Out-Null
        New-Item -ItemType Junction -Path $linkPath -Target $skillSource | Out-Null
    }
}
if (-not $WhatIfPreference) {
    foreach ($discoveryRoot in ($discoveryRoots | Select-Object -Unique)) {
        foreach ($runtime in @('.agents', '.claude')) {
            $linkPath = Join-Path $discoveryRoot "$runtime\skills\review-panel"
            if (-not (Test-Path -LiteralPath (Join-Path $linkPath 'SKILL.md'))) {
                throw "Skill entry point is not readable: $linkPath"
            }
            Write-Output "Ready: $linkPath"
        }
    }
}

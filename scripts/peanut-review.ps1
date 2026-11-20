[CmdletBinding()]
param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet('doctor', 'init', 'run', 'status', 'cancel')]
    [string]$Command,
    [string]$Distribution = 'Ubuntu',
    [string]$RuntimeRoot,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ReviewArguments
)

$ErrorActionPreference = 'Stop'
$metaWorkspace = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if (-not $RuntimeRoot) {
    $RuntimeRoot = Join-Path (Split-Path $metaWorkspace -Parent) '.cache\peanut-review\runtime'
}

function ConvertTo-WslPath([string]$Value) {
    if ($Value.StartsWith('/')) { return $Value }
    $absolute = [IO.Path]::GetFullPath($Value)
    $converted = & wsl.exe --distribution $Distribution --exec wslpath -a -u $absolute
    if ($LASTEXITCODE -ne 0) { throw "Could not translate path: $Value" }
    return ($converted | Out-String).Trim()
}

$runtimePath = ConvertTo-WslPath $RuntimeRoot
$scriptPath = ConvertTo-WslPath (Join-Path $metaWorkspace 'tools\peanut-review\scripts\workspace_review.py')
# Match Windows checkout normalization without copying credential helpers,
# aliases or other global Git settings. Repository config and .gitattributes
# retain their normal precedence over these global defaults.
$gitDefaults = [Collections.Generic.List[string]]::new()
$gitDefaults.Add('[core]')
foreach ($key in @('autocrlf', 'eol')) {
    $value = & git config --global --get "core.$key" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $value = & git config --system --get "core.$key" 2>$null
    }
    if ($LASTEXITCODE -eq 0 -and $value) {
        $normalized = ($value | Select-Object -Last 1).Trim().ToLowerInvariant()
        $allowed = if ($key -eq 'autocrlf') { @('true', 'false', 'input') } else { @('lf', 'crlf', 'native') }
        if ($normalized -notin $allowed) { throw "Unsupported Windows Git core.$key value" }
        $gitDefaults.Add("    $key = $normalized")
    }
}
$runtimeWindows = [IO.Path]::GetFullPath($RuntimeRoot)
[IO.Directory]::CreateDirectory($runtimeWindows) | Out-Null
$gitDefaultsPath = Join-Path $runtimeWindows 'native-git-global.ini'
$gitDefaultsTemporary = $gitDefaultsPath + '.' + [guid]::NewGuid().ToString('N') + '.tmp'
[IO.File]::WriteAllText($gitDefaultsTemporary, ($gitDefaults -join "`n") + "`n", [Text.UTF8Encoding]::new($false))
Move-Item -LiteralPath $gitDefaultsTemporary -Destination $gitDefaultsPath -Force
$forwarded = [Collections.Generic.List[string]]::new()
$pathOptions = @('--source', '--related-source', '--session', '--session-root')
for ($index = 0; $index -lt $ReviewArguments.Count; $index++) {
    $argument = $ReviewArguments[$index]
    if ($argument -in $pathOptions) {
        if ($index + 1 -ge $ReviewArguments.Count) { throw "Missing path after $argument" }
        $forwarded.Add($argument)
        $index++
        $forwarded.Add((ConvertTo-WslPath $ReviewArguments[$index]))
    } elseif ($argument -match '^(--source|--related-source|--session|--session-root)=(.*)$') {
        $forwarded.Add($Matches[1] + '=' + (ConvertTo-WslPath $Matches[2]))
    } else {
        $forwarded.Add($argument)
    }
}

# Argument arrays go directly to WSL; no shell command is assembled from input.
& wsl.exe --distribution $Distribution --exec env `
    "PATH=${runtimePath}/bin:${runtimePath}/venv/bin:/usr/local/bin:/usr/bin:/bin" `
    "PEANUT_REVIEW_RUNTIME=$runtimePath" 'PYTHONDONTWRITEBYTECODE=1' 'GIT_OPTIONAL_LOCKS=0' `
    "GIT_CONFIG_GLOBAL=$runtimePath/native-git-global.ini" `
    "$runtimePath/venv/bin/python" $scriptPath $Command @forwarded
exit $LASTEXITCODE

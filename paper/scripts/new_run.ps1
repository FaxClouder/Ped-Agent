[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern("^[a-z0-9]+(?:-[a-z0-9]+)*$")]
    [string]$Name,

    [ValidateSet("experiment", "regression", "smoke")]
    [string]$RunType = "experiment"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$paperRoot = Split-Path -Parent $PSScriptRoot
$templateRoot = Join-Path $paperRoot "experiments\templates"
$runsRoot = Join-Path $paperRoot "experiments\results\runs"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$runId = "$timestamp-$Name"
$runDir = Join-Path $runsRoot $runId

if (Test-Path -LiteralPath $runDir) {
    throw "Run directory already exists: $runDir"
}

New-Item -ItemType Directory -Path $runDir | Out-Null
Copy-Item (Join-Path $templateRoot "metrics.csv") (Join-Path $runDir "metrics.csv")

$metadata = Get-Content -Raw (Join-Path $templateRoot "run-metadata.yaml")
$metadata = $metadata.Replace("run_id: TODO", "run_id: $runId")
$metadata = $metadata.Replace("name: TODO", "name: $Name")
$metadata = $metadata.Replace("run_type: experiment", "run_type: $RunType")
$metadata = $metadata.Replace("started_at: TODO", "started_at: $(Get-Date -Format 'o')")

$gitCommit = (& git -C (Split-Path -Parent $paperRoot) rev-parse HEAD 2>$null)
if ($LASTEXITCODE -eq 0) {
    $metadata = $metadata.Replace("git_commit: TODO", "git_commit: $gitCommit")
}

$dirtyState = (& git -C (Split-Path -Parent $paperRoot) status --porcelain 2>$null)
$isDirty = if ($dirtyState) { "true" } else { "false" }
$metadata = $metadata.Replace("git_dirty: TODO", "git_dirty: $isDirty")

Set-Content -Encoding utf8 (Join-Path $runDir "metadata.yaml") $metadata
Set-Content -Encoding utf8 (Join-Path $runDir "notes.md") "# $Name`n`n## Observations`n`n- TODO`n`n## Failures and deviations`n`n- TODO`n`n## Claim boundary`n`n- TODO`n"

Write-Host "Created run: $runId"
Write-Host "Directory: $runDir"

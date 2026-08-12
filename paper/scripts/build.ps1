[CmdletBinding()]
param(
    [ValidateSet("ieee", "elsevier", "all")]
    [string]$Template = "all"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$paperRoot = Split-Path -Parent $PSScriptRoot
$latexRoot = Join-Path $paperRoot "latex"
$buildRoot = Join-Path $paperRoot "build"
$targets = if ($Template -eq "all") { @("ieee", "elsevier") } else { @($Template) }

if (-not (Get-Command latexmk -ErrorAction SilentlyContinue)) {
    throw "latexmk was not found. Install a LaTeX distribution with IEEEtran and elsarticle support."
}

foreach ($target in $targets) {
    $sourceDir = Join-Path $latexRoot $target
    $targetBuildDir = Join-Path $buildRoot $target
    New-Item -ItemType Directory -Force -Path $targetBuildDir | Out-Null

    Push-Location $sourceDir
    try {
        & latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error main.tex
        if ($LASTEXITCODE -ne 0) {
            throw "LaTeX compilation failed for $target."
        }

        Copy-Item -Force "main.pdf" (Join-Path $targetBuildDir "ped-agent-$target.pdf")
        & latexmk -C main.tex | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "LaTeX cleanup failed for $target."
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host "Built templates: $($targets -join ', ')"
Write-Host "Output directory: $buildRoot"

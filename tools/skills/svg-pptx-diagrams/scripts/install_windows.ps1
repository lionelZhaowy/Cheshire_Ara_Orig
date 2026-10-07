param([Parameter(Mandatory=$true)][string]$SourceDir, [switch]$UpdateExisting)
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$source = (Get-Item $SourceDir).FullName
if (-not (Test-Path (Join-Path $source 'SKILL.md'))) { throw 'Missing source SKILL.md' }
$codexRoot = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$target = Join-Path $codexRoot 'skills\svg-pptx-diagrams'
$discovery = Join-Path $env:USERPROFILE '.agents\skills\svg-pptx-diagrams'
if (((Test-Path $target) -or (Test-Path $discovery)) -and -not $UpdateExisting) { throw 'Target skill already exists; inspect it before updating' }
if (Test-Path $target) {
    $existing = Get-Content (Join-Path $target 'SKILL.md') -Raw
    if ($existing -notmatch '(?m)^name: svg-pptx-diagrams\s*$') { throw 'Existing target is not this skill' }
    $backup = Join-Path $codexRoot ('skill-backups\svg-pptx-diagrams-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
    New-Item -ItemType Directory -Path $backup -Force | Out-Null
    foreach ($entry in @('SKILL.md','requirements.txt','agents','scripts','references','assets')) {
        if (Test-Path (Join-Path $target $entry)) { Copy-Item -LiteralPath (Join-Path $target $entry) -Destination $backup -Recurse }
    }
}
if (Test-Path $discovery) {
    $link = Get-Item $discovery
    if ($link.LinkType -ne 'Junction' -or $link.Target[0] -ne $target) { throw 'Existing discovery entry points elsewhere' }
}
$basePython = (Get-Command python -ErrorAction Stop).Source
New-Item -ItemType Directory -Path $target -Force | Out-Null
foreach ($entry in @('SKILL.md','requirements.txt','agents','scripts','references','assets')) {
    Copy-Item -LiteralPath (Join-Path $source $entry) -Destination $target -Recurse -Force
}
if (-not (Test-Path (Join-Path $target '.venv\Scripts\python.exe'))) {
    & $basePython -m venv (Join-Path $target '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Windows virtual environment creation failed' }
}
$venvPython = Join-Path $target '.venv\Scripts\python.exe'
& $venvPython -m pip install --disable-pip-version-check --no-input -r (Join-Path $target 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Windows dependency installation failed' }
New-Item -ItemType Directory -Path (Split-Path $discovery) -Force | Out-Null
if (-not (Test-Path $discovery)) { New-Item -ItemType Junction -Path $discovery -Target $target | Out-Null }
& $venvPython (Join-Path $target 'scripts\test_svg_to_pptx.py') -v
if ($LASTEXITCODE -ne 0) { throw 'Windows behavioral checks failed' }
$outDir = Join-Path $target ('validation-windows-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
& $basePython (Join-Path $target 'scripts\run.py') --input (Join-Path $target 'assets\example.svg') --out-dir $outDir
if ($LASTEXITCODE -ne 0) { throw 'Windows launcher/export check failed' }
$report = [pscustomobject]@{
    target=$target; discovery=$discovery; base_python=$basePython; venv_python=$venvPython
    behavioral_checks_passed=$true; native_export_passed=$true; output=$outDir
    powerpoint_tested=$false
}
$powerpoint = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\POWERPNT.EXE' -ErrorAction SilentlyContinue
if ($powerpoint) {
    & (Join-Path $target 'scripts\verify_powerpoint.ps1') -Presentation (Join-Path $outDir 'diagrams.pptx') -OutDirectory $outDir
    $report.powerpoint_tested = $true
}
[IO.File]::WriteAllText((Join-Path $target 'installation_report.json'), ($report | ConvertTo-Json -Depth 5), (New-Object Text.UTF8Encoding($false)))
$report | ConvertTo-Json -Depth 5

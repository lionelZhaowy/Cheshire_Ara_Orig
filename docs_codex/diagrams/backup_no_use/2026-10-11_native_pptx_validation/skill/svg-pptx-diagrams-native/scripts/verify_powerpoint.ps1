param(
    [Parameter(Mandatory=$true)][string]$Presentation,
    [Parameter(Mandatory=$true)][string]$OutDirectory
)
$ErrorActionPreference = 'Stop'
$app = $null
$deck = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    # Open only the generated presentation, read-only and without a document window.
    # Never use ActivePresentation or Quit: a user's PowerPoint may already be open.
    if (Test-Path (Join-Path $OutDirectory 'office_verification.json')) { throw 'Verification output already exists; choose a fresh directory' }
    $deck = $app.Presentations.Open($Presentation, -1, 0, 0)
    $renderHeight = [int][Math]::Round(1680 * $deck.PageSetup.SlideHeight / $deck.PageSetup.SlideWidth)
    $results = @()
    foreach ($slide in $deck.Slides) {
        $texts = @()
        $editProbe = $false
        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $texts += $shape.TextFrame.TextRange.Text
                if (-not $editProbe) {
                    $character = $shape.TextFrame.TextRange.Characters(1, 1)
                    $originalCharacter = $character.Text
                    $character.Text = 'X'
                    if ($shape.TextFrame.TextRange.Characters(1, 1).Text -ne 'X') {
                        throw 'Native text editing probe failed'
                    }
                    $shape.TextFrame.TextRange.Characters(1, 1).Text = $originalCharacter
                    $editProbe = $true
                }
            }
        }
        $imagePath = Join-Path $OutDirectory ('powerpoint-slide-' + $slide.SlideIndex + '.png')
        $slide.Export($imagePath, 'PNG', 1680, $renderHeight)
        $results += [pscustomobject]@{
            slide = $slide.SlideIndex
            shapes = $slide.Shapes.Count
            text_objects = $texts.Count
            native_text_edit_probe_passed = $editProbe
            text = $texts
            preview = [IO.Path]::GetFileName($imagePath)
        }
    }
    $report = [pscustomobject]@{
        powerpoint_version = $app.Version
        read_only_open = $true
        slide_count = $deck.Slides.Count
        svg_convert_to_shape_tested = $false
        slides = $results
    }
    $json = $report | ConvertTo-Json -Depth 8
    [IO.File]::WriteAllText((Join-Path $OutDirectory 'office_verification.json'), $json, (New-Object Text.UTF8Encoding($false)))
    Write-Output ('PowerPoint ' + $app.Version + ': ' + $deck.Slides.Count + ' slides exported')
    foreach ($result in $results) {
        Write-Output ('slide ' + $result.slide + ': ' + $result.shapes + ' shapes / ' + $result.text_objects + ' text objects')
    }
}
finally {
    if ($null -ne $deck) {
        $deck.Close()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($deck)
    }
    if ($null -ne $app) {
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
    }
}

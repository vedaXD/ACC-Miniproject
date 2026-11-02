
$ErrorActionPreference = "Stop"

$US = "http://54.242.141.54:5000"
$EU = "http://34.241.36.71:5000"
$ASIA = "http://52.77.218.56:5000"

$key = "demo-lww-" + (Get-Date -Format "yyyyMMdd-HHmmss-fff")

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   LWW REGISTER - CONCURRENT WRITES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$bodyUS = @{key=$key; value="active"} | ConvertTo-Json -Compress
$bodyEU = @{key=$key; value="inactive"} | ConvertTo-Json -Compress

$jUS = Start-Job -ArgumentList $US,$bodyUS -ScriptBlock {
    param($url,$body)
    Invoke-RestMethod "$url/set" -Method Post -ContentType "application/json" -Body $body
}

$jEU = Start-Job -ArgumentList $EU,$bodyEU -ScriptBlock {
    param($url,$body)
    Invoke-RestMethod "$url/set" -Method Post -ContentType "application/json" -Body $body
}

Wait-Job $jUS,$jEU | Out-Null

Write-Host "`nUS WRITE:" -ForegroundColor Yellow
Receive-Job $jUS | Format-List

Write-Host "EUROPE WRITE:" -ForegroundColor Yellow
Receive-Job $jEU | Format-List

Remove-Job $jUS,$jEU

Write-Host "`nWaiting for CRDT replication..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

Write-Host "`nFINAL STATE ON ALL REGIONS" -ForegroundColor Cyan

$results = @()

foreach ($node in @(
    @{Name="US"; URL=$US},
    @{Name="EUROPE"; URL=$EU},
    @{Name="ASIA"; URL=$ASIA}
)) {
    try {
        $r = Invoke-RestMethod "$($node.URL)/get/$key"

        $results += [PSCustomObject]@{
            Region = $node.Name
            Value = $r.value
            HLC = $r.ts -join ":"
        }
    }
    catch {
        Write-Host "$($node.Name) ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
}

$results | Format-Table -AutoSize

if (($results.Count -eq 3) -and
    (($results.Value | Select-Object -Unique).Count -eq 1) -and
    (($results.HLC | Select-Object -Unique).Count -eq 1)) {

    Write-Host "`nSUCCESS: ALL THREE REGIONS CONVERGED!" -ForegroundColor Green
    Write-Host "Winning value: $($results[0].Value)" -ForegroundColor Green
    Write-Host "Winning HLC: $($results[0].HLC)" -ForegroundColor Green
}
else {
    Write-Host "`nREPLICATION NOT YET CONVERGED." -ForegroundColor Red
}

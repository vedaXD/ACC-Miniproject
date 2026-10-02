Write-Host "Firing conflicting writes to US (active) and Europe (inactive)..."

$jobUS = Start-Job -ScriptBlock {
    curl.exe -s -X POST localhost:5001/set -H "Content-Type: application/json" -d '{\"key\":\"user:100\",\"value\":\"active\"}'
}
$jobEU = Start-Job -ScriptBlock {
    curl.exe -s -X POST localhost:5002/set -H "Content-Type: application/json" -d '{\"key\":\"user:100\",\"value\":\"inactive\"}'
}

Wait-Job $jobUS, $jobEU | Out-Null
Receive-Job $jobUS
Receive-Job $jobEU

Write-Host ""
Write-Host "Both writes sent. Waiting 1.5s for replication..."
Start-Sleep -Seconds 1.5

Write-Host ""
Write-Host "Final state on each region:"
Write-Host -NoNewline "US     -> "; curl.exe -s localhost:5001/get/user:100
Write-Host -NoNewline "Europe -> "; curl.exe -s localhost:5002/get/user:100
Write-Host -NoNewline "Asia   -> "; curl.exe -s localhost:5003/get/user:100
Write-Host ""
Write-Host "All three lines above should show the SAME value if CRDT resolution worked."
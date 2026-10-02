Write-Host "Incrementing post:101:likes -> US +5, Europe +3, Asia +2 (fired concurrently)..."

$jobUS = Start-Job -ScriptBlock { curl.exe -s -X POST localhost:5001/incr -H "Content-Type: application/json" -d '{\"key\":\"post:101:likes\",\"amount\":5}' }
$jobEU = Start-Job -ScriptBlock { curl.exe -s -X POST localhost:5002/incr -H "Content-Type: application/json" -d '{\"key\":\"post:101:likes\",\"amount\":3}' }
$jobAS = Start-Job -ScriptBlock { curl.exe -s -X POST localhost:5003/incr -H "Content-Type: application/json" -d '{\"key\":\"post:101:likes\",\"amount\":2}' }

Wait-Job $jobUS, $jobEU, $jobAS | Out-Null
Receive-Job $jobUS; Receive-Job $jobEU; Receive-Job $jobAS

Write-Host ""
Write-Host "All increments sent. Waiting 1.5s for replication..."
Start-Sleep -Seconds 1.5

Write-Host ""
Write-Host "Final counter value on each region (expected: 10 everywhere):"
Write-Host -NoNewline "US     -> "; curl.exe -s localhost:5001/counter/post:101:likes
Write-Host -NoNewline "Europe -> "; curl.exe -s localhost:5002/counter/post:101:likes
Write-Host -NoNewline "Asia   -> "; curl.exe -s localhost:5003/counter/post:101:likes
Write-Host ""
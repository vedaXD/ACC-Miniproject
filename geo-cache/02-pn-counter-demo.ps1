$US="http://54.242.141.54:5000"; $EU="http://34.241.36.71:5000"; $ASIA="http://52.77.218.56:5000"
$key="demo-pn-"+(Get-Date -Format "yyyyMMdd-HHmmss-fff")
$bUS=(@{key=$key;amount=5}|ConvertTo-Json -Compress);$bEU=(@{key=$key;amount=3}|ConvertTo-Json -Compress);$bAS=(@{key=$key;amount=2}|ConvertTo-Json -Compress)
Write-Host "`n=== PN-COUNTER: US +5, EUROPE +3, ASIA +2 ===" -ForegroundColor Cyan
$jobs=@()
$jobs+=Start-Job -ArgumentList $US,$bUS,"US" -ScriptBlock {param($u,$b,$n) try {$r=Invoke-RestMethod "$u/incr" -Method Post -ContentType "application/json" -Body $b;"$n response: $($r|ConvertTo-Json -Compress)"}catch{"$n ERROR: $($_.Exception.Message)"}}
$jobs+=Start-Job -ArgumentList $EU,$bEU,"Europe" -ScriptBlock {param($u,$b,$n) try {$r=Invoke-RestMethod "$u/incr" -Method Post -ContentType "application/json" -Body $b;"$n response: $($r|ConvertTo-Json -Compress)"}catch{"$n ERROR: $($_.Exception.Message)"}}
$jobs+=Start-Job -ArgumentList $ASIA,$bAS,"Asia" -ScriptBlock {param($u,$b,$n) try {$r=Invoke-RestMethod "$u/incr" -Method Post -ContentType "application/json" -Body $b;"$n response: $($r|ConvertTo-Json -Compress)"}catch{"$n ERROR: $($_.Exception.Message)"}}
Wait-Job $jobs|Out-Null;$jobs|ForEach-Object{Receive-Job $_};$jobs|Remove-Job
Write-Host "`nCounter key: $key ; expected total = 10" -ForegroundColor Cyan
$deadline=(Get-Date).AddSeconds(20);$ok=$false
do {
 Start-Sleep -Milliseconds 500
 try {$us=Invoke-RestMethod "$US/counter/$key";$eu=Invoke-RestMethod "$EU/counter/$key";$asia=Invoke-RestMethod "$ASIA/counter/$key";if($us.value -eq 10 -and $eu.value -eq 10 -and $asia.value -eq 10){$ok=$true;break}}catch{}
} while((Get-Date)-lt $deadline)
Write-Host "US     -> $($us.value)";Write-Host "Europe -> $($eu.value)";Write-Host "Asia   -> $($asia.value)"
if($ok){Write-Host "SUCCESS: all regions converged to 10." -ForegroundColor Green}else{Write-Host "Not converged to 10 within 20 seconds; inspect logs." -ForegroundColor Red}

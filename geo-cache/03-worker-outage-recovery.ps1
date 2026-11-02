$ErrorActionPreference="Stop"
$nodes=@{
 "US"=@{IP="54.242.141.54";Key="D:\Downlods D\geo-cache-us-key.pem";URL="http://54.242.141.54:5000"}
 "Europe"=@{IP="34.241.36.71";Key="D:\Downlods D\geo-cache-eu-key.pem";URL="http://34.241.36.71:5000"}
 "Asia"=@{IP="52.77.218.56";Key="D:\Downlods D\geo-cache-asia-key.pem";URL="http://52.77.218.56:5000"}
}
function Remote-Worker($name,$action){
 $n=$nodes[$name];if(!(Test-Path $n.Key)){throw "PEM key not found: $($n.Key)"}
 $cmd="sudo docker compose -f ~/docker-compose.aws.yml $action worker"
 & ssh.exe -i $n.Key -o BatchMode=yes "ubuntu@$($n.IP)" $cmd
 if($LASTEXITCODE -ne 0){throw "SSH $action failed for $name"}
}
Write-Host "`n=== WORKER OUTAGE / RECOVERY DEMO ===" -ForegroundColor Cyan
Write-Host "1. US  2. Europe  3. Asia"
$c=Read-Host "Choose worker to stop (1/2/3)"
$down=switch($c){"1"{"US"}"2"{"Europe"}"3"{"Asia"}default{throw "Invalid choice"}}
$alive=@("US","Europe","Asia")|Where-Object{$_ -ne $down}
Write-Host "Stopping only the $down Flask worker; EC2 and Redis stay up..." -ForegroundColor Yellow
Remote-Worker $down "stop"
$key="demo-outage-"+(Get-Date -Format "yyyyMMdd-HHmmss-fff")
Write-Host "Writing counter updates while $down is down. Key=$key" -ForegroundColor Cyan
$jobs=@()
foreach($name in $alive){
 $n=$nodes[$name];$amt=switch($name){"US"{4}"Europe"{6}"Asia"{8}}
 $body=(@{key=$key;amount=$amt}|ConvertTo-Json -Compress)
 $jobs+=Start-Job -ArgumentList $n.URL,$body,$name,$amt -ScriptBlock {param($u,$b,$name,$amt) try {$r=Invoke-RestMethod "$u/incr" -Method Post -ContentType "application/json" -Body $b;"$name +$amt -> $($r|ConvertTo-Json -Compress)"}catch{"$name ERROR: $($_.Exception.Message)"}}
}
Wait-Job $jobs|Out-Null;$jobs|ForEach-Object{Receive-Job $_};$jobs|Remove-Job
Write-Host "`nSurviving nodes should accept writes. Press ENTER to restart $down." -ForegroundColor Yellow
[void](Read-Host)
Remote-Worker $down "start"
Write-Host "Worker restarted. Waiting up to 30 seconds for queued sync deliveries..." -ForegroundColor Cyan
$deadline=(Get-Date).AddSeconds(30);$ok=$false
do {
 Start-Sleep -Milliseconds 750
 try {$vals=@();foreach($name in @("US","Europe","Asia")){$vals+=((Invoke-RestMethod "$($nodes[$name].URL)/counter/$key").value)};if(($vals|Select-Object -Unique).Count -eq 1 -and $vals.Count -eq 3){$ok=$true;break}}catch{}
} while((Get-Date)-lt $deadline)
Write-Host "`nFinal counter values:"
foreach($name in @("US","Europe","Asia")){try{$r=Invoke-RestMethod "$($nodes[$name].URL)/counter/$key";Write-Host "$name -> $($r.value)"}catch{Write-Host "$name -> read failed"}}
if($ok){Write-Host "RECOVERY SUCCESS: all three regions converged." -ForegroundColor Green}else{Write-Host "Recovery not confirmed. Inspect worker logs and retry queue." -ForegroundColor Red}

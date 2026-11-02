param(
    [string]$Dir = "."
)
Set-Location -LiteralPath $Dir
$decks = Get-ChildItem -Filter "m*.cir" | Sort-Object Name
foreach ($d in $decks) {
    $base = $d.BaseName
    Remove-Item "$base.log", "$base.raw", "$base.op.raw", "$base.db" -ErrorAction SilentlyContinue
    & "D:\LTspice.exe" -b $d.Name | Out-Null
    $t0 = Get-Date
    while (-not (Test-Path "$base.log") -and ((Get-Date) - $t0).TotalSeconds -lt 90) {
        Start-Sleep -Milliseconds 300
    }
    if (Test-Path "$base.log") {
        $sz = (Get-Item "$base.log").Length
        Write-Output ("OK      {0}  (log {1} B)" -f $d.Name, $sz)
    } else {
        Write-Output ("TIMEOUT {0}" -f $d.Name)
    }
    Start-Sleep -Milliseconds 200
}

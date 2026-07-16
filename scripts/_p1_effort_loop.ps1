$ticks = 0
$max = 6
while ($ticks -lt $max) {
  Start-Sleep -Seconds 1500
  $ticks++
  python scripts/run_package1_viewport_gate.py | Out-Null
  $stamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
  Write-Output ("AGENT_LOOP_TICK_p1gate tick={0}/{1} stamp={2} pass_check=static_gate" -f $ticks, $max, $stamp)
}

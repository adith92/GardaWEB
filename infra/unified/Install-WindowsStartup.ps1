param(
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$Source,
    [Parameter(Mandatory=$true)][string]$Data,
    [switch]$StartNow
)
$ErrorActionPreference = 'Stop'
$principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if (!$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Run this installer from PowerShell as Administrator to enable startup before Windows login.'
}
$exe = (Resolve-Path -LiteralPath $Python).Path
$work = (Resolve-Path -LiteralPath $Source).Path
$state = (Resolve-Path -LiteralPath $Data).Path
if (!(Test-Path -LiteralPath (Join-Path $state 'server-settings.json'))) { throw 'Configure the NVR and HTTPS first.' }
if (Get-ScheduledTask -TaskName 'GARDA-NVR-Server' -ErrorAction SilentlyContinue) { throw 'GARDA startup task exists; review it before replacing.' }
$arguments = '-m garda_ai.server serve --data "' + $state + '"'
$action = New-ScheduledTaskAction -Execute $exe -Argument $arguments -WorkingDirectory $work
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew
$account = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName 'GARDA-NVR-Server' -Action $action -Trigger $trigger -Settings $settings -Principal $account -Description 'GARDA HTTPS + independent NVR recorder; restart on failure, no time limit' | Out-Null
if ($StartNow) { Start-ScheduledTask -TaskName 'GARDA-NVR-Server' }
Get-ScheduledTask -TaskName 'GARDA-NVR-Server' | Select-Object TaskName,State

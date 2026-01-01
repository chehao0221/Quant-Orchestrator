<#
建立 Windows 登入自動執行 Quant-Orchestrator 閉環任務
PowerShell (系統管理員) 執行：

powershell -ExecutionPolicy Bypass -File .\scripts\windows_task_create.ps1 `
  -RepoRoot "D:\Quant-Orchestrator" `
  -VaultRoot "E:\Quant-Vault" `
  -PythonExe "C:\Path\to\python.exe"
#>

param(
  [Parameter(Mandatory=$true)][string]$RepoRoot,
  [Parameter(Mandatory=$true)][string]$VaultRoot,
  [Parameter(Mandatory=$false)][string]$PythonExe = "python.exe",
  [Parameter(Mandatory=$false)][string]$TaskName = "QuantOrchestrator-AutoCycle"
)

$RepoRoot = (Resolve-Path $RepoRoot).Path
$RunCycle = Join-Path $RepoRoot "scripts\run_cycle.py"

$Action = New-ScheduledTaskAction -Execute $PythonExe -Argument "`"$RunCycle`" --vault-root `"$VaultRoot`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force | Out-Null
Write-Host "✅ Task created: $TaskName"

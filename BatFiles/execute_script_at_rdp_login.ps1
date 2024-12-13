
# 2024-11-25 09:28:05 - creates a scheduled task that executes when an RDP connection is made.
# Use this by get by the default restricted script policy:
# powershell -ExecutionPolicy Bypass -File execute_script_at_rdp_login.ps1


$action = New-ScheduledTaskAction -Execute "C:\Users\rgw3\pc-oswald\rdp_connection.bat"
$trigger = New-ScheduledTaskTrigger -AtLogon
Register-ScheduledTask StartAtUserLogin -Action $action -Trigger $trigger -Description "Schedule Task at User Login" -RunLevel Highest

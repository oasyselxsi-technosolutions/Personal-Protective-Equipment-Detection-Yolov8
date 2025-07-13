# PowerShell script to run Flask app with logging
# Usage: .\run_flask_with_logs.ps1 [port]
# Example: .\run_flask_with_logs.ps1 5000

param(
    [string]$Port = "5000"
)

# Create logs directory if it doesn't exist
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "Created logs directory"
}

# Generate timestamp for log file
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "logs\flaskapp_run_$timestamp.log"

# Create log header
$header = @"
===============================================================================
FLASK PPE DETECTION APP STARTUP LOG
===============================================================================
Start Time: $(Get-Date)
Port: $Port
Log File: $logFile
Working Directory: $(Get-Location)
PowerShell Version: $($PSVersionTable.PSVersion)
===============================================================================

"@

# Write header to log file
$header | Out-File -FilePath $logFile -Encoding UTF8

Write-Host "==============================================================================="
Write-Host "FLASK PPE DETECTION APP WITH LOGGING"
Write-Host "==============================================================================="
Write-Host "Port: $Port"
Write-Host "Log file: $logFile"
Write-Host ""
Write-Host "Press Ctrl+C to stop the application"
Write-Host "==============================================================================="
Write-Host ""

try {
    # Start Flask app and capture output
    $process = Start-Process -FilePath "python" -ArgumentList "flaskapp.py", $Port -NoNewWindow -PassThru -RedirectStandardOutput "logs\flask_stdout.log" -RedirectStandardError "logs\flask_stderr.log"
    
    Write-Host "Flask process started with PID: $($process.Id)"
    Write-Host "Monitoring Flask app... (Check logs\flaskapp.log for detailed logs)"
    
    # Monitor the process
    while (-not $process.HasExited) {
        Start-Sleep -Seconds 1
        
        # Display recent stdout if available
        if (Test-Path "logs\flask_stdout.log") {
            $content = Get-Content "logs\flask_stdout.log" -Tail 5 -ErrorAction SilentlyContinue
            if ($content) {
                $content | ForEach-Object { Write-Host $_ }
            }
        }
    }
    
    Write-Host ""
    Write-Host "Flask process ended with exit code: $($process.ExitCode)"
    
} catch {
    Write-Host "Error running Flask app: $($_.Exception.Message)" -ForegroundColor Red
    $_.Exception.Message | Out-File -FilePath $logFile -Append -Encoding UTF8
} finally {
    Write-Host ""
    Write-Host "==============================================================================="
    Write-Host "Flask app stopped at $(Get-Date)"
    Write-Host "Check the following log files for details:"
    Write-Host "  - Main app log: logs\flaskapp.log"
    Write-Host "  - Runtime log: $logFile"
    Write-Host "  - Stdout log: logs\flask_stdout.log"
    Write-Host "  - Stderr log: logs\flask_stderr.log"
    Write-Host "==============================================================================="
    
    # Combine all logs into the main log file
    if (Test-Path "logs\flask_stdout.log") {
        "`n--- STDOUT OUTPUT ---" | Out-File -FilePath $logFile -Append -Encoding UTF8
        Get-Content "logs\flask_stdout.log" | Out-File -FilePath $logFile -Append -Encoding UTF8
    }
    
    if (Test-Path "logs\flask_stderr.log") {
        "`n--- STDERR OUTPUT ---" | Out-File -FilePath $logFile -Append -Encoding UTF8
        Get-Content "logs\flask_stderr.log" | Out-File -FilePath $logFile -Append -Encoding UTF8
    }
    
    Read-Host "Press Enter to exit"
}

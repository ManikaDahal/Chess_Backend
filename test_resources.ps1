
$BASE_URL = "http://localhost:8000"
$REQUESTS  = 30       # Total requests per endpoint
$DELAY_MS  = 100      # Delay between requests (ms) - lower = more load

# Colour helpers
function Green($msg)  { Write-Host $msg -ForegroundColor Green }
function Yellow($msg) { Write-Host $msg -ForegroundColor Yellow }
function Red($msg)    { Write-Host $msg -ForegroundColor Red }
function Cyan($msg)   { Write-Host $msg -ForegroundColor Cyan }


# 1. HEALTH CHECK - make sure the server is up before testing
Cyan "`n=============================="
Cyan " Chess Backend Resource Tester"
Cyan "==============================`n"

Yellow "Checking if server is up at $BASE_URL ..."
try {
    $resp = Invoke-WebRequest -Uri "$BASE_URL/" -UseBasicParsing -TimeoutSec 5
    Green "Server is UP (HTTP $($resp.StatusCode))`n"
} catch {
    Red "Server is NOT reachable at $BASE_URL"
    Red "Make sure you ran: docker-compose up --build"
    exit 1
}


# 2. DEFINE ENDPOINTS TO HIT

$endpoints = @(
    @{ Name = "Home";           Url = "$BASE_URL/";                    Method = "GET"  },
    @{ Name = "Swagger Docs";   Url = "$BASE_URL/api/docs/?format=openapi"; Method = "GET" },
    @{ Name = "Token (POST)";   Url = "$BASE_URL/api/token/";          Method = "POST";
       Body = '{"email":"test@example.com","password":"fakepassword"}' }
    @{ Name = "Signup (POST)";  Url = "$BASE_URL/api/signup/";         Method = "POST";
       Body = '{"username":"loadtest","email":"load@test.com","password":"TestPass123!"}' }
)

# 3. LOAD TEST EACH ENDPOINT

$totalSuccess = 0
$totalFail    = 0
$results      = @()

foreach ($ep in $endpoints) {
    Yellow "Testing: [$($ep.Method)] $($ep.Name) - $REQUESTS requests"
    $success = 0
    $fail    = 0
    $times   = @()

    for ($i = 1; $i -le $REQUESTS; $i++) {
        try {
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            if ($ep.Method -eq "POST") {
                $r = Invoke-WebRequest -Uri $ep.Url -Method POST `
                     -Body $ep.Body -ContentType "application/json" `
                     -UseBasicParsing -TimeoutSec 10
            } else {
                $r = Invoke-WebRequest -Uri $ep.Url -UseBasicParsing -TimeoutSec 10
            }
            $sw.Stop()
            $times += $sw.ElapsedMilliseconds
            $success++
            Write-Host "  [$i/$REQUESTS] HTTP $($r.StatusCode) - $($sw.ElapsedMilliseconds)ms" -ForegroundColor DarkGreen
        } catch {
            $fail++
            Write-Host "  [$i/$REQUESTS] ERROR - $($_.Exception.Message)" -ForegroundColor DarkRed
        }
        Start-Sleep -Milliseconds $DELAY_MS
    }

    $avg = if ($times.Count -gt 0) { [math]::Round(($times | Measure-Object -Average).Average, 1) } else { "N/A" }
    $min = if ($times.Count -gt 0) { ($times | Measure-Object -Minimum).Minimum } else { "N/A" }
    $max = if ($times.Count -gt 0) { ($times | Measure-Object -Maximum).Maximum } else { "N/A" }

    $results += [PSCustomObject]@{
        Endpoint  = $ep.Name
        Success   = $success
        Failed    = $fail
        "Avg(ms)" = $avg
        "Min(ms)" = $min
        "Max(ms)" = $max
    }

    $totalSuccess += $success
    $totalFail    += $fail
    Green "  Done. Success: $success  Failed: $fail  Avg: ${avg}ms`n"
}

# 4. SUMMARY REPORT

Cyan "=============================="
Cyan "         TEST SUMMARY"
Cyan "=============================="

$results | Format-Table -AutoSize

Green "Total Requests : $($totalSuccess + $totalFail)"
Green "Successful     : $totalSuccess"
if ($totalFail -gt 0) {
    Red   "Failed         : $totalFail"
} else {
    Green "Failed         : $totalFail"
}

# 5. DOCKER STATS SNAPSHOT
Cyan "`n=============================="
Cyan "    DOCKER RESOURCE SNAPSHOT"
Cyan "=============================="
Yellow "(This is a one-shot snapshot. For live view, run: docker stats)"

try {
    $statsRaw = docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}" 2>&1
    Write-Host $statsRaw -ForegroundColor Cyan
} catch {
    Yellow "Could not read docker stats - make sure Docker is running."
}

Cyan "`nDone! To monitor live resource usage, keep 'docker stats' running in another terminal."

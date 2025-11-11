# PowerShell script to compile and run all Verilog testbenches
# Requires Icarus Verilog (iverilog) to be installed and in PATH

Write-Host "===== 4-bit Processor Test Suite =====" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0
$TestsRun = 0

# Check if iverilog is available
try {
    $null = Get-Command iverilog -ErrorAction Stop
} catch {
    Write-Host "ERROR: iverilog not found in PATH" -ForegroundColor Red
    Write-Host "Please install Icarus Verilog from: http://bleez.osdn.jp/iverilog_installers/" -ForegroundColor Yellow
    exit 1
}

# Define test configurations
$UnitTests = @(
    @{Name="XOR Gate"; TB="xor_1b_tb"; Modules=@("xor_1b.v")},
    @{Name="1-bit Full Adder"; TB="fa_1b_tb"; Modules=@("xor_1b.v", "fa_1b.v")},
    @{Name="4-bit Adder"; TB="adder_4b_tb"; Modules=@("xor_1b.v", "fa_1b.v", "adder_4b.v")},
    @{Name="4-bit ALU"; TB="alu_4b_tb"; Modules=@("xor_1b.v", "fa_1b.v", "adder_4b.v", "alu_4b.v")},
    @{Name="Registered ALU"; TB="alu_reg_4b_tb"; Modules=@("alu_reg_4b.v")}
)

$IntegrationTest = @{
    Name="Processor Integration"; 
    TB="processor_tb"; 
    Modules=@("xor_1b.v", "fa_1b.v", "adder_4b.v", "alu_4b.v", "alu_reg_4b.v", "decoder_fsm.v", "ram16x4_sync.v", "simple4_proc.v")
}

function Run-Test {
    param($TestConfig)
    
    $TestName = $TestConfig.Name
    $TB = $TestConfig.TB
    $Modules = $TestConfig.Modules
    
    Write-Host "Running: $TestName" -ForegroundColor Yellow
    
    # Build module file list
    $ModuleFiles = $Modules | ForEach-Object { "rtl\$_" }
    $TBFile = "testbenches\${TB}.v"
    $OutFile = "build\${TB}.vvp"
    
    # Create build directory if it doesn't exist
    if (-not (Test-Path "build")) {
        New-Item -ItemType Directory -Path "build" | Out-Null
    }
    
    # Compile
    Write-Host "  Compiling..." -NoNewline
    $CompileArgs = @("-o", $OutFile) + $ModuleFiles + $TBFile
    $CompileResult = & iverilog @CompileArgs 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  Compilation errors:" -ForegroundColor Red
        Write-Host $CompileResult
        return $false
    }
    Write-Host " OK" -ForegroundColor Green
    
    # Run simulation
    Write-Host "  Simulating..." -NoNewline
    $SimResult = & vvp $OutFile 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host $SimResult
        return $false
    }
    
    # Check for PASS in output
    if ($SimResult -match "PASS") {
        Write-Host " PASSED" -ForegroundColor Green
        Write-Host $SimResult | Select-String "PASS|ERROR"
        return $true
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host $SimResult
        return $false
    }
}

# Run unit tests
Write-Host "`n--- Unit Tests ---" -ForegroundColor Cyan
foreach ($Test in $UnitTests) {
    $TestsRun++
    if (-not (Run-Test $Test)) {
        $ErrorCount++
    }
    Write-Host ""
}

# Run integration test
Write-Host "`n--- Integration Test ---" -ForegroundColor Cyan
$TestsRun++
if (-not (Run-Test $IntegrationTest)) {
    $ErrorCount++
}

# Summary
Write-Host "`n===== Test Summary =====" -ForegroundColor Cyan
Write-Host "Tests Run: $TestsRun"
Write-Host "Passed: $($TestsRun - $ErrorCount)" -ForegroundColor Green
Write-Host "Failed: $ErrorCount" -ForegroundColor $(if ($ErrorCount -eq 0) { "Green" } else { "Red" })

if ($ErrorCount -eq 0) {
    Write-Host "`n✅ All tests passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n❌ Some tests failed" -ForegroundColor Red
    exit 1
}

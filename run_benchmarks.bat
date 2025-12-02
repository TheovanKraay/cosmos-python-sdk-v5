@echo off
REM Run Cosmos DB SDK Benchmarks (V4 vs V5)

echo.
echo ====================================================================
echo Cosmos DB SDK Performance Benchmark
echo V4 (Pure Python) vs V5 (Rust-based)
echo ====================================================================
echo.

REM Check if environment variables are set
if "%COSMOS_ENDPOINT%"=="" (
    echo Setting default COSMOS_ENDPOINT to emulator...
    set COSMOS_ENDPOINT=https://localhost:8081
)

if "%COSMOS_KEY%"=="" (
    echo Setting default COSMOS_KEY to emulator key...
    set COSMOS_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==
)

echo Using endpoint: %COSMOS_ENDPOINT%
echo.

REM Run the benchmark
python benchmarks\benchmark_runner.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Benchmark failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ✅ Benchmark completed successfully!
echo.
echo 📊 Results saved to: benchmarks\benchmark_results.json
echo.
pause

# Builds the native hash libraries of Windows x64 into native/lib/windows-amd64/.
# Linux and macOS are native/build.sh. The workflow
# .github/workflows/native.yml runs this; native/README.md says how and when.
#
# Usage, from a PowerShell where cl.exe is on the PATH (a Developer PowerShell
# for Visual Studio, x64): native/build.ps1
#
# Needs the submodules (git submodule update --init), MSVC and rustup (the
# Rust release is pinned in native/museair/rust-toolchain.toml).
#
# The flags are MSVC's equivalents of the ones the original .so files were
# built with: /O2 /Ob0 for -O3 -fno-inline (a5hash), /O2 for -O3 (MeowHash;
# MSVC needs no flag for the AES-NI intrinsics), `cargo build --release`
# (MuseAir).
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$here = $PSScriptRoot
$out = Join-Path $here "lib\windows-amd64"
$obj = Join-Path ([System.IO.Path]::GetTempPath()) "speedupy-native-obj"

foreach ($submodule in "a5hash", "meow_hash", "museair") {
    $dir = Join-Path $here "vendor\$submodule"
    if (-not (Get-ChildItem -Force $dir -ErrorAction SilentlyContinue)) {
        throw "native/vendor/$submodule is empty: run git submodule update --init"
    }
}

Remove-Item -Recurse -Force $out, $obj -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $out, $obj | Out-Null

# The toolchain lines go to the log and to native/build/windows-amd64.txt,
# which native/manifest.py copies into the manifest. cl prints its banner on
# stderr when called with no argument.
Write-Host "== toolchain"
$PSNativeCommandUseErrorActionPreference = $false
$banner = (cl 2>&1 | Select-Object -First 1).ToString()
$PSNativeCommandUseErrorActionPreference = $true
Push-Location (Join-Path $here "museair")
$toolchain = @($banner, (rustc --version), (cargo --version))
Pop-Location
New-Item -ItemType Directory -Force (Join-Path $here "build") | Out-Null
$toolchain | Set-Content (Join-Path $here "build\windows-amd64.txt")
$toolchain | Write-Host

# cl writes the .obj, .lib and .exp files to the current directory; only the
# .dll goes to $out.
Push-Location $obj
try {
    Write-Host "== a5hash"
    cl /nologo /O2 /Ob0 /LD /I (Join-Path $here "vendor\a5hash") `
        (Join-Path $here "src\a5hash_wrapper.c") "/Fe$(Join-Path $out 'a5hash.dll')"

    Write-Host "== MeowHash"
    cl /nologo /O2 /EHsc /LD /I (Join-Path $here "vendor\meow_hash") `
        (Join-Path $here "src\meow_wrapper.cpp") "/Fe$(Join-Path $out 'meow.dll')"
}
finally {
    Pop-Location
}

Write-Host "== MuseAir"
Push-Location (Join-Path $here "museair")
try {
    cargo build --release --locked
}
finally {
    Pop-Location
}
Copy-Item (Join-Path $here "museair\target\release\museair_ffi.dll") (Join-Path $out "museair.dll")

Remove-Item -Force (Join-Path $out "*") -Exclude "*.dll"
Write-Host "== built"
Get-ChildItem $out

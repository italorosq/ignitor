# =============================================================================
#  Renderiza os STLs das caixas e cupons.
#  Requer OpenSCAD 2021.01+ (D:\openscad\openscad.exe neste projeto).
# =============================================================================
$ErrorActionPreference = "Continue"

$scad = "D:\openscad\openscad.exe"
if (-not (Test-Path $scad)) {
    $cand = Join-Path $env:LOCALAPPDATA "Programs\openscad-dev\OpenSCAD-2026.11.01-x86-64\openscad.exe"
    if (Test-Path $cand) { $scad = $cand }
    else {
        $cmd = Get-Command openscad -ErrorAction SilentlyContinue
        if ($cmd) { $scad = $cmd.Source }
    }
}
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$out  = Join-Path $root "out"
New-Item -ItemType Directory -Force -Path $out | Out-Null

$jobs = @(
    @{ src = "comando.scad"; part = 1; name = "comando_body.stl" },
    @{ src = "comando.scad"; part = 2; name = "comando_lid.stl" },
    @{ src = "comando.scad"; part = 3; name = "comando_door.stl" },
    @{ src = "ignicao.scad"; part = 1; name = "ignicao_body.stl" },
    @{ src = "ignicao.scad"; part = 2; name = "ignicao_lid.stl" },
    @{ src = "ignicao.scad"; part = 3; name = "ignicao_door.stl" },
    @{ src = "cupons.scad";  part = 1; name = "cupom_gaxeta_frame.stl" },
    @{ src = "cupons.scad";  part = 2; name = "cupom_gaxeta_lid.stl" },
    @{ src = "cupons.scad";  part = 3; name = "cupom_inserto.stl" }
)

# Atuador 36:1 — seletor por nome (part="caixa"), aspas escapadas para o PowerShell
$atuador = @("caixa", "sun1", "planeta", "carrier1", "saida", "tampa", "gaiola", "boss", "cupom")
foreach ($p in $atuador) {
    $src = Join-Path $root "atuador.scad"
    $dst = Join-Path $out ("atuador_" + $p + ".stl")
    Write-Host "-> atuador_$p.stl"
    & $scad -o $dst -D ('part=\"' + $p + '\"') $src 2>&1 | Out-Null
    if (-not (Test-Path $dst)) { throw "Falha ao gerar atuador_$p.stl" }
}

foreach ($j in $jobs) {
    $src = Join-Path $root $j.src
    $dst = Join-Path $out $j.name
    Write-Host "-> $($j.name)"
    & $scad -o $dst -D ("part=" + $j.part) $src 2>&1 | Out-Null
    if (-not (Test-Path $dst)) {
        throw "Falha ao gerar $($j.name)"
    }
}

Write-Host ""
Write-Host "OK. STLs em: $out"

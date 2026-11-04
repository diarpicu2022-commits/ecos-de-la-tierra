# Lanza sesiones de Claude Code una tras otra hasta la hora limite. Cada sesion
# lee CONTINUAR.md y sigue donde iba la anterior.
#
#   powershell -ExecutionPolicy Bypass -File "tools\seguir de noche.ps1" -Hasta 07:00
#
# Se detiene sola a la hora limite o si existe el archivo .noche-terminada.
# Ctrl+C la detiene antes. Los registros quedan en %TEMP%\ecos de la tierra noche.
param(
    [string]$Hasta = "07:00",
    [int]$EsperaTrasFallo = 15,
    [string]$Permisos = "auto"
)

$raiz = Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $raiz

$limite = [datetime]::ParseExact($Hasta, "HH:mm", $null)
if ($limite -le (Get-Date)) { $limite = $limite.AddDays(1) }

$registros = Join-Path $env:TEMP "ecos de la tierra noche"
New-Item -ItemType Directory -Force -Path $registros | Out-Null

$rama = (git branch --show-current).Trim()
if ($rama -ne "noche/demo-accion") {
    Write-Host "Esta copia esta en la rama '$rama'. Cambia a noche/demo-accion antes de empezar."
    exit 1
}

$sesion = 0
while ((Get-Date) -lt $limite) {
    if (Test-Path -LiteralPath (Join-Path $raiz ".noche-terminada")) {
        Write-Host "Trabajo terminado: existe .noche-terminada."
        break
    }

    # Lo que haya quedado colgado de una sesion cortada no debe gastar memoria.
    Get-Process | Where-Object { $_.ProcessName -like "Godot_v4*" } |
        Stop-Process -Force -ErrorAction SilentlyContinue

    $sesion++
    $horaLimite = $limite.ToString("yyyy-MM-dd HH:mm")
    $encargo = "Turno de noche de Ecos de la Tierra. Lee CONTINUAR.md entero y sigue el primer bloque sin terminar, con sus reglas. Hora limite: $horaLimite. Antes de esa hora deja todo con commit y push en noche/demo-accion."
    $archivo = Join-Path $registros ("sesion {0:000} {1}.txt" -f $sesion, (Get-Date -Format "HH-mm"))

    Write-Host ("[{0}] Sesion {1}. Registro: {2}" -f (Get-Date -Format "HH:mm"), $sesion, $archivo)
    & claude -p $encargo --permission-mode $Permisos --chrome *>&1 | Out-File -LiteralPath $archivo -Encoding utf8
    $codigo = $LASTEXITCODE
    Write-Host ("[{0}] Sesion {1} termino con codigo {2}." -f (Get-Date -Format "HH:mm"), $sesion, $codigo)

    # Si fallo, lo mas probable es el limite de uso: se espera antes de reintentar.
    if ($codigo -ne 0) {
        Start-Sleep -Seconds ($EsperaTrasFallo * 60)
    } else {
        Start-Sleep -Seconds 30
    }
}

Write-Host ("[{0}] Fin del turno de noche." -f (Get-Date -Format "HH:mm"))

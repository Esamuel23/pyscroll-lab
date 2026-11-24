<#
.SYNOPSIS
  Open a file at a line in VS Code and save a screenshot of the VS Code window.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools/ide_snap.ps1 -File src/pyscroll_lab/config.py -Line 20 -Id P1-01 -Name 01-before
  -> docs/snapshots/P1-01/01-before.png

  Used by the change review (docs/REVIEW_FRAMEWORK.md, "IDE snapshots").
  Never open .env or anything under data/ with this: the PNG is committed to a public repo.
#>
param(
  [Parameter(Mandatory)] [string] $File,
  [int] $Line = 1,
  [Parameter(Mandatory)] [string] $Id,
  [Parameter(Mandatory)] [string] $Name,
  [int] $WaitMs = 1500
)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot

$leaf = Split-Path -Leaf $File
if ($leaf -like '.env*' -and $leaf -ne '.env.example') { throw "Refusing to snapshot $File (secrets)." }
if ($File -match '(^|[\\/])data[\\/]') { throw "Refusing to snapshot $File (private channel data)." }
if ($Id -notmatch '^P\d+-(\d{2}|phase)$') { throw "Id must look like P1-03 or P1-phase." }

Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class Win {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("dwmapi.dll")] public static extern int DwmGetWindowAttribute(IntPtr h, int attr, out RECT r, int size);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
}
'@
[Win]::SetProcessDPIAware() | Out-Null

# Open in the existing window for this folder, at the line.
$target = Join-Path $repo $File
if (-not (Test-Path $target)) { throw "No such file: $target" }
& code -r $repo -g "${target}:${Line}" | Out-Null
Start-Sleep -Milliseconds $WaitMs

# A cold start can take several seconds: poll for the window, up to 20 s.
$win = $null
for ($i = 0; $i -lt 40 -and -not $win; $i++) {
  $win = Get-Process Code -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle -like "$leaf - pyscroll-lab*" } |
    Select-Object -First 1
  if (-not $win) { Start-Sleep -Milliseconds 500 }
}
if (-not $win) { throw 'No VS Code window titled pyscroll-lab. Open the folder in VS Code first.' }

$h = $win.MainWindowHandle
[Win]::ShowWindow($h, 3) | Out-Null   # maximize, so long lines fit
[Win]::SetForegroundWindow($h) | Out-Null
Start-Sleep -Milliseconds 800

# Render the window itself (PrintWindow), not the screen: other windows, taskbar
# previews and popups drawn on top can't leak into the image.
$full = New-Object Win+RECT
[Win]::GetWindowRect($h, [ref]$full) | Out-Null
$vis = New-Object Win+RECT   # visible frame, without the invisible resize border
[Win]::DwmGetWindowAttribute($h, 9, [ref]$vis, [Runtime.InteropServices.Marshal]::SizeOf($vis)) | Out-Null
$fw = $full.R - $full.L; $fh = $full.B - $full.T
if ($fw -le 0 -or $fh -le 0) { throw 'Could not read the VS Code window size.' }

$raw = New-Object System.Drawing.Bitmap $fw, $fh
$rg = [System.Drawing.Graphics]::FromImage($raw)
$hdc = $rg.GetHdc()
$ok = [Win]::PrintWindow($h, $hdc, 2)   # 2 = PW_RENDERFULLCONTENT (needed for Electron)
$rg.ReleaseHdc($hdc); $rg.Dispose()
if (-not $ok) { $raw.Dispose(); throw 'PrintWindow failed.' }

$crop = New-Object System.Drawing.Rectangle ($vis.L - $full.L), ($vis.T - $full.T), ($vis.R - $vis.L), ($vis.B - $vis.T)
if ($crop.Width -le 0 -or $crop.Height -le 0) { $crop = New-Object System.Drawing.Rectangle 0, 0, $fw, $fh }
$bmp = $raw.Clone($crop, $raw.PixelFormat)
$raw.Dispose()
$g = [System.Drawing.Graphics]::FromImage($bmp)

$outDir = Join-Path $repo "docs/snapshots/$Id"
New-Item -ItemType Directory -Force $outDir | Out-Null
$out = Join-Path $outDir "$Name.png"
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()

Write-Output $out

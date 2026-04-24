param(
    [string] $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string] $GamePath = "E:\SteamLibrary\steamapps\common\Cities Skylines II",
    [string] $OutputDir = "",
    [string] $ModName = "AiGameModStudioBaseMod",
    [switch] $Force,
    [switch] $Build,
    [switch] $CompileOnly
)

$ErrorActionPreference = "Stop"

if (-not $OutputDir) {
    $OutputDir = Join-Path $RepoRoot "artifacts\cs2-official-template\$ModName"
}

$toolPath = Join-Path $GamePath "Cities2_Data\Content\Game\.ModdingToolchain"
$managedPath = Join-Path $GamePath "Cities2_Data\Managed"
$templatePackage = Join-Path $toolPath "ColossalOrder.ModTemplate.1.0.0.nupkg"
$coreProject = Join-Path $RepoRoot "base-mod\src\AiGameModStudio.BaseMod.Core\AiGameModStudio.BaseMod.Core.csproj"
$runtimeSource = Join-Path $RepoRoot "base-mod\src\AiGameModStudio.CS2Runtime"

if (-not (Test-Path $templatePackage)) {
    throw "Official CS2 mod template package not found: $templatePackage"
}

if (-not (Test-Path (Join-Path $managedPath "Game.dll"))) {
    throw "CS2 managed assemblies not found: $managedPath"
}

if ((Test-Path $OutputDir) -and -not $Force) {
    throw "Output directory already exists. Pass -Force to replace it: $OutputDir"
}

if (Test-Path $OutputDir) {
    Remove-Item -Recurse -Force $OutputDir
}

New-Item -ItemType Directory -Path (Split-Path $OutputDir -Parent) -Force | Out-Null

[Environment]::SetEnvironmentVariable("CSII_TOOLPATH", $toolPath, "User")
[Environment]::SetEnvironmentVariable("CSII_MANAGEDPATH", $managedPath, "User")
[Environment]::SetEnvironmentVariable("CSII_MSCORLIBPATH", (Join-Path $managedPath "mscorlib.dll"), "User")
[Environment]::SetEnvironmentVariable("CSII_ASSEMBLYSEARCHPATH", $managedPath, "User")
[Environment]::SetEnvironmentVariable("CSII_MODPOSTPROCESSORPATH", (Join-Path $toolPath "ModPostProcessor"), "User")
[Environment]::SetEnvironmentVariable("CSII_MODPUBLISHERPATH", (Join-Path $toolPath "ModPublisher"), "User")

$userDataPath = Join-Path $env:LOCALAPPDATA "Colossal Order\Cities Skylines II"
$localModsPath = Join-Path $userDataPath "Mods"
New-Item -ItemType Directory -Path $userDataPath -Force | Out-Null
New-Item -ItemType Directory -Path $localModsPath -Force | Out-Null
[Environment]::SetEnvironmentVariable("CSII_USERDATAPATH", $userDataPath, "User")
[Environment]::SetEnvironmentVariable("CSII_LOCALMODSPATH", $localModsPath, "User")

dotnet new install $templatePackage | Out-Host
dotnet new csiimod -n $ModName -o $OutputDir | Out-Host

Copy-Item (Join-Path $runtimeSource "*.cs") $OutputDir -Force

$csprojPath = Join-Path $OutputDir "$ModName.csproj"
$projectText = Get-Content $csprojPath -Raw

if ($projectText -notmatch "<TargetFramework>") {
    $projectText = $projectText.Replace(
        "<Configurations>Debug;Release</Configurations>",
        "<Configurations>Debug;Release</Configurations>`r`n`t`t<TargetFramework>net48</TargetFramework>")
}

if ($projectText -notmatch "<LangVersion>") {
    $projectText = $projectText.Replace(
        "<TargetFramework>net48</TargetFramework>",
        "<TargetFramework>net48</TargetFramework>`r`n`t`t<LangVersion>latest</LangVersion>")
}

if ($projectText -notmatch "CITIES_SKYLINES_2") {
    $projectText = $projectText.Replace(
        "<LangVersion>latest</LangVersion>",
        "<LangVersion>latest</LangVersion>`r`n`t`t<DefineConstants>`$(DefineConstants);CITIES_SKYLINES_2</DefineConstants>")
}

if ($projectText -notmatch [regex]::Escape($coreProject)) {
    $projectReference = @"

	<ItemGroup>
		<ProjectReference Include="$coreProject" />
	</ItemGroup>
"@
    $projectText = $projectText.Replace("</Project>", "$projectReference`r`n</Project>")
}

if ($CompileOnly -and $projectText -notmatch "AiGameModStudioCompileOnly") {
    $compileOnlyTargets = @"

	<Target Name="AiGameModStudioCompileOnly" BeforeTargets="CoreCompile">
		<ItemGroup>
			<Analyzer Remove="@(Analyzer)" />
		</ItemGroup>
	</Target>
"@
    $projectText = $projectText.Replace("</Project>", "$compileOnlyTargets`r`n</Project>")
}

Set-Content -Encoding UTF8 -Path $csprojPath -Value $projectText

Write-Host "Created official CS2 mod template integration at: $OutputDir"
Write-Host "Copied runtime files from: $runtimeSource"
Write-Host "Referenced Core project: $coreProject"

if ($Build) {
    $buildArgs = @($csprojPath)
    if ($CompileOnly) {
        $buildArgs += "/p:ModPublisherCommand=Update"
    }

    dotnet build @buildArgs
}

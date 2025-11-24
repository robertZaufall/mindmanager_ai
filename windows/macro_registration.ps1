$mindManagerVersion = $null

# take highest version available
if (Test-Path "HKCU:\Software\Mindjet\MindManager\20\AddIns") {
    $mindManagerVersion = "20"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\21\AddIns") {
    $mindManagerVersion = "21"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\22\AddIns") {
    $mindManagerVersion = "22"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\23\AddIns") {
    $mindManagerVersion = "23"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\24\AddIns") {
    $mindManagerVersion = "24"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\25\AddIns") {
    $mindManagerVersion = "25"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\26\AddIns") {
    $mindManagerVersion = "26"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\27\AddIns") {
    $mindManagerVersion = "27"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\28\AddIns") {
    $mindManagerVersion = "28"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\29\AddIns") {
    $mindManagerVersion = "29"
}
if (Test-Path "HKCU:\Software\Mindjet\MindManager\30\AddIns") {
    $mindManagerVersion = "30"
}

if ($null -eq $mindManagerVersion) {
    Write-Output "No MindManager version registry keys found."
    exit 1
}
else {
    Write-Output "Using MindManager version $mindManagerVersion."
}

$localAppDataPath = [System.Environment]::GetFolderPath('LocalApplicationData')  
$baseRegistryPath = "HKCU:\Software\Mindjet\MindManager\$mindManagerVersion\Macro"
$appMacrosPath = (Join-Path $localAppDataPath "Mindjet\MindManager\$mindManagerVersion\macros\windows")
  
# Define the macros with their respective GUIDs, names, and file paths  
$macros = @(
    @{ GUID = "{d4e33db5-e057-4136-822b-a16cda83bf92}"; Name = "MindManager AI"; Path = "mindmanager_ai.mmbas" }
)  

# Loop through each macro and process it  
foreach ($macro in $macros) {  
    # Construct the full registry path for the current macro  
    $registryPath = Join-Path $baseRegistryPath $macro.GUID  
      
    # Check if the registry key exists and delete it if it does  
    if (Test-Path $registryPath) {  
        Remove-Item -Path $registryPath -Recurse  
    }  
  
    # Create the registry key  
    New-Item -Path $registryPath -Force  
  
    # Set the required registry values  
    Set-ItemProperty -Path $registryPath -Name "Name" -Value $macro.Name  
    Set-ItemProperty -Path $registryPath -Name "Path" -Value (Join-Path $appMacrosPath $macro.Path)
    Set-ItemProperty -Path $registryPath -Name "Description" -Value ""  
    Set-ItemProperty -Path $registryPath -Name "Menu" -Value 17 # 0x11 in hexadecimal  

    # Update version references inside the .mmbas file
    $filePath = Join-Path $appMacrosPath $macro.Path
    if (Test-Path $filePath) {
        $fileContent = Get-Content $filePath -Raw
        # Replace any existing digit(s) after 'MindManager\' with the configured version
        $updatedContent = $fileContent -replace '(?<=MindManager\\)\d+', $mindManagerVersion
        
        # Trim trailing newlines
        $updatedContent = $updatedContent.TrimEnd("`r","`n")

        # Write back without adding extra newlines
        [System.IO.File]::WriteAllText($filePath, $updatedContent, [System.Text.Encoding]::UTF8)
    }
}  
  
Write-Output "Registry keys have been successfully created or updated."  

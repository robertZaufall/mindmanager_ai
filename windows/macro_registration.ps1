# Define the base registry path  
$baseRegistryPath = "HKCU:\Software\Mindjet\MindManager\23\Macro"  
  
# Define the macros with their respective GUIDs, names, and file paths  
$macros = @(  
    @{ GUID = "{04d9db3e-16b7-4bd8-aa47-00ebfabb2693}"; Name = "Translate to EN"; Path = "translate_en.mmbas" },  
    @{ GUID = "{056ff458-4156-48c0-a051-0510da9aa1aa}"; Name = "Translate to DE"; Path = "translate_de.mmbas" },  
    @{ GUID = "{07815d9b-2bd4-4dee-acee-15908829985f}"; Name = "Cluster"; Path = "cluster.mmbas" },  
    @{ GUID = "{1ca2390b-fbfe-4bb5-b526-6b3deadf2ba3}"; Name = "Examples"; Path = "examples.mmbas" },  
    @{ GUID = "{2472b281-2c60-4b2a-9ee0-8b360678fcfd}"; Name = "Refine"; Path = "refine.mmbas" },  
    @{ GUID = "{24cb6b18-fcb3-4b01-afab-614c1738d507}"; Name = "Refine Development"; Path = "refine_dev.mmbas" },  
    @{ GUID = "{3f7f8343-ab71-45d3-8abf-c687f61dc7ec}"; Name = "CAPEX_OPEX"; Path = "capex_opex.mmbas" },  
    @{ GUID = "{45e93099-cb4e-41e7-8698-2e36d3954dde}"; Name = "Expertise"; Path = "exp.mmbas" },  
    @{ GUID = "{4aed2571-e766-432a-b08e-81ffb94b7e8b}"; Name = "Project_Organization"; Path = "prj_org.mmbas" },  
    @{ GUID = "{559A2618-399D-4D21-B96E-5919F83F1C4C}"; Name = "Process_Organization"; Path = "prc_org.mmbas" },  
    @{ GUID = "{6591ca0c-3410-48a8-a00a-d6d1ee3c51a1}"; Name = "Project_Process_Organization"; Path = "prj_prc_org.mmbas" },  
    @{ GUID = "{6fd5b0b5-c373-4c6b-9793-2b10d8442ca7}"; Name = "Expertise_Project_Process_Organization"; Path = "exp_prj_prc_org.mmbas" },  
    @{ GUID = "{8133688c-2aa4-4faa-ab9c-07b8cde5d5bf}"; Name = "Complexity_1"; Path = "complexity_1.mmbas" },  
    @{ GUID = "{875aed98-dd01-4667-a3ef-2a87d3fb00b7}"; Name = "Complexity_2"; Path = "complexity_2.mmbas" },  
    @{ GUID = "{e53fe7fc-645d-437a-a8c2-92226dfb5a65}"; Name = "Complexity_3"; Path = "complexity_3.mmbas" },  
    @{ GUID = "{e9e5ac24-228c-46e0-867b-9df3bb2c372a}"; Name = "Generate Image"; Path = "generate_image.mmbas" }  
    @{ GUID = "{eca7391c-87c7-4ba2-be26-5ce7db82f457}"; Name = "Generate Glossary"; Path = "glossary.mmbas" }
)  

# Get the local app data path  
$localAppDataPath = [System.Environment]::GetFolderPath('LocalApplicationData')  
  
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
    Set-ItemProperty -Path $registryPath -Name "Path" -Value (Join-Path $localAppDataPath "Mindjet\MindManager\23\macros\windows\$($macro.Path)")  
    Set-ItemProperty -Path $registryPath -Name "Description" -Value ""  
    Set-ItemProperty -Path $registryPath -Name "Menu" -Value 17 # 0x11 in hexadecimal  
}  
  
Write-Output "Registry keys have been successfully created or updated."  

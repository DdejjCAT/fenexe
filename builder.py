#!/usr/bin/env python3
"""
FENEXE - lolkek 4eburek
"""
import os
import sys
import base64
import subprocess
from pathlib import Path

def create_simple_vbs_script(vbs2exe_b64):
    """Create simple working VBS"""
    return f'''Option Explicit

Dim WshShell, FSO, appData, toolsDir
Dim vbs2exePath, projDir, exePath, exeDir
Dim args

Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

exePath = WScript.ScriptFullName
exeDir = FSO.GetParentFolderName(exePath)

Set args = WScript.Arguments
projDir = ""

If args.Count > 0 Then
    Dim i
    For i = 0 To args.Count - 1
        If FSO.FolderExists(args(i)) Then
            projDir = args(i)
            Exit For
        End If
    Next
End If

If projDir = "" Then
    projDir = exeDir
End If

appData = WshShell.ExpandEnvironmentStrings("%APPDATA%")
toolsDir = appData & "\.screpty_tools"

If Not FSO.FolderExists(toolsDir) Then
    FSO.CreateFolder(toolsDir)
End If

vbs2exePath = toolsDir & "\Vbs_To_Exe.exe"

If Not FSO.FileExists(vbs2exePath) Then
    SaveBase64ToFile "{vbs2exe_b64}", vbs2exePath
End If

If Not FSO.FileExists(projDir & "\main.py") Then
    MsgBox "main.py not found", 16, "Error"
    WScript.Quit 1
End If

' === CREATE SIMPLE LAUNCHER ===
Dim launcherVbs, launcherFile
launcherVbs = projDir & "\_temp_launcher.vbs"
Set launcherFile = FSO.CreateTextFile(launcherVbs, True)

launcherFile.WriteLine "Option Explicit"
launcherFile.WriteLine ""
launcherFile.WriteLine "Dim WshShell, FSO, appData, baseDir"
launcherFile.WriteLine "Dim exePath, exeDir, mainDest, cmd"
launcherFile.WriteLine ""
launcherFile.WriteLine "Set WshShell = CreateObject(""WScript.Shell"")"
launcherFile.WriteLine "Set FSO = CreateObject(""Scripting.FileSystemObject"")"
launcherFile.WriteLine ""
launcherFile.WriteLine "exePath = WScript.ScriptFullName"
launcherFile.WriteLine "exeDir = FSO.GetParentFolderName(exePath)"
launcherFile.WriteLine ""
launcherFile.WriteLine "appData = WshShell.ExpandEnvironmentStrings(""%APPDATA%"")"
launcherFile.WriteLine "baseDir = appData & "".screpty_app"""
launcherFile.WriteLine "If Not FSO.FolderExists(baseDir) Then"
launcherFile.WriteLine "    FSO.CreateFolder(baseDir)"
launcherFile.WriteLine "End If"
launcherFile.WriteLine ""
launcherFile.WriteLine "' Copy files from EXE folder"
launcherFile.WriteLine "Dim projFolder, fileObj, fileName"
launcherFile.WriteLine "Set projFolder = FSO.GetFolder(exeDir)"
launcherFile.WriteLine ""
launcherFile.WriteLine "For Each fileObj In projFolder.Files"
launcherFile.WriteLine "    fileName = LCase(fileObj.Name)"
launcherFile.WriteLine "    If fileName <> ""main.exe"" Then"
launcherFile.WriteLine "        FSO.CopyFile fileObj.Path, baseDir & ""\"" & fileName, True"
launcherFile.WriteLine "    End If"
launcherFile.WriteLine "Next"
launcherFile.WriteLine ""
launcherFile.WriteLine "' Run Python"
launcherFile.WriteLine "mainDest = baseDir & ""\main.py"""
launcherFile.WriteLine "If FSO.FileExists(mainDest) Then"
launcherFile.WriteLine "    On Error Resume Next"
launcherFile.WriteLine "    cmd = ""python "" & Chr(34) & mainDest & Chr(34)"
launcherFile.WriteLine "    WshShell.Run cmd, 1, True"
launcherFile.WriteLine "    If Err.Number <> 0 Then"
launcherFile.WriteLine "        Err.Clear"
launcherFile.WriteLine "        cmd = ""py "" & Chr(34) & mainDest & Chr(34)"
launcherFile.WriteLine "        WshShell.Run cmd, 1, True"
launcherFile.WriteLine "    End If"
launcherFile.WriteLine "    On Error GoTo 0"
launcherFile.WriteLine "Else"
launcherFile.WriteLine "    MsgBox ""main.py not found"", 16, ""Error"""
launcherFile.WriteLine "End If"
launcherFile.WriteLine ""
launcherFile.WriteLine "Set WshShell = Nothing"
launcherFile.WriteLine "Set FSO = Nothing"

launcherFile.Close
Set launcherFile = Nothing

' === CREATE MAIN.EXE ===
Dim launcherExe, cmdStr
launcherExe = projDir & "\main.exe"
cmdStr = Chr(34) & vbs2exePath & Chr(34) & " /vbs " & Chr(34) & launcherVbs & Chr(34) & " /exe " & Chr(34) & launcherExe & Chr(34)
WshShell.Run cmdStr, 0, True

WScript.Sleep 2000

If FSO.FileExists(launcherVbs) Then FSO.DeleteFile launcherVbs

MsgBox "Created main.exe", 64, "Done"

Set WshShell = Nothing
Set FSO = Nothing

Sub SaveBase64ToFile(base64Data, filePath)
    Dim xmlDoc, xmlNode, binaryStream
    Set xmlDoc = CreateObject("MSXML2.DOMDocument")
    Set xmlNode = xmlDoc.createElement("binary")
    xmlNode.DataType = "bin.base64"
    xmlNode.Text = base64Data
    Set binaryStream = CreateObject("ADODB.Stream")
    binaryStream.Type = 1
    binaryStream.Open
    binaryStream.Write xmlNode.NodeTypedValue
    binaryStream.SaveToFile filePath, 2
    binaryStream.Close
End Sub
'''

def main():
    print("=== FINAL BUILDER ===\n")
    
    current_dir = Path.cwd()
    vbs2exe_path = current_dir / "Vbs_To_Exe.exe"
    
    if not vbs2exe_path.exists():
        print("ERROR: Vbs_To_Exe.exe not found")
        input("Press Enter to exit...")
        return 1
    
    print("Found Vbs_To_Exe.exe")
    
    with open(vbs2exe_path, 'rb') as f:
        vbs2exe_b64 = base64.b64encode(f.read()).decode('ascii')
    
    print(f"Encoded")
    
    builder_vbs = current_dir / "final_builder.vbs"
    vbs_content = create_simple_vbs_script(vbs2exe_b64)
    
    with open(builder_vbs, 'w', encoding='utf-8') as f:
        f.write(vbs_content)
    
    print("Created VBS script")
    
    # Create builder.exe
    builder_exe = current_dir / "builder.exe"
    
    version_cmd = f'"{vbs2exe_path}"' + \
                 f' /vbs "{builder_vbs}"' + \
                 f' /exe "{builder_exe}"' + \
                 f' /fileversion "1.0.0.0"' + \
                 f' /productversion "1.0.0.0"' + \
                 f' /productname "fenexe"' + \
                 f' /copyright "@error_kill"' + \
                 f' /description "Python Builder"' + \
                 f' /company "FENEXE"' + \
                 f' /compress'
    
    print("\nCreating builder.exe...")
    
    try:
        result = subprocess.run(
            version_cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Builder.exe created")
        else:
            print(f"Return code: {result.returncode}")
            simple_cmd = f'"{vbs2exe_path}" /vbs "{builder_vbs}" /exe "{builder_exe}"'
            subprocess.run(simple_cmd, shell=True, check=False)
    
    except Exception as e:
        print(f"Error: {e}")
    
    if builder_exe.exists():
        print(f"\n✅ BUILDER.EXE READY")
        print(f"Size: {builder_exe.stat().st_size / 1024:.1f} KB")
        
        # Create simple test main.py
        test_main = current_dir / "main.py"
        if not test_main.exists():
            with open(test_main, 'w') as f:
                f.write('''#!/usr/bin/env python3
import os
import time

print("Test script")
print(f"Time: {time.ctime()}")

# Create test file
test_dir = "C:/Users/FENST4R/Documents/VbsToExePortable/App/VbsToExe/тест"
os.makedirs(test_dir, exist_ok=True)

with open(f"{test_dir}/test.txt", "w") as f:
    f.write(f"Test at {time.ctime()}")

print("Test complete")
input("Press Enter to exit...")
''')
        
        print("\nTest:")
        print("1. builder.exe [folder]")
        print("2. Creates main.exe")
        print("3. main.exe runs Python script")
        
    else:
        print("\nFailed to create builder.exe")
        return 1
    
    # Clean up
    try:
        builder_vbs.unlink()
        print("\nCleaned up")
    except:
        pass
    
    input("\nPress Enter to exit...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
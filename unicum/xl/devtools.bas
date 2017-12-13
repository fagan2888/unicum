Attribute VB_Name = "devtools"
Option Private Module

Private Const mdlNames = "controls,csv,unicum,handlers,helpers,session"


' Excel macro to import the required VBA components (see below, they are hard coded)
' Requires enabling the Excel setting in Options/Trust Center/Trust Center Settings/Macro Settings/Trust access to the VBA project object mode

Sub importCode()
    Dim sFileName As Variant

    'import the code modules
    For Each sFileName In Split(mdlNames, ",")
        sImportPath = ActiveWorkbook.path + Application.PathSeparator + sFileName + ".bas"
        ActiveWorkbook.VBProject.Vbcomponents.Import sImportPath
        
        On Error Resume Next
        Err.Clear
    
        If Err.Number <> 0 Then
            Call MsgBox("Failed to import " & sImportPath & " into project.", vbCritical)
        Else
            Debug.Print "Imported " & sImportPath
        End If
    
        On Error GoTo 0
        
    Next sFileName
    
End Sub


'This Sub removes the code files from the VB Project, for easier versioning of the xlsm template and the VBA code
Sub removeCode()
    Dim cmpComponent As Object
    
    For Each sFileName In Split(mdlNames, ",")
        For Each cmpComponent In ActiveWorkbook.VBProject.Vbcomponents
            If cmpComponent.Name = sFileName Then
                ActiveWorkbook.VBProject.Vbcomponents.Remove cmpComponent
                 
                On Error Resume Next
                Err.Clear
    
                If Err.Number <> 0 Then
                    Call MsgBox("Failed to remove " & sFileName & " from project.", vbCritical)
                Else
                    Debug.Print "Removed " & sFileName
                End If
                Exit For
            
                On Error GoTo 0
            End If
        Next cmpComponent
    Next sFileName
    
End Sub

' Excel macro to export all VBA source code in this project to text files for proper source control versioning
' Requires enabling the Excel setting in Options/Trust Center/Trust Center Settings/Macro Settings/Trust access to the VBA project object model
Sub exportCode()
' ExportCode Macro
' Keyboard Shortcut: Ctrl+e

    Const Module = 1
    Const ClassModule = 2
    Const Form = 3
    Const Document = 100
    Const Padding = 24
    
    Dim VBComponent As Object
    Dim count As Integer
    Dim path As String
    Dim directory As String
    Dim extension As String
    
    directory = ActiveWorkbook.path
    count = 0
    
    For Each VBComponent In ActiveWorkbook.VBProject.Vbcomponents
        Select Case VBComponent.Type
            Case ClassModule, Document
                extension = ".cls"
            Case Form
                extension = ".frm"
            Case Module
                extension = ".bas"
            Case Else
                extension = ".txt"
        End Select
            
                
        On Error Resume Next
        Err.Clear
        
        If extension = ".bas" Then
            path = directory & Application.PathSeparator & VBComponent.Name & extension
            Call VBComponent.Export(path)
        End If
        
        If Err.Number <> 0 Then
            Call MsgBox("Failed to export " & VBComponent.Name & " to " & path, vbCritical)
        Else
            count = count + 1
            Debug.Print "Exported " & Strings.Left$(VBComponent.Name & ":" & Strings.Space$(Padding), Padding) & path
        End If

        On Error GoTo 0
    Next
End Sub




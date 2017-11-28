Attribute VB_Name = "code"
Option Private Module


' Excel macro to import all VBA source code into this project from given folder
' Requires enabling the Excel setting in Options/Trust Center/Trust Center Settings/Macro Settings/Trust access to the VBA project object model
Private Sub loadCode(Optional ByVal FolderName As String)

For Each FileName In objFSO.GetFolder(FolderName).Files
    ext = Right(FileName, 3)
    If helpers.inArray(ext, Arrray("cls", "bas")) Then
        path = FolderName + Application.PathSeparator + FileName
        cmpComponents.Import path
    
                    
        On Error Resume Next
        Err.Clear
    
        If Err.Number <> 0 Then
            Call MsgBox("Failed to import " & FileName & " into project.", vbCritical)
        Else
            count = count + 1
            Debug.Print "Imported " & Left$(FileName & ":" & Space(Padding), Padding) & path
        End If
    
        On Error GoTo 0

    End If
Next

End Sub
    

' Excel macro to export all VBA source code in this project to text files for proper source control versioning
' Requires enabling the Excel setting in Options/Trust Center/Trust Center Settings/Macro Settings/Trust access to the VBA project object model
Private Sub exportCode()
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
    
    For Each VBComponent In ActiveWorkbook.VBProject.VBComponents
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
        
        path = directory & Application.PathSeparator & VBComponent.Name & extension
        Call VBComponent.Export(path)
        
        If Err.Number <> 0 Then
            Call MsgBox("Failed to export " & VBComponent.Name & " to " & path, vbCritical)
        Else
            count = count + 1
            Debug.Print "Exported " & Left$(VBComponent.Name & ":" & Space(Padding), Padding) & path
        End If

        On Error GoTo 0
    Next
End Sub




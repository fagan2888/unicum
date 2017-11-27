Attribute VB_Name = "procedures"
Sub ViewCache()

    keys = functions.session.call_session_get("keys", "VisibleObject")
    keys = Mid(keys, 2, Len(keys) - 2)
    keys = Replace(keys, """", "")
    keys = Replace(keys, ",", vbLf)
    MsgBox keys, vbInformation, "Object Cache"
    
End Sub

Sub OpenObject()

    MsgBox "Under construction."

End Sub


Sub BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)

Dim Handles As Variant
Dim ObjectType As Variant
ObjectType = Empty

' set outupt anchor
    Dim Anchor As Worksheet
    Set Anchor = Worksheets("OBJECT")
    
' get in default folder
    d_folder = GetSetup("WORKBOOK", "DefaultFolder")

' build list of obj
    For Each sel In Target
        request = sel.Value
        request = Split(request, ":")(0)
        ' try simple LoadObjsFromFile
        contents = Application.Run("LoadObjsFromFile", , , request)
        ' try LoadObjsFromFile from default folder
        If Not IsArray(contents) Then: contents = Application.Run("LoadObjsFromFile", , , d_folder & "\" & request)
        ' try open obj and write to a new sheet
        WriteMultObject contents, Anchor
    Next
        
' get object from cache
    For Each sel In Target
        request = sel.Value
        request = Split(request, ":")(0)
        ' try open obj and write to a new sheet
        List = Application.Run("ListObj")
        If IsArray(List) Then
            For k = LBound(List, 1) To UBound(List, 1)
                If request = List(k, 1) Then
                    WriteObject List(k, 1), List(k, 2), Anchor
                End If
            Next
        End If
    Next

End Sub




' *** helper ***


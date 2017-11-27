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

' build list of obj
    For Each sel In Target
        ' try simple LoadObjsFromFile
        ' try LoadObjsFromFile from default folder
        ' try open obj and write to a new sheet
    Next
        
' get object from cache
    For Each sel In Target
        ' check if object exists in cache
        ' if yes, open obj and write to a new sheet
    Next

End Sub

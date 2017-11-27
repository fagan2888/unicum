Attribute VB_Name = "menu"
Sub ToggleButtons()
Attribute ToggleButtons.VB_ProcData.VB_Invoke_Func = " \n14"

    Set logo = by_name("Logo")
    Set Button = by_name("ButtonGroup")
    Set cache = by_name("ObjectCache")
    
    
    pre_logo = logo.Visible
    pre_button = Button.Visible
    pre_cache = cache.Visible
    
    If pre_button Then
        'change listbox name and sheet here
        With cache.ControlFormat
            .RemoveAllItems
            For Each Item In getCache()
                .AddItem Item
            Next
        End With
    ElseIf pre_cache Then
        '~~> Currently selected item index at runtime
        myindex = cache.ControlFormat.Value
        If myindex = 0 Then
            Exit Sub
        End If
        
        '~~> Currently selected item value at runtime
        myitem = cache.ControlFormat.List(myindex)
        MsgBox "selected " & myitem, vbInformation, "Object Cache"
    End If
    
    logo.Visible = pre_cache
    Button.Visible = pre_logo
    cache.Visible = pre_button

End Sub

Private Function by_name(ByVal nameStr As String) As Shape

    For Each Shape In ActiveSheet.Shapes
        If Shape.Name = nameStr Then
            Set by_name = Shape
        End If
    Next
    
End Function


Private Function getCache()

    keys = functions.session.call_session_get("keys", "VisibleObject")
    keys = Mid(keys, 2, Len(keys) - 2)
    keys = Replace(keys, """", "")
    getCache = Split(keys, ",")

End Function


Sub openFile()
    'allow the user to select multiple files
    Application.FileDialog(msoFileDialogOpen).AllowMultiSelect = True
    
    'make the file dialog visible to the user
    intChoice = Application.FileDialog(msoFileDialogOpen).Show
    
    'determine what choice the user made
    If intChoice <> 0 Then
    
        'get the file path selected by the user
        For i = 1 To Application.FileDialog(msoFileDialogOpen).SelectedItems.count
            strPath = Application.FileDialog(msoFileDialogOpen).SelectedItems(i)
            'print the file path to sheet 1
            Debug.Print strPath
        Next i
    
    End If

End Sub


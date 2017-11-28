Attribute VB_Name = "controls"
Private cacheSelection As String

Sub DoubleClick(ByVal Target As Range, Cancel As Boolean)
    ' get in default folder
    'd_folder = GetSetup("DefaultFolder")

    ' get object from cache
    For Each sel In Target
        handlers.writeObjectToSheet sel.Value
    Next

End Sub

Sub ShortcutPasteValue()
' PasteValue Macro
' Keyboard Shortcut: Ctrl+w
On Error Resume Next
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks:=False, Transpose:=False
End Sub

Sub ShortcutPasteValueTranspose()
' PasteValue Macro
' Keyboard Shortcut: Ctrl+t
On Error Resume Next
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks:=False, Transpose:=True
End Sub

Sub ShortcutExtractSheet()
' extractSheet Makro
' Tastenkombination: Strg+m
    ActiveSheet.Move
End Sub


Sub ClickLogo()
    ' opens colored menu buttons
    handlers.showShape Array("RedButton", "LightButton", "YellowButton", "GreyButton", "DarkButton")
End Sub

Sub ClickRed()
    ' load object from source
    showShape "Logo"
    
    targetValue = handlers.getSelectedCell()
    currentSource = helpers.getSetup("Source")
    Select Case currentSource
    Case "Database"
        handlers.loadObjectFromDatabase targetValue
    Case "Server"
        handlers.loadObjectFromServer targetValue
    Case Else
        handlers.loadObjectFromFile targetValue
    End Select
End Sub

Sub ClickLight()

    Dim targetValue As String
    Dim cache() As Variant
    
    ' show cache to pick object
    targetValue = handlers.getSelectedCell()
    cache = functions.showObjectCache()(0)
    Debug.Print "try to load object " & targetValue
    If targetValue = "" Or Not helpers.inArray(targetValue, cache) Then
        fillCache (cache)
        showShape "ObjectCache"
        Exit Sub
    End If
    showShape "Logo"
    If targetValue = "" Then
        helpers.Logger "Object not in Cache.", "WARNING"
    Else
        handlers.writeObjectToSheet targetValue
    End If
End Sub

Sub ClickYellow()
    Dim rng As Range
    Dim ObjectName As String
    ' create object from range
    handlers.showShape "Logo"
    Set rng = ActiveSheet.Range("B6:Z200")
    ObjectName = functions.createObject(rng)
    helpers.Logger "Created object " & ObjectName, "INFO"
End Sub

Sub ClickGrey()
    ' write object to source
    showShape "Logo"
    
    cache = functions.showObjectCache()(0)
    targetValue = handlers.getSelectedCell()
    If Not helpers.inArray(targetValue, cache) Then
        fillCache (cache)
        handlers.showShape "ObjectCache"
        targetValue = getCacheSelection()
    If Not helpers.inArray(targetValue, cache) Then
        targetValue = handlers.openTextDialog()
    
    currentSource = helpers.getSetup("Source")
    Select Case currentSource
    Case "Database"
        handlers.writeObjectToDatabase targetValue
    Case "Server"
        handlers.writeObjectToServer targetValue
    Case Else
        handlers.writeObjectToFile targetValue
    End Select
End Sub

Sub ClickDark()
    ' select source
    handlers.showShape "Logo"

    MsgBox "select source by entering relevante data"
End Sub

Sub ClickCache()
    ' show selected object
    Set currentShape = handlers.getShape("ObjectCache")
    ' currently selected item index at runtime
    myindex = currentShape.ControlFormat.Value
    If myindex = 0 Then Exit Sub
    ' currently selected item value at runtime
    myitem = currentShape.ControlFormat.List(myindex)
    handlers.showShape "Logo"
    
    MsgBox "selected " & myitem, vbInformation, "Object Cache"
End Sub

Private Sub fillCache(ByVal cache)
    Set currentShape = handlers.getShape("ObjectCache")
    With currentShape.ControlFormat
        .RemoveAllItems
        For Each Item In cache
            .AddItem Item
        Next
    End With
End Sub

Private Function getCacheSelection()
    Set logo = handlers.getShape("Logo")
    cnt = 0
    Max = 1000
    While cnt < Max And Not logo.Visible And cacheSelection = ""
        getCacheSelection = cacheSelection
    Wend
    cacheSelection = ""
End Function

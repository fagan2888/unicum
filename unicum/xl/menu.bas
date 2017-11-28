Attribute VB_Name = "menu"

Private currentSource As String


Sub BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)

    ' get object from cache
    For Each sel In Target
        menu.pasteObject sel.Value
    Next
    
    Target.Offset(1, 0).Activate
    
End Sub

Sub Logo_OnClick()
    ' opens colored menu buttons
    showShape Array("RedButton", "LightButton", "YellowButton", "GreyButton", "DarkButton")
End Sub

Sub Red_OnClick()
    ' load object from source
    showShape "Logo"
    
    targetValue = getSelectedCell()
    Select Case currentSource
    Case "Database"
        loadDatabase targetValue
    Case "Server"
        loadServer targetValue
    Case Else
        loadFile targetValue
    End Select
End Sub

Sub Light_OnClick()
    ' show cache to pick object
    showShape "Logo"

    targetValue = getSelectedCell()
    cache = getCache()
    If Not IsInArray(targetValue, cache) Then
        Set currentShape = getShape("ObjectCache")
        With currentShape.ControlFormat
            .RemoveAllItems
            For Each Item In getCache()
                .AddItem Item
            Next
        End With
        showShape "ObjectCache"
        Exit Sub
    End If
    
    pasteObject targetValue
End Sub

Sub Yellow_OnClick()
    ' create object from range
    showShape "Logo"
    Set rng = ActiveSheet.Range("B6:Z200")
    MsgBox "create object from sheet"
End Sub

Sub Grey_OnClick()
    ' write object to source
    showShape "Logo"
        
    targetValue = getSelectedCell()
    Select Case currentSource
    Case "Database"
        writeDatabase targetValue
    Case "Server"
        writeServer targetValue
    Case Else
        writeFile targetValue
    End Select
End Sub

Sub Dark_OnClick()
    ' select source
    showShape "Logo"

    MsgBox "select source by entering relevante data"
End Sub

Sub Cache_OnClick()
    ' show selected object
    Set currentShape = getShape("ObjectCache")
    
    ' currently selected item index at runtime
    myindex = currentShape.ControlFormat.Value
    If myindex = 0 Then Exit Sub
    
    ' currently selected item value at runtime
    myitem = currentShape.ControlFormat.List(myindex)
    showShape "Logo"
    
    MsgBox "selected " & myitem, vbInformation, "Object Cache"
End Sub


' **************************************************************
' ***                   private subs                         ***
' **************************************************************

Private Sub pasteObject(ByVal ObjectName As String)
    cache = getCache()

    If IsInArray(ObjectName, cache) Then
        MsgBox "show object in template worksheet"
    End If
End Sub


Private Function getSelectedCell()
    'getSelectedCell = ActiveSheet.Selection.Range.Value
    getSelectedCell = "<Value>"
End Function

Private Function getShape(ByVal nameStr As String) As Shape
    For Each currentShape In ActiveSheet.Shapes
        If currentShape.Name = nameStr Then
            Set getShape = currentShape
            Exit For
        End If
    Next
End Function

Private Sub showShape(ByVal nameStr)
    If Not IsArray(nameStr) Then nameStr = Array(nameStr)
        
    For Each currentShape In ActiveSheet.Shapes
        If IsInArray(currentShape.Name, nameStr) Then
            currentShape.Visible = True
        Else
            currentShape.Visible = False
        End If
    Next
End Sub

Private Function IsInArray(ByVal stringToBeFound As String, ByVal arr As Variant) As Boolean
  IsInArray = (UBound(Filter(arr, stringToBeFound)) > -1)
End Function

Private Function getCache()
    keys = functions.session.call_session_get("keys", "VisibleObject")
    keys = Mid(keys, 2, Len(keys) - 2)
    keys = Replace(keys, """", "")
    getCache = Split(keys, ",")
End Function

Private Sub loadFile(Optional ByVal FileName As String)
    If FileName = "" Then FileName = openFileDialog()
    MsgBox "load object from file " & FileName
End Sub

Private Sub writeFile(Optional ByVal ObjectName As String)
    If ObjectName = "" Then ObjectName = openTextDialog()
    FileName = openFileDialog()
    MsgBox "write object to file"
End Sub

Private Sub loadDatabase(Optional ByVal ObjectName As String)
    If ObjectName = "" Then ObjectName = openTextDialog()
    MsgBox "load object from database"
End Sub

Private Sub writeDatabase(Optional ByVal ObjectName As String)
    If ObjectName = "" Then ObjectName = openTextDialog()
    MsgBox "write object to database"
End Sub

Private Sub loadServer(Optional ByVal ObjectName As String)
    If ObjectName = "" Then ObjectName = openTextDialog()
    MsgBox "load object from http server"
End Sub

Private Sub writeServer(Optional ByVal ObjectName As String)
    If ObjectName = "" Then ObjectName = openTextDialog()
    MsgBox "write object to server"
End Sub


Private Function openFileDialog()
    MsgBox "open file dialog"
    openFileDialog = "<FileName>"
End Function

Private Function openTextDialog()
    MsgBox "open text dialog"
    openTextDialog = "<ObjectName>"
End Function


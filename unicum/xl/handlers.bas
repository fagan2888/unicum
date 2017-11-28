Attribute VB_Name = "handlers"

Option Private Module


Sub writeObjectToSheet(ByVal ObjectName As String)
    
    cache = functions.showObjectCache()(0)
    If Not helpers.inArray(ObjectName, cache) Then Exit Sub
    
    targetSheetName = helpers.getSetup("TemplateSheet")
    Sheets(targetSheetName).Visible = True
    Sheets(targetSheetName).Select
    Sheets(targetSheetName).Copy After:=Sheets(targetSheetName)
    Sheets(targetSheetName).Visible = False
    ActiveSheet.Visible = True

    Application.ScreenUpdating = False

    Dim mD As New DataObject
    
    topLeft = getSetup("TopLeftCell")
    Set TopLeftCell = ActiveSheet.Range(topLeft).Cells(1, 1)
    
    allPropFlag = getSetup("AllProperties")
    objRng = functions.showObject(ObjectName, allPropFlag)

    For i = LBound(objRng) To UBound(objRng)
        Line = objRng(i)
        For j = LBound(Line) To UBound(Line)
            TopLeftCell.Offset(i, j).Value = Line(j)
        Next
    Next
    TopLeftCell.Offset(1, 1).Select

    ActiveSheet.Name = ObjectName

Application.ScreenUpdating = True

End Sub

Function getSelectedCell()
    getSelectedCell = ""
    If TypeOf Selection Is Excel.Range Then getSelectedCell = Selection.Cells(1, 1).Value
End Function

Function getShape(ByVal nameStr As String) As Shape
    For Each currentShape In ActiveSheet.Shapes
        If currentShape.Name = nameStr Then
            Set getShape = currentShape
            Exit For
        End If
    Next
End Function

Sub showShape(ByVal nameStr)
    If Not IsArray(nameStr) Then nameStr = Array(nameStr)
        
    For Each currentShape In ActiveSheet.Shapes
        If helpers.inArray(currentShape.Name, nameStr) Then
            currentShape.Visible = True
        Else
            currentShape.Visible = False
        End If
    Next
End Sub

Sub loadObjectFromFile(Optional ByVal FileName As String)
    If FileName = "" Then FileName = openFileDialog()
    MsgBox "load object from file " & FileName
End Sub

Sub writeObjectToFile(Optional ByVal ObjectName As String)
    FileName = openFileDialog()
    MsgBox "write object to file"
End Sub

 Sub loadObjectFromDatabase(Optional ByVal ObjectName As String)
    If ObjectName = "" Then ObjectName = openTextDialog()
    MsgBox "load object from database"
End Sub

 Sub writeObjectToDatabase(Optional ByVal ObjectName As String)
    If ObjectName = "" Then ObjectName = openTextDialog()
    MsgBox "write object to database"
End Sub

Sub loadObjectFromServer(Optional ByVal ObjectName As String)
    If ObjectName = "" Then ObjectName = openTextDialog()
    MsgBox "load object from http server"
End Sub

Sub writeObjectToServer(Optional ByVal ObjectName As String)
    If ObjectName = "" Then ObjectName = openTextDialog()
    MsgBox "write object to server"
End Sub


' *** private ***

Private Function openFileDialog(Optional ByVal FolderStr As String)
    MsgBox "open file dialog in folder " & FolderStr
    openFileDialog = "<FileName>"
End Function

Function openTextDialog()
    MsgBox "open text dialog"
    openTextDialog = "<ObjectName>"
End Function

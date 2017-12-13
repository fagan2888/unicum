Attribute VB_Name = "handlers"
Option Private Module
Private Const CACHE_SHAPE_NAME = "ObjectCache"
Private cacheSelection As String
Private cacheOpen As String

Sub notImplemented()
    helpers.Logger "Not implemented.", "WARNING"
End Sub

' *** shape handler ***

Sub showShape(ByVal nameStr)
    Dim currentShape As Shape

    If Not IsArray(nameStr) Then nameStr = Array(nameStr)
    For Each currentShape In ActiveSheet.Shapes
        currentShape.Visible = helpers.inArray(currentShape.Name, nameStr)
    Next
End Sub

Private Sub fillShape(ByVal cache, ByVal shapeName As String)
    Dim item As Variant
    Dim currentShape As Object

    ' find shape by name
    For Each currentShape In ActiveSheet.Shapes
        If currentShape.Name = nameStr Then
            Set currentShape = currentShape
            Exit For
        End If
    Next

    ' fill shape with cache entries
    With currentShape.ControlFormat
        .RemoveAllItems
        For Each item In cache
            .AddItem item
        Next
    End With
End Sub


Private Function getObjectName(Optional ByVal ObjectName As String, Optional ByVal callSub As String)
    Dim cacheShape As Object
    Dim targetValue As String
    Dim cache() As Variant
    Dim item As Variant

    ' else pick object from cache
    cache = unicum.getObjectCache()(0)

    ' if current selection it is a range, pick first cell
    If TypeOf Selection Is Excel.Range Then
        targetValue = Selection.Cells(1, 1).Value
        If targetValue <> "" And helpers.inArray(targetValue, cache) Then
            getObjectName = targetValue
            Exit Function
        End If
    End If


    ' find shape by name
    For Each cacheShape In ActiveSheet.Shapes
        If cacheShape.Name = CACHE_SHAPE_NAME Then Exit For
    Next

    ' fill shape with cache entries and show
    With cacheShape.ControlFormat
        .RemoveAllItems
        For Each item In cache
            .AddItem item
        Next
    End With
    handlers.showShape CACHE_SHAPE_NAME

    ' pick selected name for
    cacheOpen = callSub

End Function

Sub getSelectionFromShape(Optional ByVal nameStr As String)
    Dim currentShape As Object
    Dim myindex As Long
    Dim myitem As String

    If nameStr = "" Then nameStr = CACHE_SHAPE_NAME
    For Each currentShape In ActiveSheet.Shapes
        If currentShape.Name = nameStr Then Exit For
    Next

    If TypeOf currentShape Is Excel.Shape Then
        myindex = currentShape.ControlFormat.Value
        If myindex = 0 Then Exit Sub
        myitem = currentShape.ControlFormat.List(myindex)
    End If

    Select Case cacheOpen
    Case "writeObjectToSheet"
        handlers.writeObjectToSheet myitem
    Case "writeObjectToFile"
        handlers.writeObjectToFile myitem
    Case Else
        MsgBox "selected " & myitem, vbInformation
        handlers.notImplemented
    End Select
End Sub


' *** file handler ***

Sub loadObjectFromFile(Optional ByVal fileName As String)
    Dim fileContent As String
    Dim iFile As Integer: iFile = FreeFile

    If fileName = "" Then fileName = CStr(Application.GetOpenFilename)

    If fileName <> "" And fileName <> CStr(False) Then
        Open fileName For Input As #iFile
        fileContent = Input(LOF(iFile), iFile)
        Close #iFile

        helpers.Logger "load content from file " & fileName, "INFO"
        helpers.Logger fileContent, "PRINT"

        obj = unicum.createObjectFromJson(fileContent)
    End If
End Sub

Sub writeObjectToFile(Optional ByVal ObjectName As String)
    Dim objectJson As String
    Dim allPropFlag
    Dim fileName

    If ObjectName = "" Then ObjectName = handlers.getObjectName(ObjectName, "writeObjectToFile")

    If ObjectName <> "" Then
        allPropFlag = getSetup("AllProperties")
        objectJson = unicum.writeObjectToJson(ObjectName, allPropFlag)

        fileName = Application.GetSaveAsFilename(ObjectName)
        If CStr(fileName) <> CStr(False) Then
            fileName = Split(fileName, ".", 2)(0) & ".json"

            Open fileName For Output As #1
            Print #1, objectJson
            Close #1

            helpers.Logger "write content to file " & fileName, "INFO"
            helpers.Logger objectJson, "PRINT"
        End If
    End If
End Sub

' *** sheet handler ***

Sub loadObjectFromSheet()
    Dim rng As Range
    Dim topLeft As String
    Dim bottomRight As String
    Dim ObjectName As String

    topLeft = helpers.getSetup("TopLeftCell")
    bottomRight = helpers.getSetup("BottomRightCell")
    Set rng = ActiveSheet.Range(topLeft & ":" & bottomRight)
    ObjectName = unicum.createObjectFromRange(rng)

    helpers.Logger "Created object " & ObjectName, "INFO"
End Sub

Sub writeObjectToSheet(Optional ByVal ObjectName As String)

    If ObjectName = "" Then ObjectName = handlers.getObjectName(ObjectName, "writeObjectToSheet")

    'Check if Object is in the Cache
    Dim OnProperObjectContinue As Boolean
    OnProperObjectContinue = False

    For Each objName In unicum.getObjectCache()(0)
        If objName = ObjectName Then
            OnProperObjectContinue = True
            Exit For
        End If
    Next objName


    If Not OnProperObjectContinue Then
        Exit Sub
    End If

    If ObjectName <> "" Then
        ' get object data
        allPropFlag = helpers.getSetup("AllProperties")
        objRng = unicum.writeObjectToRange(ObjectName, allPropFlag)

        ' disable screen updating
        Application.ScreenUpdating = False

        ' clone template sheet
        targetSheetName = helpers.getSetup("TemplateSheet")
        Sheets(targetSheetName).Visible = True
        Sheets(targetSheetName).Select
        Sheets(targetSheetName).Copy After:=Sheets(targetSheetName)
        Sheets(targetSheetName).Visible = False
        ActiveSheet.Visible = True

        ' fill cloned template sheet
        topLeft = helpers.getSetup("TopLeftCell")
        Set TopLeftCell = ActiveSheet.Range(topLeft).Cells(1, 1)

        For i = LBound(objRng) To UBound(objRng)
            line = objRng(i)
            For j = LBound(line) To UBound(line)
                TopLeftCell.Offset(i, j).Value = line(j)
            Next
        Next
        TopLeftCell.Offset(1, 1).Select

        ' rename sheet by 'ObjectName (#)'
        ' where the name is checked for not allowed characters and shorted if neccessary


        ActiveSheet.Name = helpers.validSheetName(ObjectName)

        ' enable screen updating
        Application.ScreenUpdating = True
    End If
End Sub

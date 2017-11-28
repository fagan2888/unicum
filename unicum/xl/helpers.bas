Attribute VB_Name = "helpers"

Function getUserName()
' function to return user id
    getUserName = UCase(Environ$("UserName"))
End Function

Function getSetup(ByVal Property As String)
    Set Rng = ActiveWorkbook.Sheets("Main").Range("AA:AB")
    For i = 1 To 100
        Debug.Print Rng.Cells(i, 1).Value
        If Rng.Cells(i, 1).Value = Property Then Exit For
    Next
    'found = Application.WorksheetFunction.VLookup(Property, Rng, 1, False)
    getSetup = Rng.Cells(i, 2).Value
End Function

Function dimArray(A)
' function to detect array DimArray
' (implementation as suggested by mircosoft)
    If IsEmpty(A) Then
        dimArray = -1
        Exit Function
    End If
    
    If Not IsArray(A) Then
        dimArray = 0
        Exit Function
    End If


On Error Resume Next
    For i = 1 To 61
        lb = LBound(A, i)
        If Err.Number <> 0 Then Exit For
    Next
    dimArray = i - 1
End Function

Function toArray(ByRef Rng As Range)
    toArray = Application.Transpose(Application.Transpose(Rng))
End Function

Function inArray(ByVal stringToBeFound As String, ByVal arr As Variant) As Boolean
  inArray = (UBound(Filter(arr, stringToBeFound)) > -1)
End Function


Sub Logger(ByVal Msg As String, ByVal Level As String)

    Dim actual_index, level_index As Integer
    Dim actual_level As String
    
    Levels = Array("ALL", "DEBUG", "INFO", "WARNING", "ERROR", "NON")
    Styles = Array(0, 0, vbInformation, vbExclamation, vbCritical, vbCritical)
    
    actual_level = getSetup("WarningLevel")
    
    For i = LBound(Levels) To UBound(Levels)
        If actual_level = Levels(i) Then actual_index = i
        If Level = Levels(i) Then level_index = i
    Next
    
    If actual_index <= level_index Then MsgBox Msg, Styles(level_index)
    
End Sub


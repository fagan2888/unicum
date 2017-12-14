Attribute VB_Name = "helpers"
Option Private Module

Private Const SETUP_SHEET_NAME = "Setup"

Function getUserName()
' function to return user id
    getUserName = UCase(Environ$("UserName"))
End Function

Function getSetup(ByVal Property As String)
    Set rng = ActiveWorkbook.Sheets(SETUP_SHEET_NAME).Range("B:C")
    For i = 1 To 100
        If rng.Cells(i, 1).Value = Property Then Exit For
    Next
    getSetup = rng.Cells(i, 2).Value
    Debug.Print "getSetup: " & Property & " = " & getSetup
End Function

Sub setSetup(ByVal Property As String, ByVal Value As Variant)
    Set rng = ActiveWorkbook.Sheets(SETUP_SHEET_NAME).Range("B:C")
    For i = 1 To 100
        If rng.Cells(i, 1).Value2 = Property Then Exit For
    Next
    Debug.Print "setSetup: " & Property & " = " & Value
    rng.Cells(i, 2).Value2 = Value
End Sub

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

Function inArray(ByVal stringToBeFound As String, ByVal arr As Variant) As Boolean
  inArray = (UBound(Filter(arr, stringToBeFound)) > -1)
End Function


Sub Logger(ByVal Msg As String, ByVal Level As String)
    ' single point of logging
    Dim actual_index, level_index As Integer
    Dim actual_level As String

    Levels = Array("PRINT", "ALL", "DEBUG", "INFO", "WARNING", "ERROR", "NON")
    Styles = Array(0, 0, 0, vbInformation, vbExclamation, vbCritical, vbCritical)

    actual_level = getSetup("WarningLevel")

    For i = LBound(Levels) To UBound(Levels)
        If actual_level = Levels(i) Then actual_index = i
        If Level = Levels(i) Then level_index = i
    Next

    If actual_index <= level_index Then Call MsgBox(Msg, Styles(level_index))
    Debug.Print Level & ": " & Msg
End Sub

Function validSheetName(ByVal ProposedName As String)
    ' Check if proposed sheetname does not contain characters that
    ' are not allowed in a name

    Dim n As Integer
    strNotAllowed = Array(":", "\", "/", "?", "*", "[", "]")
    For n = 0 To UBound(strNotAllowed)
        ProposedName = Replace(ProposedName, strNotAllowed(n), "")
    Next

    Dim cnt As Integer
    Dim num As Integer

    ProposedName = Left(ProposedName, 25)

    
    ' rename sheet by 'ProposedName (#)'
    For Each sheet In Sheets
        If InStr(1, sheet.Name, ProposedName) Then cnt = cnt + 1
    Next

    If cnt > 0 Then
        ProposedName = ProposedName & " (" & CStr(cnt) & ")"

    End If

    validSheetName = ProposedName
End Function

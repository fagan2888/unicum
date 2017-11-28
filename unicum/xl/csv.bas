Attribute VB_Name = "csv"

'**************************************************************************************************
'***                                                                                            ***
'***                                   private constants                                        ***
'***                                                                                            ***
'**************************************************************************************************

Const CSV_START = "[["
Const CSV_CRLF = "],["
Const CSV_END = "]]"

Const CSV_LINE_START = ""
Const CSV_LINE_END = ""

Const CSV_SEP = ","
Const CSV_QUOTE = """"
Const CSV_DECIMAL = "."

Private Const NV_FLUSH = 128
Private Const NV_REPLACEMENT = ""


'**************************************************************************************************
'***                                                                                            ***
'***                                   public functions                                         ***
'***                                                                                            ***
'**************************************************************************************************

'redim preserve both dimensions for a 2dimension array *ONLY
Public Function ReDimPreserve(aArrayToPreserve As Variant, nNewFirstUBound As Variant, nNewLastUBound As Variant, Optional Value As Variant) As Variant
    Dim nFirst As Long
    Dim nLast As Long
    Dim nOldFirstUBound As Long
    Dim nOldLastUBound As Long

    ReDimPreserve = False
    'check if its in array first
    If IsArray(aArrayToPreserve) Then
        'create new array
        ReDim aPreservedArray(nNewFirstUBound, nNewLastUBound)
        'get old lBound/uBound
        nOldFirstUBound = UBound(aArrayToPreserve, 1)
        nOldLastUBound = UBound(aArrayToPreserve, 2)
        'loop through first
        For nFirst = LBound(aArrayToPreserve, 1) To nNewFirstUBound
            For nLast = LBound(aArrayToPreserve, 2) To nNewLastUBound
                'if its in range, then append to new array the same way
                If nOldFirstUBound >= nFirst And nOldLastUBound >= nLast Then
                    aPreservedArray(nFirst, nLast) = aArrayToPreserve(nFirst, nLast)
                Else
                    aPreservedArray(nFirst, nLast) = Value
                End If
            Next
        Next
        'return the array redimmed
        If IsArray(aPreservedArray) Then ReDimPreserve = aPreservedArray
    End If
End Function

Function Range2Csv(rng As Variant) As String
    Dim csvStr As String
    Dim i As Long
    Dim inner As Variant

    csvStr = CSV_START
    For i = LBound(rng, 1) To UBound(rng, 1)
        If csvStr <> CSV_START Then csvStr = csvStr & CSV_CRLF
        'inner = Application.Transpose(Application.Transpose(Line.Value2))
        inner = rng(i)
        inner = cast(inner)
        inner = Join(inner, CSV_SEP)
        csvStr = csvStr & CSV_LINE_START & inner & CSV_LINE_END
    Next
    csvStr = csvStr & CSV_END
    Range2Csv = csvStr

End Function


Function Csv2Range(ByVal content As String) As Variant

    content = Mid(content, 3, Len(content) - 4)
    lineArray = Split(content, CSV_CRLF, -1, vbTextCompare)
    x = ApplicationFunc
    ReDim dataArray(LBound(lineArray) To UBound(lineArray))
    
    For i = LBound(lineArray) To UBound(lineArray)
        ' TODO: be careful with comma inside of text
        inner = Split(lineArray(i), CSV_SEP, -1, vbTextCompare)
        inner = back(inner)
        dataArray(i) = inner
    Next i
    
    Csv2Range = dataArray
    
End Function


'**************************************************************************************************
'***                                                                                            ***
'***                                   private functions                                        ***
'***                                                                                            ***
'**************************************************************************************************

Private Function cast(ByVal inputArray As Variant)
    Dim outArray() As Variant
    Dim decimal_sep As String
    Dim lctr As Integer
    'Dim Value As Variant

    ReDim outArray(LBound(inputArray) To UBound(inputArray))
    decimal_sep = Application.International(xlDecimalSeparator)

     For lctr = LBound(inputArray) To UBound(inputArray)
        Value = inputArray(lctr)
        
        If IsEmpty(Value) Then
            Value = "null"
        ElseIf Value = True Then
                Value = "true"
        ElseIf Value = False Then
            Value = "false"
        ElseIf Application.IsText(Value) Then
           Value = CSV_QUOTE & Value & CSV_QUOTE
        ElseIf IsDate(Value) Then
            Value = Format(CDate(Value), "YYYYMMDD")
        ElseIf IsNumeric(Value) Then
            If Value = Int(Value) Then
                Value = Format(Value, "#")
            Else
                Value = Format(Value, "#.##")
                Value = Replace(Value, decimal_sep, CSV_DECIMAL)
            End If
        End If
        
        outArray(lctr) = Value
    Next
    cast = outArray
End Function

Private Function back(ByVal inArray As Variant)
    back = inArray
    
    decimal_sep = Application.International(xlDecimalSeparator)
    ReDim outArray(LBound(inArray) To UBound(inArray))

    For lctr = LBound(inArray) To UBound(inArray)
        Value = inArray(lctr)

        Select Case Value
        Case "true"
            Value = True
        Case "false"
            Value = False
        Case "null"
            Value = ""
        Case Else
        
            If Application.IsText(Value) Then
                
                Select Case Mid$(Value, 1, 1)
                Case """"
                    Value = Replace(Value, """", "")
                Case "'"
                    Value = Replace(Value, "'", "")
                Case CSV_QUOTE
                    Value = Replace(Value, CSV_QUOTE, "")
                Case Else
                    If InStr(1, Value, CSV_DECIMAL) Then
                        Value = Replace(Value, CSV_DECIMAL, decimal_sep)
                        Value = CDbl(Value)
                    Else
                        Value = CLng(Value)
                    End If
                End Select
            End If
            
        End Select

        outArray(lctr) = Value
    Next
    
    back = outArray
End Function



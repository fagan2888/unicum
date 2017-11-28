Attribute VB_Name = "functions"

Public session As New clsSession


Function startSession(Optional ByVal url As String, Optional ByVal user As String, Optional ByVal password As String) As String
    If url = "" Then url = "127.0.0.1"
    If Not InStr(1, url, "http://") = 1 Then url = "http://" & url
    If Not InStr(5, url, ":") = 1 Then url = url & ":2699"
    session.init_session url, user, password
    If user = "" Then
        startSession = url
    Else
        startSession = user & "@" & url
    End If
End Function


Function createObject(ByVal rng As Range)
    Dim outArray() As Variant
    Dim cnt As Long
    Dim line As Range
    Dim csv_s As String
    
    ReDim outArray(LBound(rng.Rows.Value) To UBound(rng.Rows.Value))
    cnt = LBound(outArray)
    For Each line In rng.Rows
        outArray(cnt) = Application.Transpose(Application.Transpose(line.Value))
        cnt = cnt + 1
    Next
    csv_s = csv.Range2Csv(outArray)
    csv_s = "{ ""arg0"": ""VisibleObject"", ""arg1"":" & csv_s & ", ""arg2"": ""true""}"
    createObject = session.call_session_post("from_range", csv_s)
End Function


Function getObject(ByVal ObjectClass As String, ByVal ObjectName As String)
    getObject = session.call_session_get("create", ObjectClass, ObjectName, True)
End Function


Function showObject(ByVal ObjectName As String, Optional ByVal AllProperties As Boolean)
    rng_str = session.call_session_get("to_range", ObjectName, AllProperties)
    rng_array = csv.Csv2Range(rng_str)
    'rng_array = csv.ReDimPreserve(rng_array, 100, 100, "")
    showObject = rng_array
End Function


Function modifyObject(ObjectName As String, PropertyName As String, PropertyValue As Variant)
    modifyObject = session.call_session_get("modify_object", ObjectName, PropertyName, PropertyValue)
End Function


Function getObjectProperty(ObjectName As String, PropertyName As String, Optional PropertyItemName As String)
    getObjectProperty = session.call_session_get("get_property", ObjectName, PropertyName, PropertyValue)
End Function


Function removeObject(ObjectName As String)
    removeObject = session.call_session_get("remove", ObjectName)
End Function


Function showObjectCache(Optional ByVal Transpose As Boolean)
    Dim rng_str As String
    Dim rng_array() As Variant

    rng_str = functions.session.call_session_get("keys", "VisibleObject")
    rng_array = csv.Csv2Range("[" & rng_str & "]")
    If Transpose = True Then rng_array = Application.Transpose(rng_array)
    ' rng_array = csv.ReDimPreserve(rng_str, 100, 100, "")
    showObjectCache = rng_array

    'rng_str = Mid(rng_str, 2, Len(rng_str) - 2)
    'rng_str = Replace(rng_str, """", "")
    'rng_array = Split(rng_str, ",")
End Function

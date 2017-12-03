Attribute VB_Name = "unicum"
' cell function for unicum.VisibleObject methods
' (cfg. http://github.com/pbrisk/unicum)

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


Function createObjectFromRange(ByVal rng As Range)
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
    createObjectFromRange = session.call_session_post("from_range", csv_s)
End Function


Function createObjectFromJson(ByVal json_s As String)
    json_s = Replace(json_s, vbCrLf, "")
    json_s = Replace(json_s, vbLf, "")
    json_s = Replace(json_s, vbCr, "")
    json_s = "{ ""arg0"": ""VisibleObject"", ""arg1"":" & json_s & ", ""arg2"": ""true""}"
    createObjectFromJson = session.call_session_post("from_serializable", json_s)
End Function


Function createObject(ByVal ObjectClass As String, ByVal ObjectName As String)
    createObject = session.call_session_get("create", ObjectClass, ObjectName, True)
End Function


Function writeObjectToJson(ByVal ObjectName As String, Optional ByVal AllProperties As Boolean)
    writeObjectToJson = session.call_session_get("save_object_to_string", ObjectName, AllProperties)
End Function


Function writeObjectToRange(ByVal ObjectName As String, Optional ByVal AllProperties As Boolean)
    rng_str = session.call_session_get("to_range", ObjectName, AllProperties)
    rng_array = csv.Csv2Range(rng_str)
    collar = helpers.getSetup("Collar") + 1
    rng_array = csv.Collar4Range(rng_array, collar, collar, "")
    writeObjectToRange = rng_array
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


Function getObjectCache(Optional ByVal Transpose As Boolean)
    Dim rng_str As String
    Dim rng_array() As Variant

    rng_str = session.call_session_get("keys", "VisibleObject")
    rng_array = csv.Csv2Range("[" & rng_str & "]")
    If Transpose = True Then rng_array = Application.Transpose(rng_array)
    'rng_array = csv.Collar4Range(rng_str, 10, 10, "")
    getObjectCache = rng_array
End Function

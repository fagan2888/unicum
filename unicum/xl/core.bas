Attribute VB_Name = "core"
Function listObjectCache(Optional ByVal Transpose As Boolean)
    Dim rng_str As String
    Dim rng_array() As Variant

    rng_str = session.call_session_get("list", "VisibleObject")
    rng_array = csv.Csv2Range("[" & rng_str & "]")
    If Transpose = True And IsArray(rng_array) And IsArray(rng_array(0)) Then rng_array = Application.Transpose(rng_array)
    'rng_array = csv.Collar4Range(rng_str, 10, 10, "")
    listObjectCache = rng_array
End Function


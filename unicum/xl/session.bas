Attribute VB_Name = "session"
Option Private Module

'**************************************************************************************************
'***                                                                                            ***
'***                                   private members                                          ***
'***                                                                                            ***
'**************************************************************************************************


Private Const DEFAULTARG = "arg"

Dim url As String
Dim session_id As String

Private user As String
Private password As String



'**************************************************************************************************
'***                                                                                            ***
'***                                   public methods                                           ***
'***                                                                                            ***
'**************************************************************************************************

Public Function init_session(ByVal url_s As String, Optional ByVal session_id_s As String, Optional ByVal usr_s As String, Optional ByVal pwd_s As String) As String

    url = url_s
    session_id = session_id_s
    user = usr_s
    password = pwd_s

    If session_id = "" Then open_session
    If validate_session Then
        init_session = get_full_path()
    Else
        Msg = "Open new session?"
        ok = MsgBox(Msg, vbOKCancel, "No session found")
        If ok = 1 Then
            open_session
            init_session = get_full_path()
        Else
            init_session = "No valid session at " & get_full_path()
        End If
    End If

End Function


Function call_session_get(Optional ByVal func As String, Optional ByVal p1 As Variant, Optional ByVal p2 As String, Optional ByVal p3 As String, Optional ByVal p4 As String) As Variant
    Dim path_s As String
    Dim query_s As String

    If validate_session Then
        path_s = url_path(session_id, func)
        query_s = url_query(p1, p2, p3, p4)
        call_session_get = send("GET", url, path_s, query_s)
    End If

End Function

Function call_session_post(Optional ByVal func As String, Optional ByVal content_s As String) As Variant

    If validate_session Then
        path_s = url_path(session_id, func)
        call_session_post = send("POST", url, path_s, content_s)
    End If

End Function


Function call_session_delete(Optional ByVal func As String) As Variant

    If validate_session Then
        path_s = url_path(session_id, func)
        call_session_delete = send("DELETE", url, path_s)
    End If

End Function


Function get_valid_session_id() As String
    
    If validate_session Then
        get_valid_session_id = session_id
    Else
        get_valid_session_id = "invalid"
    End If

End Function


Function get_full_path() As String

    If user = "" Then
        get_full_path = url & "/" & session_id
    Else
        get_full_path = user & "@" & url & "/" & session_id
    End If

End Function


'**************************************************************************************************
'***                                                                                            ***
'***                                   private methods                                          ***
'***                                                                                            ***
'**************************************************************************************************

' *** session handling ***

Private Sub open_session()
    On Error GoTo Problem

    session_id = send("GET", url)

    Exit Sub

Problem:
    Msg = "Unable to open new session" & _
            vbCrLf & "Error number: " & Err.Number & _
            vbCrLf & "Error Description: " & Err.Description
    Debug.Print Msg

End Sub



Private Function validate_session()

    On Error GoTo Problem

    validate_session = (Replace(send("GET", url, session_id), VBA.vbLf, "") = "true")

    Exit Function

Problem:
    Msg = "A validation of the session was not possible" & _
            vbCrLf & "Error number: " & Err.Number & _
            vbCrLf & "Error Description: " & Err.Description
    Debug.Print Msg

    validate_session = False
End Function

Private Sub close_session()

    If validate_session Then
        path_s = url_path(session_id, func)
        call_get = send("DELETE", url)
        Application.StatusBar = ""
    End If

End Sub


' *** url helpers ***

Private Function url_path(Optional ByVal p1 As String, Optional ByVal p2 As String, Optional ByVal p3 As String, Optional ByVal p4 As String) As String
    url_path = ""
    If p1 <> "" Then url_path = url_path & p1
    If p2 <> "" Then url_path = url_path & "/" & p2
    If p3 <> "" Then url_path = url_path & "/" & p3
    If p4 <> "" Then url_path = url_path & "/" & p4
End Function


Private Function url_query(Optional ByVal p1 As String, Optional ByVal p2 As String, Optional ByVal p3 As String, Optional ByVal p4 As String) As String
    url_query = ""
    If p1 <> "" Then url_query = url_query & "?" & DEFAULTARG & "1=" & p1
    If p2 <> "" Then url_query = url_query & "&" & DEFAULTARG & "2=" & p2
    If p3 <> "" Then url_query = url_query & "&" & DEFAULTARG & "3=" & p3
    If p4 <> "" Then url_query = url_query & "&" & DEFAULTARG & "4=" & p4
End Function


' *** request handling ***

Private Function mac()

    mac = InStr(1, Application.OperatingSystem, "Macintosh") = 1

End Function


Private Function send(ByVal type_s As String, ByVal url As String, Optional ByVal path_s As String, Optional ByVal query_s As String) As Variant

    #If mac Then
        send = send_mac(type_s, url, path_s, query_s)
    #Else
        send = send_win(type_s, url, path_s, query_s)
    #End If
End Function


Private Function send_mac(ByVal type_s As String, ByVal url As String, Optional ByVal path_s As String, Optional ByVal query_s As String) As Variant
    If path_s <> "" Then url = url & "/" & path_s

    If type_s = "GET" Then
        If query_s <> "" Then url = url & query_s
        curl_s = "curl -s '" & url & "'"

    ElseIf type_s = "POST" Then
        curl_s = "curl -H 'Content-Type: application/json' -X POST -d '" & query_s & "' '" & url & "'"
        'curl_s = "curl -d """ & query_s & """ """ & url & """"

    ElseIf type_s = "DELETE" Then
        curl_s = "curl -X DELETE '" & url & "'"

    Else: Err.Raise vbObjectError + 110, , "Cannot handle HttpRequest " & type_s

    End If

    curl_s = Replace(curl_s, """", "\""")
    script_s = "do shell script "" " & curl_s & " "" "
    Debug.Print script_s
    send_mac = MacScript(script_s)
    Debug.Print send_mac

End Function


Private Function send_win(ByVal type_s As String, ByVal url As String, Optional ByVal path_s As String, Optional ByVal query_s As String) As Variant

    Dim WinHttpReq As New WinHttpRequest

    If path_s <> "" Then url = url & "/" & path_s

    If type_s = "GET" Then
        If query_s <> "" Then url = url & query_s
        Debug.Print "WinHttpRequest.Open ""GET"", " & url & ", False"
        WinHttpReq.Open "GET", url, False

    ElseIf type_s = "POST" Then
        Debug.Print "WinHttpRequest.Open ""POST"", " & url & ", False"
        WinHttpReq.Open "POST", url, False

    ElseIf type_s = "DELETE" Then
        Debug.Print "WinHttpRequest.Open ""DELETE"", " & url & ", False"
        WinHttpReq.Open "DELETE", url, False

    Else: Err.Raise vbObjectError + 110, , "Cannot handle HttpRequest " & type_s

    End If

    Debug.Print "WinHttpRequest.send"

    WinHttpReq.send "" + query_s
    send_win = WinHttpReq.ResponseText
    Debug.Print send_win

End Function


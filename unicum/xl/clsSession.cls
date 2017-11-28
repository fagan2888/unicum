VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "clsSession"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False

'**************************************************************************************************
'***                                                                                            ***
'***                                   public members                                           ***
'***                                                                                            ***
'**************************************************************************************************


'**************************************************************************************************
'***                                                                                            ***
'***                                   private members                                          ***
'***                                                                                            ***
'**************************************************************************************************


Private Const LOCALHOST = "http://127.0.0.1:2699"
Private Const DEFAULTARG = "arg"

Private url As String
Private user As String
Private password As String
Private session_id As String


'**************************************************************************************************
'***                                                                                            ***
'***                                   public methods                                           ***
'***                                                                                            ***
'**************************************************************************************************

Public Sub init_session(ByVal url_s As String, Optional ByVal usr_s As String, Optional ByVal pwd_s As String)

    url = url_s
    user = usr_s
    password = pwd_s
    
    validate_session

End Sub


Function call_session_get(Optional ByVal func As String, Optional ByVal p1 As Variant, Optional ByVal p2 As String, Optional ByVal p3 As String, Optional ByVal p4 As String) As Variant
    Dim path_s As String
    Dim query_s As String
    
    validate_session
    path_s = url_path(session_id, func)
    query_s = url_query(p1, p2, p3, p4)
    call_session_get = send("GET", url, path_s, query_s)
    
End Function


Function call_session_post(Optional ByVal func As String, Optional ByVal content_s As String) As Variant
    
    validate_session
    path_s = url_path(session_id, func)
    call_session_post = send("POST", url, path_s, content_s)
    
End Function


Function call_session_delete(Optional ByVal func As String) As Variant
    
    validate_session
    path_s = url_path(session_id, func)
    call_session_delete = send("DELETE", url, path_s)
    
End Function



'**************************************************************************************************
'***                                                                                            ***
'***                                   private methods                                          ***
'***                                                                                            ***
'**************************************************************************************************


' *** session handling ***

Private Sub open_session()
        
        If url = "" Then url = LOCALHOST
        session_id = send("GET", url)
        Application.StatusBar = "Connected to " & url & "/" & session_id
       
End Sub


Private Sub validate_session()
        
        If url = "" Then url = LOCALHOST
        If session_id <> "" Then
            If send("GET", url, session_id) <> "true" Then open_session
        Else
            open_session
        End If

End Sub

Private Sub close_session()

    validate_session
    path_s = url_path(session_id, func)
    call_get = sen("DELETE", url)
    Application.StatusBar = ""

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
    WinHttpReq.send
    send_win = WinHttpReq.ResponseText
    Debug.Print send_win
    
End Function


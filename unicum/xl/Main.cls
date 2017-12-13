VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Main"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True

Private Sub Worksheet_BeforeDoubleClick(ByVal Target As Range, Cancel As Boolean)

    controls.DoubleClick Target, Cancel

End Sub

Private Sub Worksheet_Change(ByVal Target As Range)
    session_id = session.get_id()
    helpers.setSetup "SessionId", session_id
    If session_id <> "" Then
        fullpath = helpers.getSetup("URL") & "/" & session_id
        Application.StatusBar = "Connected to " & fullpath
    Else
        Application.StatusBar = ""
    End If
End Sub

Private Sub Worksheet_SelectionChange(ByVal Target As Range)

    handlers.showShape "Logo"

End Sub


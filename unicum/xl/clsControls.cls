VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "clsControls"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False


Private Function getShape(ByVal nameStr As String) As Shape

    For Each Shape In ActiveSheet.Shapes
        If Shape.Name = nameStr Then
            Set getShape = Shape
        End If
    Next

End Function


Private Sub showShape(ByVal nameStr As String)

    For Each Shape In ActiveSheet.Shapes
        If Shape.Name = nameStr Then
            Shape.Visible = True
        Else
            Shape.Visible = False
        End If
    Next

End Sub





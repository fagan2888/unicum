Attribute VB_Name = "controls"
Option Explicit

Sub ShortcutPasteValue()
' Keyboard Shortcut: Ctrl+w
On Error Resume Next
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks:=False, Transpose:=False
End Sub

Sub ShortcutPasteValueTranspose()
' Keyboard Shortcut: Ctrl+t
On Error Resume Next
    Selection.PasteSpecial Paste:=xlPasteValues, Operation:=xlNone, SkipBlanks:=False, Transpose:=True
End Sub

Sub ShortcutExtractSheet()
' Keyboard Shortcut: Strg+m
    ActiveSheet.Move
End Sub

Sub ClickLogo()
    handlers.showShape Array("RedButton", "LightButton", "YellowButton", "GreyButton", "DarkButton")
End Sub

Sub ClickRed()
    handlers.showShape "Logo"
    handlers.loadObjectFromFile
End Sub

Sub ClickLight()
    handlers.showShape "Logo"
    handlers.writeObjectToSheet
End Sub

Sub ClickYellow()
    handlers.showShape "Logo"
    handlers.loadObjectFromSheet
End Sub

Sub ClickGrey()
    handlers.showShape "Logo"
    handlers.writeObjectToFile
End Sub

Sub ClickDark()
    handlers.showShape "Logo"
    helpers.StartUp
End Sub

Sub ClickCache()
    handlers.showShape "Logo"
    handlers.getSelectionFromShape
End Sub

Sub DoubleClick(ByVal Target As Range, Cancel As Boolean)
    Dim sel As Variant
    For Each sel In Target
        On Error Resume Next
        handlers.writeObjectToSheet sel.Value
    Next
End Sub


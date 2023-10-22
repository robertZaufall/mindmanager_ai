VERSION 1.0 CLASS
BEGIN
  MultiUse = -1 'True
END
Attribute VB_PredeclaredId = False
Attribute VB_Creatable = True
Attribute VB_Exposed = False
Attribute VB_GlobalNameSpace = False
Attribute VB_Name = "Mermaid"
'#Language "WWB-COM"

Option Explicit

Const swUseRound As Boolean = 0
Const swUseRoot As Boolean = 1
Const LineSeparator As String = vbCr

Public Function GetDocumentAsMermaid(doc As Document) As String
    Dim centralTopic As Topic
    Set centralTopic = doc.CentralTopic

    Dim mermaidDiagram As String
    mermaidDiagram = "mindmap" + LineSeparator + _
  	    "  " + IIf(swUseRoot And swUseRound, "root", "") + IIf(swUseRound, "(", "") + centralTopic.Text + IIf(swUseRound, ")", "") + LineSeparator

    RecurseTopics mermaidDiagram, centralTopic, 1

    Return mermaidDiagram
End Function

Private Sub RecurseTopics(mermaidDiagram As String, ThisTopic As Topic, level As Integer)
    If level > 1 Then
        mermaidDiagram = mermaidDiagram + _
    	    String(level * 2, " ") + _
    	    IIf(swUseRound, "(", "") + ThisTopic.Text + IIf(swUseRound, ")", "") + LineSeparator
    End If

    Dim childTopics As Topics
    Set childTopics = ThisTopic.AllSubTopics

    Dim childTopic As Topic
    For Each childTopic In childTopics
        RecurseTopics mermaidDiagram, childTopic, level + 1
    Next
End Sub

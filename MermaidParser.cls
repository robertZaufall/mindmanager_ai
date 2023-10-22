VERSION 1.0 CLASS
BEGIN
  MultiUse = -1 'True
END
Attribute VB_PredeclaredId = False
Attribute VB_Creatable = True
Attribute VB_Exposed = False
Attribute VB_GlobalNameSpace = False
Attribute VB_Name = "MermaidParser"
'#Language "WWB-COM"
'#Uses "MermaidTopic.cls"

Option Explicit

Const delimiter As String = vbCr
Const indentSize As Integer = 2
Const swDebug As Boolean = vbFalse

Public Function ParseMermaid(mermaidSyntax As String) As MermaidTopic()
	Dim MermaidTopics() As MermaidTopic
	Dim newIndex As Integer
	newIndex = -1

    Dim mermaidLinesArray() As String
    mermaidLinesArray = Split(mermaidSyntax, delimiter)

	If UBound(mermaidLinesArray) > 1 Then
	    Dim mermaidLine As String

	    Dim i As Integer
	    For i = 1 To UBound(mermaidLinesArray)
	    	mermaidLine = mermaidLinesArray(i)
	        If mermaidLine <> "" Then
	        	Dim IndentLevel As Integer
	        	IndentLevel = (Len(mermaidLine) - Len(LTrim(mermaidLine))) / 2
				newIndex = newIndex + 1
				ReDim Preserve MermaidTopics(newIndex + 1)
				Set MermaidTopics(newIndex) = New MermaidTopic
				MermaidTopics(newIndex).TopicText = Trim(mermaidLine)
				MermaidTopics(newIndex).TopicLevel = IndentLevel - 1
	        End If
	    Next
	End If

	Return MermaidTopics
End Function

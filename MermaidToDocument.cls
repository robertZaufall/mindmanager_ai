VERSION 1.0 CLASS
BEGIN
  MultiUse = -1 'True
END
Attribute VB_PredeclaredId = False
Attribute VB_Creatable = True
Attribute VB_Exposed = False
Attribute VB_GlobalNameSpace = False
Attribute VB_Name = "MermaidToDocument"
'#Language "WWB-COM"
'#Uses "MermaidParser.cls"
'#Uses "MermaidTopic.cls"

Option Explicit

Public Sub NewDocumentFromMermaid(NewMermaidText As String)
	Dim MermaidParser As New MermaidParser

	Dim doc As Document
	Set doc = ActiveDocument

	Dim MermaidTopics() As MermaidTopic
	MermaidTopics = MermaidParser.ParseMermaid(NewMermaidText)

	Dim MermaidDoc As Document
	Dim LastTopic As Topic
	Dim ParentTopic As Topic

	Set MermaidDoc = AllDocuments.Add(True)
	Set ParentTopic = MermaidDoc.CentralTopic
	ParentTopic.Text = MermaidTopics(0).TopicText

	Dim i As Integer
	i = CreateSubTopics(MermaidTopics, 1, ParentTopic)
End Sub

Function CreateSubTopics(ByRef MermaidTopics() As MermaidTopic, index As Integer, ParentTopic As Topic) As Integer
	Dim i As Integer
	i = index
	Dim LastTopic As Topic

	While i <= UBound(MermaidTopics) - 1
		Dim mTopic As MermaidTopic
		Dim TopicLevel As Integer
		Dim TopicText As String

		Set mTopic = MermaidTopics(i)
		TopicLevel = mTopic.TopicLevel
		TopicText = mTopic.TopicText

		If TopicLevel <= ParentTopic.Level Then
			Return i
		End If

		Dim NewTopic As Topic
		If TopicLevel = ParentTopic.Level + 1 Then
			Set NewTopic = ParentTopic.AddSubTopic(TopicText)
			Set LastTopic = NewTopic
		End If

		If TopicLevel > ParentTopic.Level + 1 Then
			i = CreateSubTopics(MermaidTopics, i, LastTopic) - 1
		End If

		i += 1
	Wend
End Function

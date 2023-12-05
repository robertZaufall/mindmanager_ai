VERSION 1.0 CLASS
BEGIN
  MultiUse = -1 'True
END
Attribute VB_PredeclaredId = False
Attribute VB_Creatable = True
Attribute VB_Exposed = False
Attribute VB_GlobalNameSpace = False
Attribute VB_Name = "JSONParser"
'#Language "WWB-COM"

Option Explicit

Public Function ParseTopicsFromJSON(JSON As String, cloudType As String) As String
    Dim findStr As String
    Dim contentStart As Integer, contentEnd As Integer
    Dim contentString As String
    Dim Topics() As String

    'JSON = Replace(JSON, "\n", "")
    JSON = Replace(JSON, "\'", "")
    JSON = Replace(JSON, "\""", "")
    JSON = Replace(JSON, "\u0026", "&")
    JSON = Replace(JSON, "'", "")

    If cloudType = "OPENAI" Then
        findStr = """content"": """
    Else ' AZURE
        findStr = """content"":"""
    End If
    contentStart = InStr(1, JSON, findStr)
    contentEnd = InStr(contentStart + Len(findStr), JSON, """")
    contentString = Mid(JSON, contentStart + Len(findStr), contentEnd - contentStart - Len(findStr))

    contentString = Replace(contentString, "```mermaid\n", "")

    Return contentString
End Function

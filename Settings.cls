VERSION 1.0 CLASS
BEGIN
  MultiUse = -1 'True
END
Attribute VB_PredeclaredId = False
Attribute VB_Creatable = True
Attribute VB_Exposed = False
Attribute VB_GlobalNameSpace = False
Attribute VB_Name = "Settings"
'#Language "WWB-COM"

Option Explicit

Const CLOUD_TYPE = "AZURE" ' ["AZURE","OPENAI"]
Const OPENAI_MODEL As String = "gpt-4" ' only relevant for OPENAI

Const MAX_TOKENS As Integer = 100
Const TOP_MOST_RESULTS As Integer = 3
Const MAX_RETURN_WORDS As Integer = 5

Public MaxTokens As String
Public CloudType As String
Public ApiUrl As String
Public KeyHeaderText As String
Public KeyHeaderValue As String
Public OpenAIModel As String
Public TopMostResults As String
Public MaxReturnWords As String

Private Sub Class_Initialize
	Dim OPENAI_API_KEY As String
	Dim OPENAI_API_BASE As String
	Dim OPENAI_DEPLOYMENT As String
	Dim OPENAI_API_VERSION As String

	CloudType = CLOUD_TYPE
	MaxTokens = CStr(MAX_TOKENS)
	TopMostResults = CStr(TOP_MOST_RESULTS)
	MaxReturnWords = CStr(MAX_RETURN_WORDS)

	If CloudType = "OPENAI" Then
		'''
		OPENAI_API_KEY = Environ("OPENAI_API_KEY_NATIVE")
		'''
	    ApiUrl = "https://api.openai.com/v1/chat/completions"
		OpenAIModel = OPENAI_MODEL
	    KeyHeaderText = "Authorization"
	    KeyHeaderValue = "Bearer " & OPENAI_API_KEY
	Else
		'''
		OPENAI_API_KEY = Environ("OPENAI_API_KEY")
		OPENAI_API_BASE = Environ("OPENAI_API_BASE")
		OPENAI_DEPLOYMENT = Environ("OPENAI_DEPLOYMENT")
		OPENAI_API_VERSION = Environ("OPENAI_API_VERSION")
		'''
	    ApiUrl = OPENAI_API_BASE + "openai/deployments/" + OPENAI_DEPLOYMENT + "/chat/completions?api-version=" + OPENAI_API_VERSION
	    KeyHeaderText = "api-key"
	    KeyHeaderValue = OPENAI_API_KEY
	End If
End Sub

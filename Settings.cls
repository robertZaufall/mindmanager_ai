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

Const DEBUG_FLAG = False

'**********************************************************
Const CLOUD_TYPE         As String = "AZURE" ' ["AZURE","OPENAI"]
Const OPENAI_MODEL       As String = "gpt-4" ' only relevant for OPENAI
Const OPENAI_TEMPERATURE As String = "0.3"
'**********************************************************

Const MAX_TOKENS_SIMPLE     As Integer = 100 ' single topic
Const MAX_TOKENS_NORMAL     As Integer = 1000 ' generate tasks or examples
Const MAX_TOKENS_DEEP       As Integer = 4000 ' refinement
Const TOP_MOST_RESULTS      As Integer = 3 ' tasks or examples
Const TOP_MOST_RESULTS_DEEP As Integer = 6 ' refinement
Const MAX_RETURN_WORDS      As Integer = 5 ' per topic text
Const LEVELS_DEEP           As Integer = 5 ' refinement

' http request
Const RESOLVE_TIMEOUT       As Long = 60000
Const CONNECT_TIMEOUT       As Long = 60000
Const SEND_TIMEOUT          As Long = 60000
Const RECEIVE_TIMEOUT       As Long = 60000

Public SwDebug As Boolean
Public CloudType As String
Public Temperature As String

Public MaxTokens As String
Public MaxTokensSimple As String
Public MaxTokensNormal As String
Public MaxTokensDeep As String
Public TopMostResults As String
Public TopMostResultsDeep As String
Public MaxReturnWords As String
Public LevelsDeep As String

Public ResolveTimeout As Long
Public ConnectTimeout As Long
Public SendTimeout As Long
Public ReceiveTimeout As Long

Public ApiUrl As String
Public KeyHeaderText As String
Public KeyHeaderValue As String
Public OpenAIModel As String

Private Sub Class_Initialize
	Dim OPENAI_API_KEY As String
	Dim OPENAI_API_BASE As String
	Dim OPENAI_DEPLOYMENT As String
	Dim OPENAI_API_VERSION As String

	SwDebug = DEBUG_FLAG
	CloudType = CLOUD_TYPE
	Temperature = OPENAI_TEMPERATURE

	MaxTokens = CStr(MAX_TOKENS_SIMPLE)
	MaxTokensSimple = CStr(MAX_TOKENS_SIMPLE)
	MaxTokensNormal = CStr(MAX_TOKENS_NORMAL)
	MaxTokensDeep = CStr(MAX_TOKENS_DEEP)
	TopMostResults = CStr(TOP_MOST_RESULTS)
	TopMostResultsDeep = CStr(TOP_MOST_RESULTS_DEEP)
	MaxReturnWords = CStr(MAX_RETURN_WORDS)
	LevelsDeep = CStr(LEVELS_DEEP)

	ResolveTimeout = RESOLVE_TIMEOUT
	ConnectTimeout = CONNECT_TIMEOUT
	SendTimeout = SEND_TIMEOUT
	ReceiveTimeout = RECEIVE_TIMEOUT

	If CloudType = "OPENAI" Then
		' OpenAI
        '**********************************************************
		OPENAI_API_KEY     = Environ("OPENAI_API_KEY_NATIVE")
        '**********************************************************
	    ApiUrl = "https://api.openai.com/v1/chat/completions"
		OpenAIModel = OPENAI_MODEL
	    KeyHeaderText = "Authorization"
	    KeyHeaderValue = "Bearer " & OPENAI_API_KEY
	Else
		' Azure
        '**********************************************************
		OPENAI_API_KEY     = Environ("OPENAI_API_KEY")
		OPENAI_API_BASE    = Environ("OPENAI_API_BASE")
		OPENAI_DEPLOYMENT  = Environ("OPENAI_DEPLOYMENT")
		OPENAI_API_VERSION = Environ("OPENAI_API_VERSION")
        '**********************************************************
	    ApiUrl = OPENAI_API_BASE + "openai/deployments/" + OPENAI_DEPLOYMENT + "/chat/completions?api-version=" + OPENAI_API_VERSION
	    KeyHeaderText = "api-key"
	    KeyHeaderValue = OPENAI_API_KEY
	End If
End Sub

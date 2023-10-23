VERSION 1.0 CLASS
BEGIN
  MultiUse = -1 'True
END
Attribute VB_PredeclaredId = False
Attribute VB_Creatable = True
Attribute VB_Exposed = False
Attribute VB_GlobalNameSpace = False
Attribute VB_Name = "GptRequest"
'#Language "WWB-COM"
'#Uses "Settings.cls"
'#Uses "JSONParser.cls"

Option Explicit

Public Function Gpt4Request(Settings As Settings, strSystem As String, strUser As String) As String
    Dim strPayload As String
    Dim Request As Object
    Dim responseText As String
    Dim result As String

    strPayload = "{" + _
        IIf (Settings.CloudType = "OPENAI", _
        """model"": """ + Settings.OpenAIModel + """, ", "") + _
        """max_tokens"": " + Settings.MaxTokens +", " + _
        """temperature"": " + Settings.Temperature +", " + _
        """messages"": [" + _
            "{""role"": ""system"", ""content"": """ + strSystem + """}, " + _
            "{""role"": ""user"", ""content"": """ + strUser + """ " + _
        "}]" + _
    "}"
    If Settings.SwDebug = True Then MsgBox(strPayload)

    Set Request = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    Request.Open "POST", Settings.ApiUrl, False
    Request.setRequestHeader "Content-Type", "application/json"
    Request.setRequestHeader Settings.KeyHeaderText, Settings.KeyHeaderValue
    Request.SetTimeouts Settings.ResolveTimeout, Settings.ConnectTimeout, Settings.SendTimeout, Settings.ReceiveTimeout
    Request.send strPayload
    responseText = Request.responseText

    If Settings.SwDebug = True Then MsgBox(responseText)

    Dim parser As New JSONParser
    result = parser.ParseTopicsFromJSON(responseText, Settings.CloudType)

    If Settings.SwDebug = True Then MsgBox(result)

    Return result
End Function

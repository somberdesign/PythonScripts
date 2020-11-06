Option Explicit

Dim sound : sound = "160483__koyber__casio-f-91w-hour-chime.wav"

Dim o : Set o = CreateObject("wmplayer.ocx")
With o
 .url = sound
 .controls.play
 While .playstate <> 1
 wscript.sleep 100
 Wend
 .close
End With

Set o = Nothing

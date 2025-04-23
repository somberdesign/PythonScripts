Option Explicit


' INSTALLATION:
' 
' Copy this file to "C:\Program Files (x86)\MediaMonkey\Scripts\CleanTags.vbs"
' 
' Open Scripts.ini (in the same dir) and add the following entry:
' 
' [CleanTags]
' FileName=CleanTags.vbs
' ProcName=RemoveUnderscores
' Order=15
' DisplayName=Remove Underscores...
' Description=Remove Underscores from Title
' Language=VBScript
' ScriptType=0
' 
' Restart MM and you will see "Remove Underscores..." in Tools / Scripts


Sub AddUnderscores
	ModifyUnderscores false
End Sub

Sub RemoveUnderscores
	ModifyUnderscores true
End Sub

Sub UnderscoreToComma
	ReplaceChar "_", ", "
End Sub


''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
' added 2020-09-07 - visiting dad during Conona
' NOT tested.
Sub ReplaceChar(find, replace)
 
 	Dim i, j, itm, char, newTitle, newArtist, newActors
	Dim selectedItems : Set selectedItems = SDB.CurrentSongList 

	' loop over each selected item
	For i = 0 to selectedItems.Count - 1
		Set itm = selectedItems.Item(i)
		
		' loop over each character in the Title
		newTitle = ""
		For j = 1 to Len(itm.Title)
			If Mid(itm.Title, j, 1) = find Then
				newTitle = newTitle + replace

			Else
				newTitle = newTitle + Mid(itm.Title, j, 1)

			End If
		Next
		itm.Title = newTitle

		' loop over each character in the Artist
		newArtist = ""
		For j = 1 to Len(itm.ArtistName)
			If Mid(itm.ArtistName, j, 1) = find Then
				newArtist = newArtist + Replace

			Else
				newArtist = newArtist + Mid(itm.Title, j, 1)

			End If
		Next
		itm.ArtistName = newArtist

	Next

	selectedItems.UpdateAll



End Sub

Sub ModifyUnderscores(remove)
 
 	Dim i, j, itm, char, newTitle, newArtist, newActors
	Dim selectedItems : Set selectedItems = SDB.CurrentSongList 
	
	Dim showDebugBox : showDebugBox = False
	Dim debugText : debugText = ""

' loop over each selected item
For i = 0 to selectedItems.Count - 1
Set itm = selectedItems.Item(i)

		' 2023-12-30 process item only if it contains underscores and is long enough
		If InStr(itm.Title, "_") > 0 Then
			' loop over each character in the Title
			newTitle = ""
			For j = 1 to Len(itm.Title)
				If remove = True And Mid(itm.Title, j, 1) = "_" Then
					newTitle = newTitle + " "

				ElseIf remove = False And Mid(itm.Title, j, 1) = " " Then
					newTitle = newTitle + "_"

				Else
					newTitle = newTitle + Mid(itm.Title, j, 1)

				End If
			Next

			' 2023-01-31 remove year at end of title
			If Len(newTitle) <= 5 Then
				newTitle = newTitle
			ElseIf Mid(newTitle, Len(newTitle) - 4, 1) = " " And IsNumeric(Mid(newTitle, Len(newTitle) - 3, 4)) Then
				newTitle = Mid(newTitle, 1, Len(newTitle) - 5)
			End If

			If showDebugBox = True Then
				debugText = debugText + "newTitle = " + newTitle + vbCrLf
				debugText = debugText + "Mid(newTitle, Len(newTitle) - 7, 5) = " + Mid(newTitle, Len(newTitle) - 7, 5) + vbCrLf
			End If

			' replace " SCREENER"
			Dim START_POSITION : START_POSITION = 1
			Dim REPLACEMENT_COUNT : REPLACEMENT_COUNT = -1 ' replace all
			Dim COMPARE_TYPE_TEXT : COMPARE_TYPE_TEXT = 0 ' 0 is Binary, 1 is text
			newTitle = Replace(newTitle, " SCREENER", "", START_POSITION, REPLACEMENT_COUNT, COMPARE_TYPE_TEXT)


			' 2023-04-04 put a colon before "Part x"
			If Len(newTitle) <= 7 Then
				newTitle = newTitle
			ElseIf Mid(newTitle, Len(newTitle) - 7, 5) = " Part" Then
				newTitle = Left(newTitle, Len(newTitle) - 7) + ":" + Mid(newTitle, Len(newTitle) - 7)
			End If

			itm.Title = newTitle



			' loop over each character in the Artist
			newArtist = ""
			For j = 1 to Len(itm.ArtistName)
				If remove = True And Mid(itm.ArtistName, j, 1) = "_" Then
					newArtist = newArtist + " "

				ElseIf remove = False And Mid(itm.ArtistName, j, 1) = " " Then
					newArtist = newArtist + "_"

				Else
					newArtist = newArtist + Mid(itm.ArtistName, j, 1)

				End If
			Next
			itm.ArtistName = newArtist

			' 2016-05-22 - can't find what the item property is for the Actor field
			' it's not Actor, ActorName or Actornames.

		End If

	Next

	selectedItems.UpdateAll

	If showDebugBox = True Then
		MsgBox(debugText)
	End If


End Sub

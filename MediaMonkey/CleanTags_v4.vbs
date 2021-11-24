Option Explicit

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
 
Dim i, j, itm, char, newTitle, newArtist, newActors, last4
Dim selectedItems : Set selectedItems = SDB.CurrentSongList 

' loop over each selected item
For i = 0 to selectedItems.Count - 1
Set itm = selectedItems.Item(i)

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

' strip year
If Len(newTitle) > 5 Then
	last4 = Mid(newTitle, Len(newTitle)-3, Len(newTitle))
	If IsNumeric(last4) Then
		newTitle = Mid(newTitle, 1, Len(newTitle)-4)
	End If
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

Next

selectedItems.UpdateAll



End Sub

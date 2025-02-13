from os import open


inList = ["A Song of Ice & Fire", "Action on the High Seas", "Battlesystem", "BattleTech", "Boot Hill", "Braunstein", "Burrows and Badgers", "Car Wars", "Chainmail", "Check Your 6", "Classic Warfare", "Clay-O-Rama", "Don't Give Up the Ship!", "Dragon Rampant: Fantasy Wargaming Rules", "Dungeon!", "Fast Rules", "Full Thrust", "Game System", "Gaslands", "General Quarters", "HeroClix", "Legions of the Petal Throne", "Little Wars", "Marvel Battleworld", "Panzers vs. Dragons", "Pulp Alley", "Rebels and Patriots", "Redcoats in the Wilderness", "Remagen Bridgehead", "ROCKETSHIPS Exclamation Point!", "Siege of Bodenburg", "Space Hulk", "Strategos N", "Sturmgeschutz & Sorcery", "Tractics"]
output = ""

counter = 1
for i in inList:
    output += i + "\t\t\t"
    if counter % 3 == 0: output += "\n"
    counter += 1

print(output)
# with open('ListToColumns.txt', 'w') as f:
#     f.writelines(output)


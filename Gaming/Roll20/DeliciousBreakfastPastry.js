on ('chat:message', function(msg) {

    if (msg.type == 'api' && msg.content.toLowerCase().indexOf('!deliciouspastry') != -1) {
			var buffs = [
				{ description: '+2 to Dexterity-based skill checks', weight: 1 },
				{ description: '+2 to Acrobatics skill checks', weight: 1 },
				{ description: '+2 to Sleight skill checks', weight: 1 },
				{ description: '+2 to Stealth skill checks', weight: 1 },
				{ description: '+2 to Intelligence-based skill checks', weight: 1 },
				{ description: '+2 to Arcana skill checks', weight: 1 },
				{ description: '+2 to History skill checks', weight: 1 },
				{ description: '+2 to Investigation skill checks', weight: 1 },
				{ description: '+2 to Nature skill checks', weight: 1 },
				{ description: '+2 to Religion skill checks', weight: 1 },
				{ description: '+2 to Wisdom-based skill checks', weight: 1 },
				{ description: '+2 to Animal skill checks', weight: 1 },
				{ description: '+2 to Insight skill checks', weight: 1 },
				{ description: '+2 to Medicine skill checks', weight: 1 },
				{ description: '+2 to Perception skill checks', weight: 1 },
				{ description: '+2 to Survival skill checks', weight: 1 },
				{ description: '+2 to Charisma-based skill checks', weight: 1 },
				{ description: '+2 to Deception skill checks', weight: 1 },
				{ description: '+2 to Intimidation skill checks', weight: 1 },
				{ description: '+2 to Performance skill checks', weight: 1 },
				{ description: '+2 to Persuasion skill checks', weight: 1 },
				{ description: '+2 Strength', weight: 1 },
				{ description: '+2 Dexterity', weight: 1 },
				{ description: '+2 Constitution', weight: 1 },
				{ description: '+2 Intelligence', weight: 1 },
				{ description: '+2 Wisdom', weight: 1 },
				{ description: '+2 Charisma', weight: 1 },
				{ description: 'Advantage on Charisma ability checks', weight: 1 },
				{ description: 'Advantage on Constitution ability checks', weight: 1 },
				{ description: 'Advantage on Dexterity ability checks', weight: 1 },
				{ description: 'Advantage on Intelligence ability checks', weight: 1 },
				{ description: 'Advantage on Strength ability checks', weight: 1 },
				{ description: 'Advantage on Wisdom ability checks', weight: 1 },
				{ description: 'Advantage on Charisma saves', weight: 1 },
				{ description: 'Advantage on Constitution saves', weight: 1 },
				{ description: 'Advantage on Dexterity saves', weight: 1 },
				{ description: 'Advantage on Intelligence saves', weight: 1 },
				{ description: 'Advantage on Strength saves', weight: 1 },
				{ description: 'Advantage on Wisdom saves', weight: 1 },
				{ description: 'Resistant to Acid damage', weight: 1 },
				{ description: 'Resistant to Bludgeoning damage', weight: 1 },
				{ description: 'Resistant to Cold damage', weight: 1 },
				{ description: 'Resistant to Fire damage', weight: 1 },
				{ description: 'Resistant to Force damage', weight: 1 },
				{ description: 'Resistant to Lightning damage', weight: 1 },
				{ description: 'Resistant to Necrotic damage', weight: 1 },
				{ description: 'Resistant to Piercing damage', weight: 1 },
				{ description: 'Resistant to Poison damage', weight: 1 },
				{ description: 'Resistant to Psychic damage', weight: 1 },
				{ description: 'Resistant to Radiant damage', weight: 1 },
				{ description: 'Resistant to Slashing damage', weight: 1 },
				{ description: 'Resistant to Thunder damage', weight: 1 },
				{ description: '+20% Movement', weight: 1 },
				{ description: '+20% Bludgeoning damage', weight: 1 },
				{ description: '+20% Cold damage', weight: 1 },
				{ description: '+20% Fire damage', weight: 1 },
				{ description: '+20% Force damage', weight: 1 },
				{ description: '+20% Lightning damage', weight: 1 },
				{ description: '+20% Necrotic damage', weight: 1 },
				{ description: '+20% Piercing damage', weight: 1 },
				{ description: '+20% Poison damage', weight: 1 },
				{ description: '+20% Psychic damage', weight: 1 },
				{ description: '+20% Radiant damage', weight: 1 },
				{ description: '+20% Slashing damage', weight: 1 },
				{ description: '+20% Thunder damage', weight: 1 },
				{ description: '+20% Max Hit Points', weight: 1 },
				{ description: '+2 Armor Class', weight: 1 },
				{ description: 'You feel very full and satisfied', weight: 10 }
				
			  ],
			  sumOfWeights = buffs.reduce(function(memo, buff) {
				return memo + buff.weight;
			  }, 0)//,
			  //selectedWeights = {};

			function getRandom(sumOfWeights) {
			  var random = Math.floor(Math.random() * (sumOfWeights + 1));

			  return function(buff) {
				random -= buff.weight;
				return random <= 0;
			  };
			}

			var buff = buffs.find(getRandom(sumOfWeights));
			var returnVal = 'Delicous Breakfast Pastry: ' + buff.description;
			sendChat(msg.who, returnVal);
    }
});
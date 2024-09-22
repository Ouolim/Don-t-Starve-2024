# Don't Starve 2024
Summer semester project for programming class at MFFUK
Also toolbox and frontend for game at local scout camp

# Uživatelská dokumentace
Aplikace přichází v několika částech. 

## Hlavní okno
Bydlí v souboru main.py, po spuštění zobrazuje UI které se ukazovalo dětem při hře.
Po připojení čtečky čárových kódů se do horní části automaticky vpisuje to co čtečka vrací.
V prostřední části se ukazuje aktuální recept, ve spodní části aktuální předměty v inventáři.

Po načtení kódu pro předmět se přidá odpovídající množství do inventáře. Při načtení receptu,
se ukážou ingredience pod šipkou. Na samotné vyrobení předmětu se používal kód pro vyrobení,
který byl dětem rozdán před táborem. Na vyrobení je potřeba se "přihlásit". Na to měl každý
hráč také svůj kód. 

## Recepty
Bydlí v ./recipeGenerator.py, vcelku jednoduchá aplikace. Do horní části se vyplní detaily o receptu 
- recipe Id - co se vyrábí
- amount - kolik se toho vyrábí
- restriction - omezení, kdo může recept vyrábět. Když zůstane prázdné tak ho může vyrábět kdo chce. Při vyplnění jediného čísla
označuje číslo role která recept může vyrábět (viz. ##Role)

Print recipes poté otevře weový prohlížeč ze kterého se dají kódy na recepty vytisknout. Recepty se přidávají dolů, kde se dají i mazat

## Kódy pro předměty
Aplikace bydlí v ./codeGenerator, vyrábí skupiny kódů (batches), které se dají vytisknout odděleně. Obrázky se dávají do
./batches/<číslo skupiny>. Do horní části se vyplní kolik jakého kódu chci a kolik chci aby na papírku bylo předmětů. 
Předměty se ze skupiny nedají mazat, při chybě se vyrobí nová skupina.

# Technická dokumentace

Aplikace si všechno ukádá v SQL3 databázi v ./data/database.db. V ní jsou uložené kódy předmětů, použité kódy, recepty 
a aktuální hráčský inventář. S databází je vždy komunikováno skrz ./databaseCommands.py. 

## Recepty a kódy na předměty
Všechny recepty a předmětové kódy které se vyrobí a pošlou do databáze, mají k sobě i odpovídající svg obrázek, který
se vytiskne. Výrobu kódu zastává knihovna barcode (https://pypi.org/project/python-barcode/) a konkrétně to jsou kódy
128 (https://en.wikipedia.org/wiki/Code_128). Receptové kódy se ukládají do ./recepies a kódy bydlí v ./batches. Dají se 
vytisknout pomocí tlačítek v jejich aplikacích, které pouští funkci printBuild v codeGenerator.py. 

Nejdříve je potřeba vyplnit proměnné v ./data/gameConstants.py, ve které jsou kódy hráčů a kódy a potvrzování výroby,
jejich obrázky byli vyrobeny předem a vytisknuty do deníčků co s s sebou na hrách nosili. Seznam předmětů je v ./data/items.py.
Ke každému obrázku je potřeba ikonka, které jsou uložené v ./icons.


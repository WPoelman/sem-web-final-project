# sem_web_final_project
Final project for the course Semantic Webtechnology

## Usage
1. Run `pip install -r requirements.txt`
   1. If you get a `curl` related error on Debian based systems, try installing the following:
    `sudo apt install libcurl4-openssl-dev libssl-dev`
2. run ...

## TODO
- Mappings leren / opslaan van de training data die we hebben
  - Welke keys hebben dezelfde values?
  - Formats EN-NL omzetten en kijken of ze zo hetzelfde zijn (dates, formal names etc)
  - Kijken naar datatype en kijken of die mogelijk overeen komen met een marge? (datetime, page numbers etc.)
- Het live ophalen van een titel en daar de NL en/of EN infobox van parsen
- Maken van nieuwe of aangevulde infoboxes
  - Gevonden mappings toepassen (ook vertaling van keys die we weten)
  - Evt. keys vertalen als we 'weten' dat iets ontbreekt, maar we er geen vooraf gegenereerde mapping voor hebben
  - Output naar file met een soort van report van de toegepaste mappings en wat we gemist hebben of niet weten
- (Later) handmatige menselijke annotatie van output
- (Later) evaluatie van infoboxes die ongeveer 1 op 1 overeenkomen, als gold set behandelen, kan eventueel ook op key niveau voor bepaalde mappings die al overeen komen (gaat de vertaling van deze key goed etc.)
- (Later) ook kijken of er Nederlandse artikelen zijn waar wel een infobox voor is en voor het Engels niet (alleen nuttig voor het verslag, volledige statistieken voor het probleem)

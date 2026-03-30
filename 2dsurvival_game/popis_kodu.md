# Dokumentace a popis struktury kódu

Tento soubor obsahuje přehled všech použitých importů a hlavních tříd/funkcí ze souboru `2dsurvival_game.py` s jejich vysvětlením. Záměrně jsou vynechány drobné pomocné funkce uvnitř tříd, abychom se zaměřili na to nejdůležitější stavivo hry.

## Importy (Knihovny)

* **`pygame`**: Hlavní knihovna použitá pro tvorbu celé 2D hry. Stará se o vykreslování grafiky, zpracování vstupů z klávesnice/myši, vytváření okna aplikace a udržování herní smyčky (časování/FPS).
* **`random`**: Používá se pro generování náhodných čísel. Ve hře se hodí pro náhodné generování rozložení mapy (dungeonu), na výpočet šance spawnování nepřátel nebo i na rozptyl "teček" u textur bloků pro grafickou variabilitu.
* **`math`**: Obsahuje matematické funkce. Ve hře se používá primárně pro goniometrii - zjišťování přesné vzdálenosti mezi hráčem a nepřítelem (`math.hypot`), nebo k počítání úhlů na základě pozice myši (`math.atan2` a `math.degrees`) během útoku.
* **`sys`**: Modul systému, zde využit pro korektní spolehlivé ukončení celého programu zavoláním příkazu `sys.exit()` poté, co uživatel zvolí "Quit" nebo křížkem zavře okno.
* **`typing` (`TypedDict, List, Tuple, cast`)**: Slouží pro takzvaný "type hinting" (napovídání typů proměnných editoru a ostatním vývojářům), aby byl kód spolehlivější a čistší. Pomocí nich se lépe popisuje, z jakých proměnných se například skládá datový slovník místnosti.

## Hlavní třídy (Classes)

* **`Camera`**: Třída starající se o pohled na hru. Neustále sleduje hráče a aktualizuje svoji pozici. Zabudovaná je i takzvaná "deadzone", což znamená, že než se hráč pohne víc ke kraji obrazovky, pohled se neposouvá, což působí mnohem příjemněji na oči. Následně poskytuje výpočty umožňující vykreslit ostatní entity uvnitř daného pohledu.
* **`Block`**: Třída představující jeden nehybný dílek prostředí (např. hlína, kámen, tráva). Spravuje svou vlastní čtverečkovou texturu a hlídá logiku pro kolize stěn.
* **`Item`**: Třída reprezentující sebratelné předměty, zejména ty, které za sebou zanechají mrtví nepřátelé. Může to být zkušenostní orb (XP), lahvička dočasně posilující poškození nebo zdraví. Spravuje efekt, který tyto předměty aplikují na hráče (funkce `apply()`).
* **`Player`**: Masivní centrální třída ovládané postavy hráče. Stará se o příjem instrukcí z klávesnice/myši (pohyb a míření), posunutí sebe sama, spravování vlastních animací (změna obrázků), tvarů a dosahů útoků mečem, a eviduje vlastní statistiky včetně zdraví a systému nabírání levelu na základě XP.
* **`Enemy`**: Abstrahováná třída reprezentující jakéhokoliv nepřítele (např. normální "walker" zombík, nebezpečný pomalý obrněný golem, nebo létající netopýr ignorující část terénu). Udržuje chování dané umělé inteligence, tedy jakým algoritmem se blížím za hráčem. Spravuje odskočení (knockback) při zásahu, odebírá si životy a po vlastní smrti na svém místě zanechá příslušný Item popsaný výše.

## Hlavní herní funkce

* **`generate_dungeon(size)`**: Mechanismus definující "mapu". Volá se na úplném začátku, nebo jakmile začne nová hra po smrti. Náhodně skládá dohromady podklady obdélníkových místností oddělené tvrdými kamennými stěnami (`Block`), takže vymezí hrací plochu pro potulujícího se hráče i rodící se monstra, odkud nemohou za hranice propadnout "mimo mapu".
* **`main()`**: Ústřední herní smyčka (Game Loop) fungující stále dokola. Na začátku zprovozní světlo světa: vygeneruje mapu, oživí postavu a nastaví časovač vln nepřátel. Vzápětí donekonečna překresluje po sobě obrazovky. Stále aktualizuje pozice a stavy hráčů (`update()`), vytváří další skupiny nepřátel na kraji vzdálenosti kamery (pomocí propracované vlny spawnování) a vykresluje i uživatelské rozhraní. Kromě toho kontroluje detekci stisknutí nabídek odměn "Level Up!".
* **`main_menu()`**: Drobná úvodní funkce. Spustí se jako úplně první hned po spuštění programu a vykreslí na černou obrazovku do tmy "Survival Game" výběr. Slouží jako pasivní smyčka čekající, až kliknete Enter a zahájíte tak onu opravdovou hru (`main()`).

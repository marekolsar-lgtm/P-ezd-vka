# 2D Survival Game - Dokumentace

## Přehled hry

**2D Survival Game** je 2D akční survival hra vytvořená v Pythonu s využitím knihovny Pygame. Hra staví na populárním žánru "horde survival / roguelite" (podobně jako MegaBonk nebo Vampire Survivors). Hráč musí přežít vlny nepřátel, sbírat zkušenostní orby, vybírat si zbraně a pasivní tomy (tomes) a tvořit synergie, aby přežil co nejdéle.

## Hlavní mechaniky

### Pohyb a ovládání
- **Pohyb**: Použijte klávesy `WASD` nebo šipky pro pohyb ve všech směrech
- **Útok**: Všechny zbraně (včetně meče) útočí plně automaticky s vlastním cooldownem. Klávesnice se používá jen k pohybu, myš směřuje základní útok mečem.
- **Fullscreen**: Klávesa `F` pro přepínání mezi oknem a fullscreen režimem
- **Reroll (Přetočení nabídek)**: Klávesa `R` (nebo klik na tlačítko) na obrazovce povýšení
- **Ukončení**: `ESC` pro ukončení hry

### Hráč
- **Zdraví**: Začíná na 100 životech (lze trvale zvyšovat pomocí Vitality Tome)
- **Úroveň a XP**: Hráč sbírá zelené orby z nepřátel; po naplnění lišty XP získá novou úroveň a vyskočí menu s výběrem 3 karet.
- **Peníze**: Z nepřátel občas padají zlaté mince. Ty slouží jako měna pro Reroll (přetočení) nabídek karet při level-upu.
- **Knockback a Imunita**: Při zásahu nepřítelem je hráč mírně odhozen a na 30 snímků se stane nezranitelným (bliká červeně).

### Nepřátelé

Hra obsahuje pět typů nepřátel s různými vlastnostmi:

#### 1. Walker (Chodec) - Zelený Slime/Zombie
- **Zdraví**: 30 | **Poškození**: 15 | **XP**: 5
- **Chování**: Základní jednotka, pronásleduje hráče

#### 2. Flying (Létající) - Fialový Netopýr
- **Zdraví**: 20 | **Poškození**: 10 | **XP**: 5
- **Chování**: Pomaleji létá za hráčem, ignoruje složitější překážky

#### 3. Tank (Golem) - Šedý
- **Zdraví**: 100 | **Poškození**: 30 | **XP**: 15
- **Chování**: Pomalý, ale velice odolný nepřítel

#### 4. Fast (Duch) - Průhledný
- **Zdraví**: 10 | **Poškození**: 5 | **XP**: 5
- **Chování**: Extrémně rychlý s vysokým knockbackem

#### 5. Boss - Velký červený golem
- **Zdraví**: 500 (+200 za každou další vlnu) | **Poškození**: 40 (+10 za vlnu) | **XP**: 150
- **Chování**: Spawnuje se na konci každé vlny za okrajem obrazovky

## Roguelite Upgrade Systém (MegaBonk Styl)

Při startu hráč začíná pouze s mečem úrovně 1. Kdykoli nasbírá dostatek XP na nový level, hra se pozastaví a nabídne 3 náhodné možnosti povýšení generované pomocí rarit.

### Rarity systém
Karty padají s určitou pravděpodobností podle rarity (možnost vylepšit atributem **Luck**):
- **Common** (Šedá)
- **Uncommon** (Zelená)
- **Rare** (Modrá)
- **Epic** (Fialová)
- **Legendary** (Zlatá)
(Čím vyšší úroveň uprgadu, tím vzácnější je příslušná karta.)

### Zbraně (Weapons)
Zbraně zajišťují likvidaci nepřátel. Hráč může nést maximálně **4 různé zbraně** ve 4 slotech. Každou zbraň lze povýšit až na **Maximální Level (Lv. 5)**.
1. **Sword (Meč)**: Seká plošně před hráče. Vyšší úroveň zvyšuje damage, dosah a zrychluje frekvenci útoku. Ovlivněn směrem pohledu hráče/myši.
2. **Shuriken (Šuriken)**: Vystřeluje hvězdice rotující a procházející skrz nepřátele. Vyšší level zvyšuje počet šurikenů, poškození a rychlost.
3. **Fire Ring (Ohnivý kruh)**: Vytvoří pulzující zónu ohně okolo hráče. Ničí nepřátele v blízkém perimetru.
4. **Lightning (Blesk)**: Sesílá blesky z oblohy na nejbližší nepřátele, dokáže přeskočit na další cíle (chain lightning efekt na vyšších levelech).

### Tomy (Pasivní vylepšení)
Pasivní upgrady nemají limit slotů jako zbraně. Každý lze stackovat vícekrát pro masivní vylepšení celkových statistik.
1. **Vitality Tome**: Zvyšuje Max HP o +10 za level (max. Lv. 10).
2. **Power Tome**: Tzv. "Glass Cannon", zvyšuje celkové udělené poškození všech zbraní o 10% (max. Lv. 10).
3. **Speed Tome**: Zvyšuje rychlost pohybu o +0.3 (max. Lv. 8).
4. **Haste Tome**: Zkracuje dobu nabíjení všech zbraní (cooldown reduction) o 5% per level (max. Lv. 10).
5. **Luck Tome**: Mírně navyšuje šanci na lepší (vzácnější) nabídky upgradů karet.

### Reroll (Přehlasování karet)
Pokud se vám nabízené karty nelíbí, můžete použít **Reroll**.
- Klikněte na spodní tlačítko Reroll nebo stiskněte `R`.
- Platí se nasbíranými zlatými mincemi.
- První reroll stojí **3 mince**, každý další je o **2 dražší**. (Cena se při dalším povýšení úsmrti resetuje).

## Technické detaily

### Moduly
- **Camera**: Relativní přesun herního světa odpovídající virtuálnímu přiblížení (1.5x ZOOM).
- **Procedurální staveniště**: Hra vygeneruje plátno plné stěn, omezující postavu k opuštění světa.

### Ovládání Renderu
Vykreslení probíhá v 2 vrstvách:
1. Skutečné nativní plátno hry s danou šířkou (WINDOW_WIDTH / ZOOM) -> "display_surface", do kterého se vykreslují veškeré dynamické entity.
2. Následné překlopení s přepočtem a přiblížením napříč celou plochou monitoru (`pygame.transform.scale`).

### Instalace a spuštění
- Požadavky: Python 3.x, `pygame`
- Instalace knihoven: `pip install pygame`
- Spuštění hry: `python 2dsurvival_game.py`

## Licence
Tento projekt je open-source a může být volně používán.

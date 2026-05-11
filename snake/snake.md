# Dokumentace: Klasický Had (Snake)

Tento projekt je implementací legendární arkádové hry Had (Snake), vytvořenou v jazyce Python. Využívá populární herní knihovnu `pygame` pro vykreslování grafiky a zpracování vstupů od uživatele.

## Požadavky pro spuštění

Ke spuštění hry je nutné mít nainstalovaný Python a knihovnu **pygame**. Tu lze snadno doinstalovat přes terminál pomocí správce balíčků pip:

```bash
pip install pygame
```

## Spuštění hry

Poté, co je nainstalována knihovna `pygame`, stačí hru spustit klasicky z terminálu:

```bash
python snake.py
```
Nebo jednoduše spuštěním skriptu přímo z vašeho editoru.

## Ovládání a pravidla

- **Pohyb**: Pro ovládání hada použijte šipky na klávesnici (Nahoru, Dolů, Doleva, Doprava).
- **Cíl hry**: Sbírejte červené kostičky (jídlo), které se náhodně objevují na hrací ploše.
- **Růst a skóre**: S každým snědeným jídlem se had prodlouží o jeden blok a vaše skóre se zvýší o 1. Aktualní skóre se ukazuje v levém horním rohu obrazovky.
- **Konec hry (Game Over)**: Hra končí prohrou ve dvou případech:
  1. Hlava hada narazí do stěny (okraje obrazovky).
  2. Hlava hada narazí do jakékoliv jiné části vlastního těla.
- **Po prohře**: Na modré obrazovce se objeví text s možnostmi:
  - Stisknutím klávesy `C` (Continue) spustíte novou hru.
  - Stisknutím klávesy `Q` (Quit) hru zcela ukončíte.

## Jak to funguje pod kapotou

Hra běží v tzv. **herní smyčce (Game Loop)** v rámci funkce `gameLoop()`. Tato smyčka běží neustále dokola a s každým proběhnutím aktualizuje stav hry určitou rychlostí (`snake_speed = 15` snímků za sekundu).

- **Tělo hada** je uloženo jako seznam souřadnic (`snake_List`), které představují jednotlivé "kostičky" jeho těla. Při každém "kroku" (snímku) se do seznamu přidá nová pozice hlavy a pokud had v daný krok nejedl, odstraní se naopak konec ocasu. Tím vzniká plynulá iluze pohybu.
- **Kolize s jídlem** se detekuje porovnáním přesných souřadnic hlavy hada a souřadnic vygenerovaného jídla. Pokud se protnou, vygeneruje se jídlo nové aocas hada se nesmaže, čímž had naroste.
- **Detekce prohry** funguje na dvou principech:
  - Hranice okna (`0` až `dis_width`, respektive `dis_height`) určují srážku se stěnou.
  - Srážka sama do sebe se testuje tak, že program projede všechny články hadova těla a pokud se jakýkoliv z nich rovná pozici hlavy, hra končí.

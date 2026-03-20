# Název projektu
snake

## Popis a cíl projektu
Tento malý herní projekt implementuje klasickou hru Snake v Pythonu s
pokročilejšími herními mechanikami (sbírání coinů, updaty, debuffy a štít).
Je určen pro výuku programování a jako jednoduchá ukázka práce s knihovnou
`pygame`.

## Funkcionalita programu
Hra obsahuje tyto hlavní bloky:

- **Herní smyčka**: vykreslování plátna, zpracování vstupu a aktualizace
  stavu hada.
- **Snake logika**: pohyb, kolize s hranou okna, vlastním tělem a překážkami,
  růst po sebrání jídla.
- **Cíl**: dosáhnout 100 bodů (hra skončí s výhrou) a sbírat co nejvíce skóre.
- **Coins / peníze**: skóre se převádí na coinů, které lze utrácet za
  upgrady. Zůstatek se ukládá do souboru.
- **Points upgrade**: zvyšuje počet bodů za každé snězené jídlo. Stav se
  persistuje v `upgrade.txt`.
- **Coin upgrade**: zvyšuje množství získaných peněz ze skóre. Stav se
  persistuje v `coin_upgrade.txt`.
- **Debuff systém**: každých 10 bodů hráč vybírá jednu ze tří skrytých karet.
  Každá karta aplikuje náhodný debuff (např. zrychlení, obrácené ovládání,
  mlha, více překážek, teleport, snížení délky hada apod.).
- **Power‑up štít**: po sebrání jídla se s určitou pravděpodobností objeví
  štít; ten jednou zabrání smrti kolizí.
- **Překážky**: statické i (jako výsledek debuffu) pohyblivé překážky.

## Menu a ovládání
V menu:

- `Enter` – spustí hru
- `Q` nebo `Esc` – ukončí program
- `R` – resetuje zůstatek a obě úrovně upgradů (body + coiny)
- `U` – vylepší bodový bonus (pokud máte dost coinů)
- `C` – vylepší coinový bonus (pokud máte dost coinů)

Ve hře:

- šipky – pohyb
- `Esc` – ukončení hry a návrat do menu

## Persistovaná data
V adresáři `snake/` se ukládají tyto soubory:

- `balance.txt`: aktuální zůstatek coinů
- `highscore.txt`: nejlepší dosažené skóre
- `upgrade.txt`: úroveň bodového upgradu (0–6)
- `coin_upgrade.txt`: úroveň coinového upgradu (0–6)

--
# Název projektu

## Popis a cíl projektu
Tento malý herní projekt implementuje klasickou hru Snake v Pythonu s
rozšířením o sbírání mincí, dvěma druhy upgrade schopností ("shockwave" a
bonus za rychlejší získávání coinů). Je určen pro výuku programování nebo
jako jednoduchá zábavná ukázka práce s knihovnou pygame.

## Funkcionalita programu
Hra se skládá z těchto technických bloků:

- **Herní smyčka**: vykreslování plátna, zpracování událostí a aktualizace
  stavu hada.
- **Snake logika**: pohyb, kolize s hranami a vlastním tělem, růst po sebrání
  jídla.
- **Coin systém**: skóre konvertované na měnu, která se ukládá v souboru.
- **Shockwave upgrade**: opakovatelná schopnost s úrovněmi, která při
  aktivaci sbírá jídlo v okolí. Úroveň se zvyšuje v menu, cena roste
  lineárně, stav se ukládá do `upgrade.txt`.
- **Coin upgrade**: opakovatelná úroveň, která zvyšuje množství
  získaných coinů; cena roste lineárně, stav se ukládá do
  `coin_upgrade.txt`.
- **Menu**: umožňuje začít hru, koupit/upgradovat shockwave, resetovat mince
  a úroveň nebo ukončit program.

(Stručně: uživatelské ovládání je realizováno přes klávesnice, data se
persistují do několika jednoduchých textových souborů.)

---

*Dokumentace upravena podle uživatelského požadavku.*
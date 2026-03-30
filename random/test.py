import re

text = "Regulární výraz (zkratky regexp, regex či RE z anglického regular expression) je textový řetězec, který slouží jako vzor pro vyhledávání textu. Regulární výraz tvoří soubor dvou typů znaků – literálů"

all_word = re.findall(regex_words, text)
# print (all_words)

regex_spaces = r"\x20"

all_spaces = re.findall(regex_spaces, text)
print(f"Pocet mezer: {len(all_spaces)}")

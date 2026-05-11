import tkinter as tk

def click(event):
    global current_equation
    text = event.widget.cget("text")
    
    if text == "=":
        try:
            # Používáme eval pro výpočet výrazu
            result = str(eval(current_equation))
            display_var.set(result)
            current_equation = result
        except ZeroDivisionError:
            display_var.set("Dělení nulou!")
            current_equation = ""
        except Exception as e:
            display_var.set("Chyba")
            current_equation = ""
    elif text == "C":
        current_equation = ""
        display_var.set("")
    else:
        current_equation += text
        display_var.set(current_equation)

root = tk.Tk()
root.title("Kalkulačka")
root.geometry("300x400")
root.resizable(False, False)

current_equation = ""
display_var = tk.StringVar()

# Displej pro zobrazení čísel a výsledku
display = tk.Entry(root, textvar=display_var, font="Arial 24 bold", bg="#f0f0f0", fg="black", bd=5, justify="right")
display.pack(fill=tk.BOTH, ipadx=8, pady=10, padx=10)

# Rámec pro tlačítka
button_frame = tk.Frame(root)
button_frame.pack()

# Rozložení tlačítek
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["C", "0", "=", "+"]
]

for row in buttons:
    f = tk.Frame(button_frame)
    f.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    for btn_text in row:
        # Barevné odlišení tlačítek
        if btn_text in ["=", "C", "/", "*", "-", "+"]:
            bg_color = "#d9d9d9"
        else:
            bg_color = "white"
            
        btn = tk.Button(f, text=btn_text, font="Arial 18 bold", bg=bg_color, height=2, width=4)
        btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=2, pady=2)
        btn.bind("<Button-1>", click)

root.mainloop()

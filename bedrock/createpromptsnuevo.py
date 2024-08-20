import random

with open("./data/claves-combinadas-completo.csv", "r", encoding="utf-8-sig") as f:
    items = f.read().removesuffix('\n').split('\n')
items.pop(0)
items.pop(0)

items = list(map(lambda x: x.split(','), items))

titantxt = ""

for index, item in enumerate(items[0:500]):
    random_index = random.randint(0, 4676)
    random_index_2 = random.randint(0, 4676)

    if index % 500 == 0:
        print(index)

    product = items[random_index][1]
    query = items[random_index][3]
    
    prompt_titan = f"""You are going to play the role of an assistant at a hardware store and you are going to help a
customer find the item that they are looking for. You asked you co-worker to bring you the item that most resembles the
customer's description. Now, you must determine if they brought the correct item or not.

First, you must determine what type of item the customer is looking for based on the description. For example, if the
customer asks for "Abrazadera #10 (19-27mm) 3/4 - 1-1/16 c/10pz AB10 Fiero," you know they are looking for an
"abrazadera".

If the customer mentions any measurement/caliber/length/gauge, you must also make sure that they are the same. In the
past example, you should make sure the item is #10 and 3/4 - 1 1/16 inches, or 19-27 mm.

The two items must also be the same brand, if the brand is mentioned. Normally, it is mentioned at the end of the
description.

If the customer mentions a color, you must make sure that the item is of the same color.

For electronic components, their specifications (voltage, current, resistance, etc.) must be the same.

Lastly, if the customer mentions a count, you must also make sure to pick an item that contains the same count. The
past examples mentions "10 pz," so make sure to give a customer an item with 10 pieces.

The following is an example of products that are not equivalent:
"Remaches con espiga 6.4x15.9mm bolsa con 50 pzas" and "Remache diam 3/16 agarre 1/2 c/50pz R68B Fiero"
Notice how in this example, the type of item is the same, but the size is different.

The following is an example of products that are equivalent:
"Rotomartillo 1/2' 550 W Pretul" and "Rotomartillo 1/2 550w ROTO1/2P6 Pretul"

The customer is looking for the item with the following description:
"{query}"

Your co-worker brought the following item:
"{product}"

Are they the same item? Respond with a confidence score (0.0 - 1.0) that represents how likely it is that the item is
the same as the item that the customer is looking for.--------"""
    
    titantxt += prompt_titan

    with open(f"./promptsnuevos/titan-sison-{index}.txt", "w+") as f:
        f.write(prompt_titan.removesuffix("--------"))

with open("./promptsnuevos/prompts-titan.txt", "w+", encoding="utf-8-sig") as f:
    f.write(titantxt.removesuffix("--------"))
import json
import psycopg2
import psycopg2.extras
import boto3
import random
import time

bedrock = boto3.client('bedrock-runtime')

def invoke(item_1, item_2):
    input_text = f"""You are going to play the role of an assistant at a hardware store and you are going to help a
customer find the item that they are looking for. You asked you co-worker to bring you the item that most resembles the
customer's description. Now, you must determine if they brought the correct item or not.

First, you must determine what type of item the customer is looking for based on the description. For example, if the
customer asks for "Abrazadera #10 (19-27mm) 3/4 - 1-1/16 c/10pz AB10 Fiero," you know they are looking for an
"abrazadera".

If the customer mentions any measurement/caliber/length/gauge, you must also make sure that they are the same. In the
past example, you should make sure the item is #10 and 3/4 - 1 1/16 inches, or 19-27 mm.

Lastly, if the customer mentions a count, you must also make sure to pick an item that contains the same count. The
past examples mentions "10 pz," so make sure to give a customer an item with 10 pieces.

The following is an example of products that are not equivalent:
"Remaches con espiga 6.4x15.9mm bolsa con 50 pzas" and "Remache diam 3/16 agarre 1/2 c/50pz R68B Fiero"
Notice how in this example, the type of item is the same, but the size is different.

The following is an example of products that are equivalent:
"Rotomartillo 1/2' 550 W Pretul" and "Rotomartillo 1/2 550w ROTO1/2P6 Pretul"

The customer is looking for the item with the following description:
"{item_1}"

Your co-worker brought the following item:
"{item_2}"

Are they the same item? Respond with a confidence score (0.0 - 1.0) that represents how likely it is that the item is
the same as the item that the customer is looking for."""

    body = json.dumps({"inputText": input_text, "textGenerationConfig": {"maxTokenCount": 10}})
    modelId = "amazon.titan-text-premier-v1:0"
    accept = "application/json"
    contentType = "application/json"

    try:
        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    except:
        time.sleep(5)
        response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    responsebody = json.loads(response.get("body").read())
    return responsebody.get("results")[0].get("outputText")

def query_clave(claves):
    if claves == []:
        return []

    ids = ''
    for clave in claves:
        ids += f"'{clave}',"
    ids = ids.removesuffix(',')
    query = f"""SELECT
        articulos.nombre,
        STRING_AGG(claves.clave, ', ') AS claves
    FROM
        public.articulos_dev__articulos AS articulos
    LEFT JOIN
        public.articulos_dev__articulo_clave AS claves
    ON
        articulos.id = claves.articulo_id
    WHERE
        articulos.empresa_id = 279
    AND
        claves.clave IN ({ids})
    GROUP BY
        articulos.nombre;"""

    connection = psycopg2.connect(dbname='RomboDev', user='root', password='q(Z*-=2{uUEV].OOJ+U2lGBRu%PyM}lA', host='rombo-dev.cj5slgb6v6em.us-west-2.rds.amazonaws.com', port='5432', sslmode='require')
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def query_nombre(nombre):
    query = f"""SELECT nombre
    FROM public.articulos_dev__articulos
    WHERE empresa_id = 279
    AND difference(nombre, '{nombre}') > 2
    ORDER BY levenshtein(nombre, '{nombre}')
    LIMIT 5;"""

    connection = psycopg2.connect(dbname='RomboDev', user='root', password='q(Z*-=2{uUEV].OOJ+U2lGBRu%PyM}lA', host='rombo-dev.cj5slgb6v6em.us-west-2.rds.amazonaws.com', port='5432', sslmode='require')
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()  
    return results

def buscar(nombre, claves=[]):
    query_results = query_clave(claves)

    if(query_results != []):
        score = float(invoke(nombre, query_results[0][0]))
        if score >= 0.8:
            return {"articulo": query_results[0][0], "resultado": "seguro", "score": score}
        if score >= 0.5:
            return {"articulo": query_results[0][0], "resultado": "probable", "score": score}
        return {"articulo": query_results[0][0], "resultado": "vacio", "score": score}

    query_results = query_nombre(nombre)
    if(query_results == []):
        return {"articulo": "vacio", "resultado": "vacio", "score": 0.0}

    max_score = 0.0
    max_score_nombre = ''
    for articulo in query_results:
        score = float(invoke(nombre, articulo[0]))
        if score > max_score:
            max_score = score
            max_score_nombre = articulo[0]
    if max_score >= 0.9:
        return {"articulo": max_score_nombre, "resultado": "seguro", "score": max_score}
    if max_score >= 0.6:
        return {"articulo": max_score_nombre, "resultado": "probable", "score": max_score}
    return {"articulo": max_score_nombre, "resultado": "vacio", "score": max_score}
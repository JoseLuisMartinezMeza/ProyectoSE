# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 18:49:55 2023

@author: pepem
"""
import sys
import tkinter as tk
from tkinter import messagebox
import random
from tkinter import simpledialog
from collections import Counter

respuestas_afirmativas_a = 0
questionIndex = 0
questionNumber = 1
infoDisplayed = False
questions = []
answers = []
shuffledIndexes = []
userSelections = ""

def main():
    cargar_preguntas_desde_archivo("preguntas.txt")
    global answers, respuestas_afirmativas_a 
    answers = [""] * len(questions)
    reset_variables()
    generar_indices_aleatorios()
    sistema_experto_inicio()

def sistema_experto_inicio():
    response = messagebox.askyesno("Sistema Experto de Adivinanzas de Pokemon",
                                   "¡Bienvenido al sistema experto de adivinanzas de Pokemon!\n\n"
                                   "La dinámica es la siguiente:\n"
                                   "     * Te presentaré 5 Pokemon misteriosos.\n"
                                   "     * Piensa en un pokemon que te guste y yo trataré de adivinar en cuál estás pensando.\n"
                                   "     * Si tu respuesta es afirmativa, haz clic en 'Sí', si es negativa, haz clic en 'No'.\n\n"
                                   "Elige una opción para comenzar:", icon='info',
                                   )
    if response:
        adivinar()
    else:
        messagebox.showinfo("Sistema Experto de Adivinanzas de Pokemon", "\n*******-Nos vemos luego-*******")
        exit()

def adivinar():
    global questionIndex, infoDisplayed, userSelections, respuestas_afirmativas_a, respuesta_g2

    if not infoDisplayed:
        informacion()
        infoDisplayed = True

    while questionIndex < len(questions):
        pregunta_actual = questions[shuffledIndexes[questionIndex]]
        tipo_pregunta_actual, numero_pregunta_actual = obtener_tipo_y_numero_pregunta(pregunta_actual)

        response = messagebox.askyesno(f"Pregunta {tipo_pregunta_actual}.{numero_pregunta_actual}",
                                       pregunta_actual, icon='question')

      

        if response:
            answers[shuffledIndexes[questionIndex]] = "Si"
            userSelections += f"{tipo_pregunta_actual}.{numero_pregunta_actual}Si"
        else:
            answers[shuffledIndexes[questionIndex]] = "No"
            userSelections += f"{tipo_pregunta_actual}.{numero_pregunta_actual}No"

        guardar_respuesta("Pregunta #" + str(questionNumber) + ": " +
                          questions[shuffledIndexes[questionIndex]] + ": " +
                          answers[shuffledIndexes[questionIndex]])

        if should_predict():
            display_prediction()
            return

        questionIndex += 1

    nombre_archivo = "solo.txt"

    encontrado = False
    try:
        with open(nombre_archivo, 'r') as reader:
            for line in reader:
                if userSelections in line:
                    start_index = line.find(userSelections)
                    nombre = line[:start_index]
                    messagebox.showinfo("Nombre encontrado", "Nombre encontrado: " + nombre)
                    encontrado = True
    except IOError as e:
        print(e)

    if not encontrado:
        nombre_pokemon = messagebox.askstring("Pokemon no encontrado",
                                              "El Pokémon no se encontró en el archivo. Por favor, ingresa el nombre del Pokémon:")
        guardar_nombre_pokemon(nombre_pokemon)
        guardar_respuesta_solo(nombre_pokemon + ":" + userSelections)

    juguemos_nuevamente()


def obtener_tipo_y_numero_pregunta(pregunta_actual):
    if pregunta_actual is None:
        return None, None

    tipo_pregunta = None
    numero_pregunta = ""

    # Busca la primera letra que indica el tipo de pregunta (G, A, B, C, etc.)
    for char in pregunta_actual:
        if char.isalpha():
            tipo_pregunta = char
            break

    # Busca los dígitos que siguen a la letra del tipo de pregunta
    for char in pregunta_actual:
        if char.isdigit():
            numero_pregunta += char
        elif numero_pregunta:
            # Si encontramos un carácter que no es un dígito después de los dígitos, terminamos
            break

    return tipo_pregunta, int(numero_pregunta) if numero_pregunta else None

def obtener_tipo_pregunta(pregunta_actual):
    if pregunta_actual and len(pregunta_actual) > 0:
        primera_letra_tipo = pregunta_actual[0].upper()
        if primera_letra_tipo in ['G.', 'A.', 'B.', 'C.']:
            return primera_letra_tipo
        else:
            return "Otro"
    else:
        return None
    
def obtener_tipo_pregunta_index(tipo):
    global shuffledIndexes
    # Recorrer la lista de índices revueltos
    for i in range(len(shuffledIndexes)):
        # Obtener el tipo de la pregunta actual
        tipo_pregunta = obtener_tipo_pregunta(questions[shuffledIndexes[i]])
        # Si el tipo de la pregunta coincide con el tipo dado, devolver el índice
        if tipo_pregunta == tipo:
            return i
    # Si no se encuentra ninguna pregunta del tipo dado, devolver -1
    return -1


def obtener_tipo_pregunta_numero(tipo_pregunta):
    global shuffledIndexes
    tipo_pregunta_index = obtener_tipo_pregunta_index(tipo_pregunta)
    tipo_pregunta_numero = tipo_pregunta_index + 1
    return tipo_pregunta_numero



def should_predict(user_responses, questions):
    total_questions = len(questions)
    matching_count = sum(1 for response in user_responses if response == "Si" or response == "No")
    matching_percentage = matching_count / total_questions * 100
    historical_threshold = calculate_historical_threshold(user_responses)
    return matching_percentage >= historical_threshold

def calculate_historical_threshold(user_responses):
    nombre_archivo = "solo.txt"
    try:
        with open(nombre_archivo, 'r') as reader:
            total_matching_percentage = 0.0
            count = 0
            user_responses_counter = Counter(user_responses)
            for line in reader:
                parts = line.split(":")
                if len(parts) > 1:
                    responses_dataset = parts[1].strip()
                    dataset_counter = Counter(responses_dataset)
                    matching_percentage = calculate_matching_percentage(user_responses_counter, dataset_counter)
                    total_matching_percentage += matching_percentage
                    count += 1
            return total_matching_percentage / count if count > 0 else 100.0
    except IOError as e:
        print(e)
        return 100.0

def calculate_matching_percentage(user_responses_counter, dataset_counter):
    total_questions = sum(min(user_responses_counter[response], dataset_counter[response]) for response in user_responses_counter)
    total_user_responses = sum(user_responses_counter.values())
    return total_questions / total_user_responses * 100 if total_user_responses > 0 else 0.0

def display_prediction(user_responses, questions):
    nombre_archivo = "solo.txt"
    try:
        with open(nombre_archivo, 'r') as reader:
            max_matching_percentage = 0.0
            predicted_object = ""
            user_responses_counter = Counter(user_responses)
            for line in reader:
                parts = line.split(":")
                if len(parts) > 1:
                    object_name = parts[0]
                    responses_dataset = parts[1].strip()
                    dataset_counter = Counter(responses_dataset)
                    matching_percentage = calculate_matching_percentage(user_responses_counter, dataset_counter)

                    if matching_percentage > max_matching_percentage:
                        max_matching_percentage = matching_percentage
                        predicted_object = object_name

            if predicted_object:
                response = messagebox.askyesno("¡Predicción!",
                                               f"¡Predicción!: {predicted_object}\n¿Es correcta la predicción?", icon='question')
                if response:
                    juguemos_nuevamente()
                else:
                    obtener_retroalimentacion_incorrecta(predicted_object)
            else:
                messagebox.showinfo("No se pudo hacer una predicción.", "No se pudo hacer una predicción.")
    except IOError as e:
        print(e)

def obtener_retroalimentacion_incorrecta(predicted_pokemon):
    nueva_pregunta = simpledialog.askstring("Retroalimentación incorrecta",
                                            "¡Vaya! Parece que no adiviné correctamente. "
                                            "Ayúdame a mejorar. Proporciona el nombre del pokemon nuevo")
    if nueva_pregunta:
        guardar_respuesta_solo(nueva_pregunta + ":" + userSelections)
        juguemos_nuevamente()
    else:
        messagebox.showinfo("Nueva pregunta vacía", "La nueva pregunta no puede estar vacía. Intenta nuevamente.")
        obtener_retroalimentacion_incorrecta(predicted_pokemon)

def guardar_nombre_pokemon(nombre):
    if nombre:
        try:
            with open("result.txt", 'a') as writer:
                writer.write(nombre + "\n")
        except IOError as e:
            print(e)
    else:
        print("El nombre del Pokémon es nulo.")

def cargar_un_resultado_desde_archivo(archivo):
    try:
        with open(archivo, 'r') as reader:
            return reader.readline()
    except IOError as e:
        print(e)
        return "Error al cargar el resultado"

def informacion():
    informacion_texto = cargar_informacion_desde_archivo("informacion.txt")
    messagebox.showinfo("Información", informacion_texto)

def juguemos_nuevamente():
    options = ["Sí", "No"]
    response = messagebox.askyesno("Reinicio", "¿Quieres jugar de nuevo?", icon='question')

    if response:
        reset_variables()
        generar_indices_aleatorios()  # Generamos nuevos índices aleatorios para el próximo juego
        sistema_experto_inicio()
    else:
        messagebox.showinfo("Nos vemos luego", "\n*******-Nos vemos luego-*******")
        sys.exit()

def guardar_respuesta(respuesta):
    try:
        with open("basededato.txt", 'a') as writer:
            writer.write(respuesta + "\n")
    except IOError as e:
        print(e)

def guardar_respuesta_solo(respuesta):
    try:
        with open("solo.txt", 'a') as writer:
            writer.write(respuesta + "\n")
    except IOError as e:
        print(e)

def guardar_resultado_en_archivo(result):
    try:
        with open("result.txt", 'w') as writer:
            writer.write(result)
    except IOError as e:
        print(e)

def cargar_preguntas_desde_archivo(archivo):
    try:
        with open(archivo, 'r') as reader:
            global questions
            questions = reader.read().splitlines()
    except IOError as e:
        print(e)

def cargar_informacion_desde_archivo(archivo):
    try:
        with open(archivo, 'r') as reader:
            return reader.read()
    except IOError as e:
        print(e)
        return ""

def generar_indices_aleatorios():
    global shuffledIndexes, questionIndex, tipo_pregunta_actual
    questionIndex = 0

    # Obtener índices de preguntas de cada tipo
    preguntas_tipo_g = [i for i, pregunta in enumerate(questions) if pregunta.startswith("G.")]
    preguntas_tipo_a = [i for i, pregunta in enumerate(questions) if pregunta.startswith("A.")]
    preguntas_tipo_c = [i for i, pregunta in enumerate(questions) if pregunta.startswith("C.")]
    preguntas_tipo_b = [i for i, pregunta in enumerate(questions) if pregunta.startswith("B.")]

    # Revolver los índices de cada tipo
    random.shuffle(preguntas_tipo_g)
    random.shuffle(preguntas_tipo_a)
    random.shuffle(preguntas_tipo_c)
    random.shuffle(preguntas_tipo_b)

    # Inicializar los índices
    shuffledIndexes = []

    # Si hay preguntas del tipo G, agréguelas al índice aleatorio
    if preguntas_tipo_g:
        shuffledIndexes.extend(preguntas_tipo_g)
    if preguntas_tipo_a:
        shuffledIndexes.extend(preguntas_tipo_a)
    if preguntas_tipo_b:
        shuffledIndexes.extend(preguntas_tipo_b)
    if preguntas_tipo_c:
        shuffledIndexes.extend(preguntas_tipo_c)


    # Asegurarse de que no se repitan preguntas
    while tiene_repetidos(shuffledIndexes):
        random.shuffle(shuffledIndexes)

    tipo_pregunta_actual = obtener_tipo_pregunta(questions[shuffledIndexes[questionIndex]])


def tiene_repetidos(lst):
    counter = Counter(lst)
    return any(count > 1 for count in counter.values())

def reset_variables():
    global questionIndex, questionNumber, infoDisplayed, userSelections, answers
    questionIndex = 0
    questionNumber = 1
    infoDisplayed = False
    userSelections = ""
    answers = [""] * len(questions)
    generar_indices_aleatorios()

def guardar_nueva_pregunta(nueva_pregunta, nombre_pokemon):
    if nueva_pregunta and nombre_pokemon:
        try:
            with open("preguntas.txt", 'a') as writer:
                writer.write(nueva_pregunta + ":" + nombre_pokemon + "\n")
        except IOError as e:
            print(e)
    else:
        print("La nueva pregunta o el nombre del Pokémon son nulos.")

def guardar_nueva_pregunta2(nombre_pokemon):
    if nombre_pokemon:
        try:
            with open("solo.txt", 'a') as writer:
                writer.write(nombre_pokemon + "\n")
        except IOError as e:
            print(e)
    else:
        print("El nombre del Pokémon es nulo.")
        
def acomodar_pokemon(resultados_file, respuestas_file, solo_file):
    try:
        with open(resultados_file, 'r') as resultados_reader, \
                open(respuestas_file, 'r') as respuestas_reader, \
                open(solo_file, 'w') as solo_writer:

            nombre_pokemon = ""
            respuestas = []

            for line in resultados_reader:
                # Leer el nombre del Pokémon
                if line.startswith("Resultado: "):
                    nombre_pokemon = line.replace("Resultado: ", "").strip()
                    solo_writer.write(nombre_pokemon + ":")

                    # Leer las respuestas del archivo "respuestas.txt"
                    for _ in range(10):
                        respuestas_line = respuestas_reader.readline()
                        if respuestas_line:
                            respuesta = "Si" if respuestas_line.endswith("Si") else "No"
                            respuestas.append(respuesta)

                    # Escribir las respuestas en el archivo "solo.txt"
                    solo_writer.write("".join(respuestas))
                    solo_writer.write("\n")
                    respuestas.clear()

        print("Acomodo de Pokémon y respuestas guardado en", solo_file)

    except IOError as e:
        print(e)

# Uso de la función
resultados_file = "result.txt"
respuestas_file = "basededato.txt"
solo_file = "solo.txt"


if __name__ == "__main__":
    main()

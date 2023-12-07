# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 19:42:50 2023

@author: pepem
"""

import sys
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
from sklearn.tree import DecisionTreeClassifier
import numpy as np

questionIndex = 0
questionNumber = 1
infoDisplayed = False
questions = []
answers = []
shuffledIndexes = []
userSelections = []

def main():
    cargar_preguntas_desde_archivo("preguntas.txt")
    global answers
    answers = np.zeros((len(questions),), dtype=int)
    reset_variables()
    generar_indices_aleatorios()
    sistema_experto_inicio()

def sistema_experto_inicio():
    response = messagebox.askyesno("Sistema Experto de Adivinanzas de Pokemon",
                                   "¡Bienvenido al sistema experto de adivinanzas de Pokemon!\n\n"
                                   "La dinámica es la siguiente:\n"
                                   "     * Te presentaré 5 Pokemon misteriosos.\n"
                                   "     * Piensa en un Pokémon que te guste y yo trataré de adivinar en cuál estás pensando.\n"
                                   "     * Si tu respuesta es afirmativa, haz clic en 'Sí', si es negativa, haz clic en 'No'.\n\n"
                                   "Elige una opción para comenzar:", icon='info',
                                   )
    if response:
        adivinar()
    else:
        messagebox.showinfo("Sistema Experto de Adivinanzas de Pokemon", "\n*******-Nos vemos luego-*******")
        sys.exit()

def adivinar():
    global questionIndex, questionNumber, infoDisplayed, userSelections

    if not infoDisplayed:
        informacion()
        infoDisplayed = True

    while questionIndex < len(questions):
        response = messagebox.askyesno("Pregunta #" + str(questionNumber),
                                       questions[shuffledIndexes[questionIndex]], icon='question')

        if response:
            answers[shuffledIndexes[questionIndex]] = 1  # 1 for 'Si'
            userSelections += '1'
        else:
            answers[shuffledIndexes[questionIndex]] = 0  # 0 for 'No'
            userSelections += '0'

        guardar_respuesta("Pregunta #" + str(questionNumber) + ": " +
                          questions[shuffledIndexes[questionIndex]] + ": " +
                          str(answers[shuffledIndexes[questionIndex]]))

        if should_predict():
            display_prediction()
            return

        questionIndex += 1
        questionNumber += 1

    nombre_archivo = "solo.txt"

    encontrado = False
    try:
        with open(nombre_archivo, 'r') as reader:
            for line in reader:
                if userSelections == list(map(int, line.strip())):
                    start_index = line.find(':')
                    nombre = line[:start_index]
                    messagebox.showinfo("Nombre encontrado", "Nombre encontrado: " + nombre)
                    encontrado = True
    except IOError as e:
        print(e)

    if not encontrado:
        nombre_pokemon = messagebox.askstring("Pokemon no encontrado",
                                              "El Pokémon no se encontró en el archivo. Por favor, ingresa el nombre del Pokémon:")
        guardar_nombre_pokemon(nombre_pokemon)
        guardar_respuesta_solo(nombre_pokemon + ":" + ":".join(map(str, userSelections)))

    juguemos_nuevamente()
    reset_variables()

def should_predict():
    total_questions = len(questions)
    matching_count = sum(1 for answer in answers if answer == 1 or answer == 0)
    matching_percentage = matching_count / total_questions * 100
    historical_threshold = calculate_historical_threshold(userSelections)
    return matching_percentage >= historical_threshold

def calculate_historical_threshold(user_responses):
    nombre_archivo = "solo.txt"
    try:
        with open(nombre_archivo, 'r') as reader:
            total_matching_percentage = 0.0
            count = 0
            for line in reader:
                parts = line.strip().split(':')
                if len(parts) > 1:
                    responses_dataset = [1 if resp == 'S' else 0 for resp in list(parts[1])]
                    matching_percentage = best_first_search(list(map(int, user_responses)), responses_dataset)
                    total_matching_percentage += matching_percentage
                    count += 1
            return total_matching_percentage / count if count > 0 else 100.0
    except IOError as e:
        print(e)
        return 100.0
def best_first_search(user_responses, dataset_responses):
    total_questions = min(len(user_responses), len(dataset_responses))
    matching_count = sum(1 for i in range(total_questions) if user_responses[i] == dataset_responses[i])
    return matching_count / total_questions * 100 if total_questions > 0 else 0.0

def display_prediction():
    clf = DecisionTreeClassifier()
    clf.fit(np.eye(len(questions)), answers)
    predicted_pokemon = clf.predict([userSelections])[0]

    response = messagebox.askyesno("¡Predicción!",
                                   "¡Predicción!: " + predicted_pokemon +
                                   "\n¿Es correcta la predicción?", icon='question')
    if response:
        juguemos_nuevamente()
    else:
        obtener_retroalimentacion_incorrecta(predicted_pokemon)

def obtener_retroalimentacion_incorrecta(predicted_pokemon):
    nueva_pregunta = simpledialog.askstring("Retroalimentación incorrecta",
                                            "¡Vaya! Parece que no adiviné correctamente. "
                                            "Ayúdame a mejorar. Proporciona una nueva pregunta que distinguirá a " +
                                            predicted_pokemon + ":")
    if nueva_pregunta:
        guardar_respuesta_solo(nueva_pregunta + ":" + ":".join(map(str, userSelections)))
        juguemos_nuevamente()
    else:
        messagebox.showinfo("Nueva pregunta vacía", "La nueva pregunta no puede estar vacía. Intenta nuevamente.")
        obtener_retroalimentacion_incorrecta(predicted_pokemon)

def calculate_matching_percentage(user_responses_counter, dataset_counter):
    total_questions = sum(min(user_responses_counter[response], dataset_counter[response]) for response in user_responses_counter)
    total_user_responses = sum(user_responses_counter.values())
    return total_questions / total_user_responses * 100 if total_user_responses > 0 else 0.0

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
    global shuffledIndexes
    shuffledIndexes = list(range(len(questions)))
    random.shuffle(shuffledIndexes)

def reset_variables():
    global questionIndex, questionNumber, infoDisplayed, userSelections, answers
    questionIndex = 0
    questionNumber = 1
    infoDisplayed = False
    userSelections = []
    answers = np.zeros((len(questions),), dtype=int)
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

if __name__ == "__main__":
    main()
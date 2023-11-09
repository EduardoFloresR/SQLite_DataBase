import sqlite3
import os
from datetime import datetime # Importar el módulo datetime para obtener la fecha actual

def limpiar_terminal():
    # Verificar el sistema operativo y ejecutar el comando apropiado para limpiar la terminal
    sistema_operativo = os.name

    if sistema_operativo == 'posix':  # Linux y macOS
        os.system('clear')
    elif sistema_operativo == 'nt':  # Windows
        os.system('cls')
    else:
        print("No se pudo determinar el sistema operativo. La terminal no se limpiará automáticamente.")

def imprimir_libros():
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()

        # Obtener todos los ID y títulos de los libros
        c.execute("SELECT id, titulo, autor_id FROM Libros")
        libros = c.fetchall()

        if libros:
            print("ID\tTítulo\tAutor")
            for libro in libros:
                libro_id = libro[0]
                titulo = libro[1]
                autor_id = libro[2]

                # Obtener el nombre del autor desde la tabla Autores
                c.execute("SELECT nombre FROM Autores WHERE id = ?", (autor_id,))
                nombre_autor = c.fetchone()

                if nombre_autor:
                    print(f"{libro_id}\t{titulo}, {nombre_autor[0]}")
                else:
                    print(f"{libro_id}\t{titulo}, Autor no encontrado")
        else:
            print("No hay libros registrados en la base de datos.")

        # Cerrar la conexión
        conn.close()
    except sqlite3.Error as e:
        print("Error al imprimir los libros:", e)

def imprimir_libro(c, titulo):
    try:
        # Imprimir la información del libro recién agregado
        c.execute("SELECT * FROM Libros WHERE titulo = ?", (titulo,))
        libro = c.fetchone()

        if libro:
            print("\nInformación del libro:")
            print(f"ID: {libro[0]}")
            print(f"Título: {libro[1]}")
            # Obtener el nombre del autor desde la tabla Autores
            autor_id = libro[2]
            c.execute("SELECT nombre FROM Autores WHERE id = ?", (autor_id,))
            nombre_autor = c.fetchone()
            if nombre_autor:
                print(f"Autor: {nombre_autor[0]} (ID={libro[2]})")
            else:
                print("Error al obtener el nombre del autor.")
            print(f"Año de publicación: {libro[3]}")
        else:
            print("Error al obtener información del libro.")
    except sqlite3.Error as e:
        print("Error al desplegar la información del libro:", e)

def agregar_autor_libro(c, conn, nombre_autor, titulo, año_publicacion):
    biografia_autor = input("Ingrese la biografía del autor: ")

    try:
        # Insertar un nuevo autor en la tabla Autores
        c.execute("INSERT INTO Autores (nombre, biografia) VALUES (?, ?)",
                  (nombre_autor, biografia_autor))

        # Obtener el ID del autor recién insertado
        c.execute("SELECT last_insert_rowid()")
        autor_id = c.fetchone()[0]

        # Insertar un nuevo libro en la tabla Libros
        c.execute("INSERT INTO Libros (titulo, autor_id, año_publicacion) VALUES (?, ?, ?)",
                  (titulo, autor_id, año_publicacion))

        # Guardar (commit) los cambios y cerrar la conexión
        conn.commit()
        print(f"Autor registrado")
        print("\nLibro agregado con éxito.")
        imprimir_libro(c, titulo)

    except sqlite3.Error as e:
        print("Error al agregar el autor y el libro:", e)

def agregar_libro():
    titulo = input("Ingrese el título del libro: ")
    año_publicacion = int(input("Ingrese el año de publicación: "))
    nombre_autor = input("Ingrese el nombre del autor: ")

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()

        # Verificar si el autor existe en la tabla Autores
        c.execute("SELECT id FROM Autores WHERE nombre = ?", (nombre_autor,))
        autor_existente = c.fetchone()

        if autor_existente:
            autor_id = autor_existente[0]

            # Insertar un nuevo libro en la tabla Libros
            c.execute("INSERT INTO Libros (titulo, autor_id, año_publicacion) VALUES (?, ?, ?)",
                      (titulo, autor_id, año_publicacion))

            # Guardar (commit) los cambios
            conn.commit()
            print("\nLibro agregado con éxito.")
            imprimir_libro(c, titulo)

        else:
            print("\nEl autor no existe en la base de datos.")
            agregarAutor = input("¿Deseas agregarlo? Y/N: ")
            if (agregarAutor == "Y" or agregarAutor == "y"):
                agregar_autor_libro(c, conn, nombre_autor, titulo, año_publicacion)
            else:
                print("Error al agregar el libro")
        
        conn.close()

    except sqlite3.Error as e:
        print("Error al agregar el libro:", e)

def buscar_libro():
    titulo = input("Ingrese el título del libro a buscar: ")

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()

        # Buscar el libro por título
        c.execute("SELECT * FROM Libros WHERE titulo = ?", (titulo,))
        libro = c.fetchone()

        if libro:
            print("Libro encontrado")
            imprimir_libro(c, titulo)
        else:
            print("Libro no encontrado")

        # Cerrar la conexión
        conn.close()
    except sqlite3.Error as e:
        print("Error al buscar el libro:", e)

def agregar_prestamo():
    usuario = input("Ingrese el nombre del usuario: ")
    fecha_prestamo = input("Ingrese la fecha del préstamo [AAAA-MM-DD] (vacío para la fecha de hoy): ")
    if fecha_prestamo == "" or len(fecha_prestamo)!=10:
        fecha_prestamo = datetime.now().strftime('%Y-%m-%d')
    libro_id = input("Ingrese el ID del libro prestado: ")

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()

        # Verificar si el libro existe en la tabla Libros
        c.execute("SELECT id, disponible FROM Libros WHERE id = ?", (libro_id,))
        libro_info = c.fetchone()

        if libro_info:
            libro_id = libro_info[0]
            disponibilidad = libro_info[1]

            if disponibilidad > 0:
                # Insertar un nuevo préstamo en la tabla Prestamos
                c.execute("INSERT INTO Prestamos (libro_id, usuario, fecha_prestamo, fecha_devolucion) VALUES (?, ?, ?, ?)",
                          (libro_id, usuario, fecha_prestamo, None))

                # Actualizar la disponibilidad del libro
                c.execute("UPDATE Libros SET disponible = ? WHERE id = ?", (disponibilidad - 1, libro_id))

                # Guardar (commit) los cambios
                conn.commit()

                print("Préstamo agregado con éxito.")
            else:
                print("No hay disponibilidad para el libro con ID:", libro_id)
        else:
            print("Error al agregar el préstamo.\nEl libro con el ID especificado no existe en la base de datos.")

        # Cerrar la conexión
        conn.close()

    except sqlite3.Error as e:
        print("Error al agregar el préstamo:", e)

def agregar_devolucion():
    usuario = input("Ingrese el nombre del usuario: ")
    libro_id = input("Ingrese el ID del libro prestado: ")

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()

        # Verificar el ID del préstamo en la tabla Prestamos
        c.execute("SELECT id FROM Prestamos WHERE usuario = ? AND libro_id = ?", (usuario, libro_id))
        id_prestamo = c.fetchone()

        if id_prestamo:
            id_prestamo = id_prestamo[0]

            fecha_devolucion = input("Ingrese la fecha de devolución [AAAA-MM-DD] (vacío para la fecha de hoy): ")
            if fecha_devolucion == "" or len(fecha_devolucion)!=10:
                fecha_devolucion = datetime.now().strftime('%Y-%m-%d')

            # Actualizar la tabla Prestamos con la fecha de devolución
            c.execute("UPDATE Prestamos SET fecha_devolucion = ? WHERE id = ?", (fecha_devolucion, id_prestamo))

            # Incrementar la disponibilidad del libro en la tabla Libros
            c.execute("UPDATE Libros SET disponible = disponible + 1 WHERE id = ?", (libro_id,))

            # Guardar (commit) los cambios
            conn.commit()

            print("Devolución registrada con éxito.")
        else:
            print("Error al agregar la devolución.\nNo se encontró ningún préstamo para el usuario y libro especificados.")

        # Cerrar la conexión
        conn.close()

    except sqlite3.Error as e:
        print("Error al agregar la devolución:", e)

def mostrar_prestamos():
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('biblioteca.db')
        c = conn.cursor()

        # Obtener préstamos devueltos
        c.execute("SELECT id, libro_id, usuario, fecha_prestamo, fecha_devolucion FROM Prestamos WHERE fecha_devolucion IS NOT NULL")
        prestamos_devueltos = c.fetchall()

        if prestamos_devueltos:
            print("Préstamos Devueltos:")
            print("ID     Libro ID\tUsuario\t\tF. Préstamo\tF. Devolución")
            for prestamo in prestamos_devueltos:
                print(f"{prestamo[0]}\t{prestamo[1]}\t{prestamo[2]}\t{prestamo[3]}\t{prestamo[4]}")
        else:
            print("No hay préstamos devueltos en la base de datos.")

        # Obtener préstamos pendientes de devolución
        c.execute("SELECT id, libro_id, usuario, fecha_prestamo FROM Prestamos WHERE fecha_devolucion IS NULL")
        prestamos_pendientes = c.fetchall()

        if prestamos_pendientes:
            print("\nPréstamos Pendientes de Devolución:")
            print("ID     Libro ID\tUsuario\t\tF. Préstamo")
            for prestamo in prestamos_pendientes:
                print(f"{prestamo[0]}\t{prestamo[1]}\t{prestamo[2]}\t{prestamo[3]}")
        else:
            print("\nNo hay préstamos pendientes de devolución en la base de datos.")

        # Cerrar la conexión
        conn.close()

    except sqlite3.Error as e:
        print("Error al mostrar los préstamos:", e)

# Función principal
def main():
    while True:
        limpiar_terminal()
        print("***** Bienvenido al sistema interactivo para Bibloteca *****")
        print("Menú:")
        print("1. Agregar un libro")
        print("2. Buscar un libro")
        print("3. Registrar un préstamo")
        print("4. Registrar una devolución")
        print("5. Mostrar todos los préstamos")
        print("6. Mostrar todos los libros")
        print("7. Salir")

        opcion = input("Seleccione una opción (1-7): ")
        print("\n")

        if opcion == "1":
            print(" *** AGREGANDO LIBRO *** ")
            agregar_libro()
        elif opcion == "2":
            print(" *** BUSCANDO LIBRO *** ")
            buscar_libro()
        elif opcion == "3":
            print(" *** AGREGANDO PRESTAMO *** ")
            agregar_prestamo()
            pass
        elif opcion == "4":
            print(" *** AGREGANDO DEVOLUCION *** ")
            agregar_devolucion()
            pass
        elif opcion == "5":
            print(" *** MOSTRANDO PRESTAMOS *** ")
            mostrar_prestamos()
            pass
        elif opcion == "6":
            print(" *** MOSTRANDO LIBROS *** ")
            imprimir_libros()
            pass
        elif opcion == "7":
            print(" *** SALIENDO DEL MENU *** \n")
            break
        else:
            print("Opción no válida. Seleccione una opción del 1 al 6.")
        print("\n")
        input("Presiona enter para continuar\n")
        limpiar_terminal()

if __name__ == "__main__":
    main()

NotSoSharp (nscharp) — Einfache Programmiersprache
NotSoSharp (kurz nscharp) ist eine einfache und leicht verständliche Programmiersprache für kleine Programme und Skripte. Sie hat folgende Features:

Variablen: Zahlen und Texte speichern, z.B. let name = "Maiky" oder let alter = 25

Benutzereingabe: Eingabe über input (ohne Klammern), z.B. let pw = input

Ausgabe: Text oder Variablen mit print() ausgeben, z.B. print("Hallo Welt!") oder print(name)

Bedingungen: if und else ohne runde Klammern, z.B.
if pw == "1234" {
print("Zugang erlaubt!")
} else {
print("Falsches Passwort!")
}

Schleifen: Wiederholungen mit while, z.B.
let count = 0
while count < 5 {
print(count)
let count = count + 1
}

Funktionen: Einfache Funktionen ohne Parameter, z.B.
fun greet() {
print("Hallo!")
}

Ausdrücke: Rechnen und Vergleichen mit +, -, *, /, ==, <, >

Besonderheiten sind, dass keine runden Klammern bei Bedingungen und Funktionsaufrufen verwendet werden (nur {}), input ohne Klammern genutzt wird, und Fehlermeldungen verständlich und mit Zeilennummern versehen sind.

Beispiel Passwortabfrage in nscharp:

print("Gib dein Passwort ein:")
let pw = input

print("Bitte Passwort bestätigen:")
let eingabe = input

if eingabe == pw {
print("Passwort korrekt, Zugang erlaubt!")
} else {
print("Falsches Passwort!")
}

Installation und Nutzung:

Python 3 von https://python.org installieren

Den Interpreter nscharp.py in einen Ordner (z.B. C:\Nscharp) speichern

Diesen Ordner zum System-PATH hinzufügen, damit nscharp im Terminal funktioniert

Skript mit Endung .ns schreiben, z.B. test.ns

Im Terminal mit folgendem Befehl ausführen:
nscharp test.ns

Was noch fehlt / Nicht unterstützt:

Runde Klammern () bei Bedingungen und Funktionsaufrufen (nur {} erlaubt)

Funktionen mit Parametern

Komplexe Datentypen oder Klassen

Erweiterte Features (können später ergänzt werden)

Viel Spaß mit NotSoSharp!
Erstellt von Maiky


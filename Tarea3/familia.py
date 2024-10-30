from pyswip import Prolog

# Crear instancia de Prolog
prolog = Prolog()

#mi famila materna
prolog.assertz("padre(juan, yohana)")
prolog.assertz("padre(juan, yodalis)")
prolog.assertz("padre(juan, juanantonio)")

prolog.assertz("madre(omayra, yohana)")
prolog.assertz("madre(omayra, yodalis)")
prolog.assertz("madre(omayra, juanantonio)")

# mi familia paterna
prolog.assertz("padre(clemente, clementejr)")
prolog.assertz("padre(clemente, alexander)")
prolog.assertz("padre(clemente, iris)")

prolog.assertz("madre(maria, clementejr)")
prolog.assertz("madre(maria, alexander)")
prolog.assertz("madre(maria, iris)")

# mi familia nuclear
prolog.assertz("padre(clementejr, anthony)")
prolog.assertz("padre(clementejr, adrian)")
prolog.assertz("padre(clementejr, allison)")

prolog.assertz("madre(yohana, anthony)")
prolog.assertz("madre(yohana, adrian)")
prolog.assertz("madre(yohana, allison)")

prolog.assertz("abuelo(X, Y) :- padre(X, Z), padre(Z, Y)")
prolog.assertz("abuelo(X, Y) :- padre(X, Z), madre(Z, Y)")
prolog.assertz("abuela(X, Y) :- madre(X, Z), padre(Z, Y)")
prolog.assertz("abuela(X, Y) :- madre(X, Z), madre(Z, Y)")


# Consultar abuelos de Anthony
abuelos = list(prolog.query("abuelo(X, anthony)"))
abuelas = list(prolog.query("abuela(X, anthony)"))

for resultado in abuelos:
    print(f"El abuelo de Anthony es: {resultado['X']}")

for resultado in abuelas:
    print(f"La abuela de Anthony es: {resultado['X']}")

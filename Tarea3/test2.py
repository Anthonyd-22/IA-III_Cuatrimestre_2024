from pyswip import Prolog

prolog = Prolog()

prolog.assertz("padre(juan, pedro)")
prolog.assertz("padre(juan, maria)")
prolog.assertz("padre(carlos, juan)")
prolog.assertz("padre(ana, pedro)")


prolog.assertz("abuelo(X, Y) :- padre(X, Z), padre(Z, Y)")


resultados = list(prolog.query("abuelo(X, pedro)"))

for resultado in resultados:
    print(f"El abuelo de Pedro es: {resultado['X']}")

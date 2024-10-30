from pyswip import Prolog

prolog = Prolog()

prolog.assertz("padre(clemente, anthony)")
prolog.assertz("padre(clemente, adrian)")
prolog.assertz("padre(juan, clemente)")
prolog.assertz("padre(yohana, anthony)")


prolog.assertz("abuelo(X, Y) :- padre(X, Z), padre(Z, Y)")


resultados = list(prolog.query("abuelo(X, anthony)"))

for resultado in resultados:
    print(f"El abuelo de Anthony es: {resultado['X']}")




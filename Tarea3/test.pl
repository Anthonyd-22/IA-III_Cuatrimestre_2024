%relaciones_familiares

padre(juan, pedro).
padre(juan, maria).
padre(carlos, juan).
padre(ana, pedro).

%reglas_para_definir_el_abuelo
abuelo(X, Y) :- padre(X, Z), padre(Z, Y).
def wypiszListy (lista, level):
    for eachElement in lista:
        if isinstance(eachElement, list):
            wypiszListy(eachElement, level+1)
        else:                        
             for tab_stop in range(level):
                 print("\t", end=' ')
             print(eachElement)
			


def wypiszListy (lista):
	for eachElement in lista:
		if isinstance(eachElement, list	):
			wypiszListy(eachElement)
		else:
			print(eachElement)

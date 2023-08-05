import sys

file1 = open(sys.argv[1],'r')

file1 = file1.readlines()
vals = []
for l1,l2 in zip(file1[:-1],file1[1:]):
	if l2 == 'New path!\n':
		print vals
		vals = []
	if l1 == 'New path!\n':
		vals = []
		z2 = float(l2)
		vals.append(z2)
	else:
		try:
			z2 = float(l2)
			vals.append(z2)


		except:
			continue

print vals


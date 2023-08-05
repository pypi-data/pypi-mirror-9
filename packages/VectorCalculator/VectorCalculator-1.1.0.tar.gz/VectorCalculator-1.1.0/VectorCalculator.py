#Vector Calculator
#
#Noah Rossignol
#Version 1.1

#First I will import the vector class
import Vector
def vector(x,y,z):
	return Vector.Vector(x,y,z)
        
#Now I have the vector class.  Now I make the user interface.
print('-----------------------------')
print('Vector Calculator 1.1        ')
print("Noah Rossignol 10/19/2014    ")
print("-----------------------------")
print('Enter the x, y, and z components of the first vector.')
x1 = float(raw_input("Enter the x component: "))
y1 = float(raw_input("Enter the y component: "))
z1 = float(raw_input("Enter the z component: "))
v1 = vector(x1, y1, z1)
while(True):
    print " "
    print "Enter + for addition, - for subtraction, * for scalar product, "
    print "o for dot product, or x for cross product."
    print " "
    response = raw_input("Which vector operation would you like to do? ")
    if response!='+' and response!='-' and response!='*' and response!='o' and response!='x':
		print("That is not a valid input.  Enter +, -, *, o, or x.")
    else:
        break
if response == '*':
	print " "
	num = float(raw_input("Enter the scalar factor: "))
else:
	print " "
	print "Enter the x, y, and z components of the second vector. "
	x2 = float(raw_input("Enter the x component: "))
	y2 = float(raw_input("Enter the y component: "))
	z2 = float(raw_input("Enter the z component: "))
	v2 = vector(x2, y2, z2)

if response == '+':
    v3 = v1.add(v2)
elif response == '-':
    v3 = v1.add(v2.scalarProduct(-1))
elif response == '*':
    v3 = v1.scalarProduct(num)
elif response == 'o':
    v3 = v1.dotProduct(v2)
elif response == 'x':
    v3 = v1.crossProduct(v2)
print (" ")
print ("The answer is "+str(v3)+".")

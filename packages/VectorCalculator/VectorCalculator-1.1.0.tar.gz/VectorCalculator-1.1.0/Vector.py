#Vector class
#author: Noah Rossignol
class Vector(object):
    #init method initializes the vector
    def __init__(self, i, j, k):
        self.x = i
        self.y = j
        self.z = k
    #str method to display a vector.
    def __str__(self):
        return (str(self.x)+'x + '+str(self.y)+'y + '+str(self.z)+'z')
    #accessor methods.
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    def getZ(self):
        return self.z
    
    #now the calculation methods
    def add(self, other):
        '''Takes another vector as an argument and returns another vector that
        is the vector sum of self and the other vector.'''
        a = self.x+other.x
        b = self.y+other.y
        c = self.z+other.z
        return Vector(a, b, c)
    def scalarProduct(self, n):
        a = self.x * n
        b = self.y * n
        c = self.z * n
        return Vector(a, b, c)
    def dotProduct(self, other):
        '''Similar to add, but returns the dot product rather than the sum.'''
        a=self.x*other.x
        b=self.y*other.y
        c=self.z*other.z
        return a+b+c
    def crossProduct(self, other):
        '''Returns the cross product of self and another vector.  This one is a 
        bit more work.'''
        #first do x1 cross y2 and y1 cross x2 to get the new z component.
        #remember x cross y is +z and y cross x is -z
        c = (self.x * other.y) - (self.y * other.x)
        #get new y component by doing same with x and z plane
        #z cross x is +y and x cross z is -y
        b = (self.z * other.x) - (self.x * other.z)
        #get new x component by doing same with y and z plane
        #y cross z is +x and z cross y is -x
        a = (self.y * other.z) - (self.z * other.y)
        return Vector(a, b, c)

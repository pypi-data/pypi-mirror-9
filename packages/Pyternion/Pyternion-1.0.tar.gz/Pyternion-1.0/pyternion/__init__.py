from math import sqrt, pi, asin, acos, sin, cos

def normalize_vector(vec):
   m = abs(Quaternion(0, *vec))
   return tuple([m*comp for comp in vec])

def yawpitch_from_normvector(vec):
   x, y, z = vec
   if abs(x) > abs(y):
      largeXY = x
   else:
      largeXY = y

   if largeXY == 0:
      yaw = 0
   else:
      if largeXY == x:
         yaw = acos(x)
         if y < 0:
            yaw += pi
      else:
         yaw = asin(y)
         if x < 0:
            yaw = pi-yaw

   a = x*x+y*y
   pitch = acos(a/sqrt(a))*(1 if z >= 0 else -1)

   return (yaw, pitch)

class Quaternion(object):

   def __init__(self, w, x, y, z):
      try:
         w = float(w)
         x = float(x)
         y = float(y)
         z = float(z)
      except TypeError:
         raise TypeError('Quaternion() arguments must be real numbers')
      self.w = w
      self.x = x
      self.y = y
      self.z = z

   @classmethod
   def fromaxisangle(cls, vecAxis, angle):
      return Quaternion(
         cos(angle/2.0),
         vecAxis[0]*sin(angle/2.0),
         vecAxis[1]*sin(angle/2.0),
         vecAxis[2]*sin(angle/2.0)
      )

   # TODO
   # @classmethod
   # def fromvectovec(cls, vecFrom, vecTo):
   #    x, y, z = normalize_vector(vecFrom)
   #    yaw1, pitch1 = yawpitch_from_normvector((x,y,z))
   #    q1 = Quaternion.fromaxisangle((0,1,0), pitch1)
   #    q2 = Quaternion.fromaxisangle((0,0,1), yaw1)
   #    return q2*q1
   
   def conjugate(self):
      return Quaternion(
         self.w,
         -self.x,
         -self.y,
         -self.z,
      )

   def __abs__(self):
      return sqrt(
         self.w * self.w +
         self.x * self.x +
         self.y * self.y +
         self.z * self.z
      )

   def __sub__(self, other):
      return self + other*-1

   def __add__(self, other):
      t = type(other)
      if t == Quaternion:
         return Quaternion(*[self[i]*other[i] for i in range(4)])
      elif t in (float, int, complex):
         other = complex(other)
         return Quaternion(real(other), imag(other), 0, 0) + self
      else:
         raise TypeError('Quaternions cannot be added to or subtracted from anything except complex numbers (including scalars) and other quaternions')
            
   def __repr__(self):
      return str(self)

   def __str__(self):
      return ("%g+%gi+%gj+%gk" % tuple(self)).replace('+-', '-')

   def __bool__(self):
      return abs(self) != 0

   def __gt__(self, other):
      raise TypeError('no ordering relation is defined for quaternions')

   def __gte__(self, other):
      return self.__gt__(other)

   def __lt__(self, other):
      return self.__gt__(other)

   def __lte__(self, other):
      return self.__gt__(other)

   def __getitem__(self, index):
      return (self.w, self.x, self.y, self.z)[index]

   def __iter__(self):
      yield self.w
      yield self.x
      yield self.y
      yield self.z

   def rank(self):
      return len([c for c in self if c != 0])

   def __mul__(self, other):
      t = type(other)
      if t == Quaternion:
         # quaternion * quaternion
         # Note: this is just the distributive law, taking
         # into account the following properties of hypercomplex numbers:
         #  ii = jj = kk = -1
         #  ij = k = -ji
         #  jk = i = -kj
         #  ki = j = -ik
         return Quaternion(
            self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z
            , self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y
            , self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x
            , self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w
         )
      elif t in (float, complex):
         # quaternion * scalar
         return Quaternion(*[comp*other for comp in self])
      elif t in (tuple, list) and len(other) == 3:
         # quaternion * vector
         equivalent_q = Quaternion(0, *other)
         result_q = self * equivalent_q * self.conjugate()
         return (result_q[1], result_q[2], result_q[3])
      else:
         raise TypeError('Quaternions cannot be multiplied by anything except real numbers and other quaternions')

Quaternion.i = Quaternion(0,1,0,0)
Quaternion.j = Quaternion(0,0,1,0)
Quaternion.k = Quaternion(0,0,0,1)

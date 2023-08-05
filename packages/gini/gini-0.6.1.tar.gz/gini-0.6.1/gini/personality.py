import sys,time,random
import zlib, base64, getpass, atexit

def compress(data, level=9):
	''' return compressed, ASCII-encoded string '''
	return base64.encodestring(zlib.compress(data,9))

def decompress(data):
	''' return uncompressed data '''
	return zlib.decompress(base64.decodestring(data))

typing_speed = 100 #wpm
def slow_type(t):
	for l in t:
		sys.stdout.write(l)
		sys.stdout.flush()
		time.sleep(random.random()*10.0/typing_speed)
	print ''

def display(name):
    user = getpass.getuser()
    if compress(user) in faces:
        nl.notify(decompress(faces[compress(user)][name]))

def set_goodbye():
    atexit.register(display,'goodbye')

faces = {
    'eNrLLcqvyk3MAwAMOAMF\n': {
        'greeting': 'eNplUDEKwzAM3P2KSxclBctjIS/o0B9ErSdDh0ChdNTjK9kxJalsZEln684K6MahR4mAvLMOpYSE\ng4mDXDG16FrW9YXPs7yLo+qoSkqXih7MUWM7QeB7T5uCt8XZlt2CpYqxMjoXiLNX/DTndWJQaAKF\nIuUYI2PCFHjPOjMF/fuFVrbqeBsItUjRtZteebiaHGluE3FCbTjZF6y1Sd0KEPE3AhlNRx+g9egv\nWorbgOGXYcl3qy1ZwxdvpUwA\n',
        'goodbye': 'eNp1T8sKgzAQvOcrxl5iIK73iIfe+hGChJo+IK3QSqGXfHs3aqoUO5DsZGd2lgDbKPmIjb4m+qNp\nyZesFk1rattIWpbKqFDSjIzuwIgvSZAhxey9R9ffXSYmI3Iu6rtFGZ2oSLMEqgtGTVQEUCVnw8G+\nHCxu9nw9Wo+Hew7oTxguDp19Z9MGsJsnjBm54bgdVv/LTeyOtFLrxRFNg8lOJX61OWepwAc6pzyM\n'
    },
    'eNpLSi/KLy4GAAjDApE=\n': {
        'greeting': 'eNrzSM3JyVcoyUgtStVRKM4s0gMANzUF9Q==\n',
        'goodbye': 'eNpzz89PSapM1QMADcIC+A==\n'
    }
}

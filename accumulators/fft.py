#!/usr/bin/python
from numpy import complex64
from scipy.fftpack import ifft, fft

def to_complex(arr):
	return [complex64(a) for a in arr]

def ccmult(i, j):
	return i * j.conjugate()

def pad_sim(arr, amount):
	ret = [0 for i in range(amount)]
	ret += arr 
	ret += [0 for i in range(amount)]
	return ret

def next_pow2(of):
	cur = 1
	while cur < of:
		cur *= 2

	return cur 

def pad_end(arr, amount):
	return arr + [0 for i in range(amount)]

def correlate_skip_fft(sig1, sig2):
	cnv = [ccmult(i, j) for i,j in zip(sig1_fft, sig2_fft)]
	res = fft(cnv, power_pad, -1)

def correlate_skip_ff1_onfirst(sig1_fft, sig2):

	sig2 = to_complex(sig2)

	if len(sig2) % 2 != 0:
		sig2 = pad_end(sig2, 1)

	padding = (abs(len(sig1_fft) - len(sig2)))/2
	sig2 = pad_sim(sig2, padding)

	power_pad = next_pow2(len(sig2))
	pad_toadd = power_pad - len(sig2)

	sig2 = pad_end(sig2, pad_toadd)

	sig2_fft = fft(sig2)
	cnv = [i * j.conjugate() for i,j in zip(sig1_fft, sig2_fft)]
	res = ifft(cnv)
	return res

def correlate(sig1, sig2):

	sig1 = to_complex(sig1)
	sig2 = to_complex(sig2)

	if len(sig1) % 2 != 0:
		sig1 = pad_end(sig1, 1)
	if len(sig2) % 2 != 0:
		sig2 = pad_end(sig2, 1)

	#print len(sig1), len(sig2), abs(len(sig1) - len(sig2)),
	padding = (abs(len(sig1) - len(sig2)))/2
	#print padding
	if len(sig1) < len(sig2):
		sig1 = pad_sim(sig1, padding)
	elif len(sig2) < len(sig1):
		sig2 = pad_sim(sig2, padding)

	if not len(sig1) == len(sig2):
		print len(sig1), len(sig2)
		raise ValueError()

	power_pad = next_pow2(len(sig1))
	pad_toadd = power_pad - len(sig1)

	sig1 = pad_end(sig1, pad_toadd)
	sig2 = pad_end(sig2, pad_toadd)

	sig1_fft = fft(sig1)
	sig2_fft = fft(sig2)

#	print sig1_fft, sig2_fft

	cnv = [i * j.conjugate() for i,j in zip(sig1_fft, sig2_fft)]
	res = ifft(cnv)

	return [r.real for r in res]

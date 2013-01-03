#!/usr/bin/python

import math
TWOPI = math.pi * 2

def reverse_bits(index, size):
	rev = 0
	while size > 1:
		rev = (rev << 1) | (index & 1)
		index >>= 1
		size  >>= 1
	return rev

def fft(arr, nn, isign):

	# Create bit-reversed dict for the data
	rp = {}
	for i in range(nn):
		rb = reverse_bits(i, nn)
		rp[rb] = arr[i]

	# Danielson-Lanzcos routine
	imax = 1
	istep = 2
	while imax < nn:
		istep = imax << 1
		theta = TWOPI/istep
		wtemp = math.sin(0.5*theta*isign)
		wpr = -2.0 * wtemp * wtemp
		wpi = math.sin(theta * isign)
		wr = 1.0
		wi = 0.0
		m = 0
		while m < imax: # Looping logic is correct
			i = m
			while i < nn:
				j = i+imax 
				# print m, j, i, imax, istep, nn
				tmp_re = wr * rp[j][0] - wi*rp[j][1]
				tmp_im = wr * rp[j][1] + wi*rp[j][0]
				tmp_j = (rp[i][0]-tmp_re, rp[i][1]-tmp_im)
				tmp_i = (rp[i][0]+tmp_re, rp[i][1]+tmp_im)
				rp[i] = tmp_i
				rp[j] = tmp_j
				i += istep
			wtemp = wr
			wr = wtemp * wpr - wi * wpi + wr 
			wi = wi * wpr + wtemp * wpi + wi
			m += 1
		imax = istep

	# Scale the result if taking th inverse
	if isign == -1:
		scale = 1.0/nn
		for i in rp:
			re, im = rp[i]
			re *= scale
			im *= scale 
			rp[i] = (re, im)

	return rp.values()

def ccmult(c1, c2):

	first_re, first_im = c1
	secnd_re, secnd_im = c2

	ac = first_re * secnd_re
	bd = first_im * -secnd_im

	return ac-bd, (first_re+first_im)*(secnd_re - secnd_im) - ac - bd 

def cnv_complex(real):
	return real, 0

def pad_sim(arr, amount):
	ret = [(0, 0) for i in range(amount)]
	ret += arr 
	ret += [(0, 0) for i in range(amount)]
	return ret

def next_pow2(of):
	cur = 1
	while cur < of:
		cur *= 2

	return cur 

def pad_end(arr, amount):
	return arr + [(0, 0) for i in range(amount)]

def correlate_skip_fft(sig1, sig2):
	cnv = [ccmult(i, j) for i,j in zip(sig1_fft, sig2_fft)]
	res = fft(cnv, power_pad, -1)

def correlate_skip_ff1_onfirst(sig1_fft, sig2):

	sig2 = [cnv_complex(i) for i in sig2]

	if len(sig2) % 2 != 0:
		sig2 = pad_end(sig2, 1)

	padding = (abs(len(sig1_fft) - len(sig2)))/2
	sig2 = pad_sim(sig2, padding)

	power_pad = next_pow2(len(sig2))
	pad_toadd = power_pad - len(sig2)

	sig2 = pad_end(sig2, pad_toadd)

	sig2_fft = fft(sig2, power_pad, 1)
	cnv = [ccmult(i, j) for i,j in zip(sig1_fft, sig2_fft)]
	res = fft(cnv, power_pad, -1)
	return res

def correlate(sig1, sig2):

	sig1 = [cnv_complex(i) for i in sig1]
	sig2 = [cnv_complex(i) for i in sig2]

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

	sig1_fft = fft(sig1, power_pad, 1)
	sig2_fft = fft(sig2, power_pad, 1)

#	print sig1_fft, sig2_fft

	cnv = [ccmult(i, j) for i,j in zip(sig1_fft, sig2_fft)]
	res = fft(cnv, power_pad, -1)

	return res 

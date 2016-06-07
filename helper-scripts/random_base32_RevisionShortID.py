#!/usr/bin/env python
# This is a one-time use script used to generate the random letter-num sequence
# that we use to map base 32 numbers to letters.

import random

#It is important that we at least remember this seed so that we can
#reduplicate our randomized letter-num sequence in case it is ever forgotten.
random.seed(332211)

#We removed the following characters to improve readability for short urls:
#o, 0 and l, and 1. (26+10) = 36-4 = 32 characters left.
initial_seq = '23456789abcdefghijkmnpqrstuvwxyz'

temp = list(initial_seq)
random.shuffle(temp)

final_seq = ''.join(temp)
print final_seq

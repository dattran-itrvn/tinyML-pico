import cmsisdsp
import numpy as np

def convu(h_q15, x_q15, n, k):
    if n - k >= 0:
        return cmsisdsp.arm_mult_q15([h_q15[k], 0], [x_q15[n - k], 0])
    else:
        return cmsisdsp.arm_float_to_q15([0, 0])

def arm_filter(b, a, x, mode='f32', modert='f32'):
    if mode=='f32':
        for i in range(len(b)):
            b[i] /= a[0]
        for i in range(len(a)):
            if i == 0:
                continue
            a[i] /= -a[0]
        a[0] = -1
        x_q15 = cmsisdsp.arm_float_to_q15(x)
        b_q15 = cmsisdsp.arm_float_to_q15(b)
        a_q15 = cmsisdsp.arm_float_to_q15(a)
    if mode == 'q15':
        x_q15 = x
        b_q15 = b
        a_q15 = a
    y = np.zeros(len(x))
    y_q15 = cmsisdsp.arm_float_to_q15(y)
    for n in range(len(y)):
        for k in range(len(b)):
            y_q15[n] = cmsisdsp.arm_add_q15([y_q15[n], 0], convu(b_q15, x_q15, n, k))[0]
        for k in range(len(a)):
            if k == 0:
                continue
            y_q15[n] = cmsisdsp.arm_add_q15([y_q15[n], 0], convu(a_q15, y_q15, n, k))[0]
    if modert=='f32':
        return cmsisdsp.arm_q15_to_float(y_q15)
    if modert=='q15':
        return y_q15


# b = [0.24, 0.2, 0.3, 0.5][::-1]
# a = [0.2, 0.23, 0.32, 0.5][::-1]
# x = [1 / 20, 2 / 20, 3 / 20, 4 / 20, 5 / 20, 6 / 20, 7 / 20, 8 / 20, 9 / 20, 10 / 20]

# print(arm_filter(b,a,x,'f32','q15'))
import Quantum_computer
low_bit = [
[1,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,0],
[0,1,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,0],
[0,0,1,0,  0,0,0,0,  0,0,0,0,  0,0,0,0],
[0,0,0,1,  0,0,0,0,  0,0,0,0,  0,0,0,0],

[0,0,0,0,  0,0,0,1,  0,0,0,0,  0,0,0,0],
[0,0,0,0,  1,0,0,0,  0,0,0,0,  0,0,0,0],
[0,0,0,0,  0,1,0,0,  0,0,0,0,  0,0,0,0],
[0,0,0,0,  0,0,1,0,  0,0,0,0,  0,0,0,0],

[0,0,0,0,  0,0,0,0,  1,0,0,0,  0,0,0,0],
[0,0,0,0,  0,0,0,0,  0,1,0,0,  0,0,0,0],
[0,0,0,0,  0,0,0,0,  0,0,1,0,  0,0,0,0],
[0,0,0,0,  0,0,0,0,  0,0,0,1,  0,0,0,0],

[0,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,1],
[0,0,0,0,  0,0,0,0,  0,0,0,0,  1,0,0,0],
[0,0,0,0,  0,0,0,0,  0,0,0,0,  0,1,0,0],
[0,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,1,0]
]



high_bit = [
[1,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,0],
[0,1,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,0],
[0,0,1,0,  0,0,0,0,  0,0,0,0,  0,0,0,0],
[0,0,0,1,  0,0,0,0,  0,0,0,0,  0,0,0,0],

[0,0,0,0,  1,0,0,0,  0,0,0,0,  0,0,0,0],
[0,0,0,0,  0,1,0,0,  0,0,0,0,  0,0,0,0],
[0,0,0,0,  0,0,1,0,  0,0,0,0,  0,0,0,0],
[0,0,0,0,  0,0,0,1,  0,0,0,0,  0,0,0,0],

[0,0,0,0,  0,0,0,0,  0,0,1,0,  0,0,0,0],
[0,0,0,0,  0,0,0,0,  0,0,0,1,  0,0,0,0],
[0,0,0,0,  0,0,0,0,  1,0,0,0,  0,0,0,0],
[0,0,0,0,  0,0,0,0,  0,1,0,0,  0,0,0,0],

[0,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,1,0],
[0,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,1],
[0,0,0,0,  0,0,0,0,  0,0,0,0,  1,0,0,0],
[0,0,0,0,  0,0,0,0,  0,0,0,0,  0,1,0,0]
]

adder = Quantum_computer.matrix_product(high_bit,low_bit)

register = Quantum_computer.Qubit_system(4,{13:1})
register.multi_qubit_op(adder,0)
print register.measure()
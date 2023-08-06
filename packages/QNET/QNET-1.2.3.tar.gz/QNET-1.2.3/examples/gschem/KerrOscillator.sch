v 20110115 2
C 15300 69400 1 180 0 phase-1.sym
{
T 14305 67905 5 8 0 0 180 0 1
device=Phase
T 13897 69415 5 8 1 1 180 0 1
refdes=P2
T 13500 69600 5 10 1 0 0 0 1
phi=phi_2
}
C 18500 69400 1 180 0 phase-1.sym
{
T 17505 67905 5 8 0 0 180 0 1
device=Phase
T 17097 69415 5 8 1 1 180 0 1
refdes=P1
T 16700 69600 5 10 1 0 0 0 1
phi=phi_1
}
C 10600 68700 1 0 0 output-1.sym
{
T 10600 69600 5 10 0 0 0 0 1
device=OPAD
T 10100 69000 5 10 1 1 0 0 1
refdes=Out2
T 10100 69300 5 10 1 0 0 0 1
pinseq=o2
}
C 20200 68500 1 180 0 output-1.sym
{
T 20200 67600 5 10 0 0 180 0 1
device=OPAD
T 20900 68400 5 10 1 1 180 0 1
refdes=Out1
T 20900 68100 5 10 1 0 180 0 1
pinseq=o1
}
C 10600 68100 1 0 0 input-1.sym
{
T 10600 69000 5 10 0 0 0 0 1
device=IPAD
T 10200 67900 5 10 1 1 0 0 1
refdes=In1
T 10100 68200 5 10 1 0 0 0 1
pinseq=i1
}
C 20200 69100 1 180 0 input-1.sym
{
T 20200 68200 5 10 0 0 180 0 1
device=IPAD
T 20800 69200 5 10 1 1 180 0 1
refdes=In2
T 20900 69000 5 10 1 0 180 0 1
pinseq=i2
}
C 10900 67600 1 0 0 three_port_kerr_cavity-3.sym
{
T 11195 69895 5 8 0 0 0 0 1
device=ThreePortKerrCavity
T 12100 69100 5 8 1 1 0 0 1
refdes=K1
T 10900 67200 5 10 1 0 0 0 1
kappa_1=kappa
T 10900 67000 5 10 1 0 0 0 1
kappa_2=kappa
T 10900 66800 5 10 1 0 0 0 1
kappa_3=eta
T 10900 66300 5 10 1 0 0 0 1
chi=chi
T 10900 66500 5 10 1 0 0 0 1
Delta=Delta
}
C 14100 67600 1 0 0 three_port_kerr_cavity-3.sym
{
T 14395 69895 5 8 0 0 0 0 1
device=ThreePortKerrCavity
T 15300 69100 5 8 1 1 0 0 1
refdes=KC
T 14800 66800 5 10 1 0 0 0 1
kappa_3=eta
T 14800 67000 5 10 1 0 0 0 1
kappa_2=gamma
T 14800 67200 5 10 1 0 0 0 1
kappa_1=gamma
T 14800 66500 5 10 1 0 0 0 1
Delta=delta
T 14800 66300 5 10 1 0 0 0 1
chi=chi_C
}
C 17300 67600 1 0 0 three_port_kerr_cavity-3.sym
{
T 17595 69895 5 8 0 0 0 0 1
device=ThreePortKerrCavity
T 18500 69100 5 8 1 1 0 0 1
refdes=K2
T 18100 67200 5 10 1 0 0 0 1
kappa_1=kappa
T 18100 67000 5 10 1 0 0 0 1
kappa_2=kappa
T 18100 66800 5 10 1 0 0 0 1
kappa_3=eta
T 18100 66300 5 10 1 0 0 0 1
chi=chi
T 18100 66500 5 10 1 0 0 0 1
Delta=Delta
}
N 17900 68300 16100 68300 4
N 16400 68900 16100 68900 4
N 14700 68300 12900 68300 4
N 13200 68900 12900 68900 4
N 14400 68900 14700 68900 4
N 17900 68900 17600 68900 4
T 10600 70300 8 10 1 0 0 0 1
params=Delta:real;chi:real;kappa:real;gamma:real;eta:real;delta:real;chi_C:real:0;phi_1:real:3.14159265359; phi_2:real:-3.14159265359
T 10600 70500 8 10 1 0 0 0 1
module-name=KerrOscillator

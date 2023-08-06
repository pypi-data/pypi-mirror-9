v 20110115 2
C 18800 62800 1 0 0 kerr_oscillator_2-1.sym
{
T 18995 65095 5 8 0 0 0 0 1
device=KerrOscillator2
T 20500 64500 5 8 1 1 0 0 1
refdes=OSC
T 19900 65900 5 10 1 0 0 0 1
Delta=Delta
T 19900 65300 5 10 1 0 0 0 1
chi=chi
T 19900 66100 5 10 1 0 0 0 1
kappa=kappa
T 19900 65500 5 10 1 0 0 0 1
eta=eta
T 19900 65700 5 10 1 0 0 0 1
gamma=gamma
T 19900 65100 5 10 1 0 0 0 1
chi_C=chi_C
T 19900 64900 5 10 1 0 0 0 1
delta=delta
T 19900 64800 5 10 1 0 0 0 1
phi_1=phi_1
T 19900 64600 5 10 1 0 0 0 1
phi_2=phi_2
}
C 24300 64800 1 180 1 three_port_kerr_cavity-3.sym
{
T 24595 62505 5 8 0 0 180 6 1
device=ThreePortKerrCavity
T 25400 64400 5 8 1 1 180 6 1
refdes=Filter
T 24700 65600 5 10 1 0 0 0 1
kappa_1=kappa_F
T 24700 65400 5 10 1 0 0 0 1
kappa_2=gamma_F
T 24700 65200 5 10 1 0 0 0 1
kappa_3=eta_F
T 24700 64800 5 10 1 0 0 0 1
chi=0
T 24700 65000 5 10 1 0 0 0 1
Delta=Delta_F
}
N 24900 64100 22500 64100 4
C 28000 64300 1 180 0 output-1.sym
{
T 28000 63400 5 10 0 0 180 0 1
device=OPAD
T 28000 64100 5 10 1 1 0 0 1
refdes=sb_ref
T 28000 64300 5 10 1 0 0 0 1
pinseq=o1
}
C 24300 63500 1 180 0 kerr_amplifier-1.sym
{
T 23505 60905 5 8 0 0 180 0 1
device=KerrAmplifier
T 21900 61600 5 10 1 0 0 0 1
Delta=Delta_A
T 21900 61000 5 10 1 0 0 0 1
chi=chi_A
T 21900 61400 5 10 1 0 0 0 1
kappa=kappa_A
T 21900 61200 5 10 1 0 0 0 1
eta=eta_A
T 22500 62700 5 10 1 1 180 0 1
refdes=A
}
N 23500 62800 24900 62800 4
C 21700 63000 1 180 0 phase-1.sym
{
T 20705 61505 5 8 0 0 180 0 1
device=Phase
T 20297 62115 5 8 1 1 180 0 1
refdes=P
T 19900 62800 5 10 1 0 0 0 1
phi=phi
}
C 17900 63300 1 0 0 input-1.sym
{
T 17900 64200 5 10 0 0 0 0 1
device=IPAD
T 18200 63700 5 10 1 1 0 0 1
refdes=bias
T 18200 63900 5 10 1 0 0 0 1
pinseq=i1
}
N 19600 62500 18800 62500 4
N 18800 62500 18800 63200 4
N 18800 63500 19000 63500 4
C 24500 62700 1 180 0 input-1.sym
{
T 24500 61800 5 10 0 0 180 0 1
device=IPAD
T 24500 62200 5 10 1 1 0 0 1
refdes=sig
T 24500 62400 5 10 1 0 0 0 1
pinseq=i2
}
N 18800 63200 19000 63200 4
N 23600 62500 23500 62500 4
T 17500 66400 8 10 1 1 0 0 1
params=kappa:real;Delta:real;delta:real;gamma:real;eta:real;chi:real;chi_C:real;phi_1:real:3.14159265359;phi_2:real:-3.14159265359;kappa_F:real;gamma_F:real;eta_F:real;Delta_F:real;Delta_A:real;kappa_A:real;chi_A:real;phi:real;eta_A:real
N 20800 62500 21300 62500 4
T 19500 66800 8 10 1 1 0 0 1
module-name=PhaseLock
N 27100 64100 26300 64100 4
N 24900 63500 24900 62800 4

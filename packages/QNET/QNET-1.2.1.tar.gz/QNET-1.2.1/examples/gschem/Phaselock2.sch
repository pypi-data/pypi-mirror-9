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
phi_1=phi_1
T 19900 64700 5 10 1 0 0 0 1
phi_2=phi_2
T 19900 64500 5 10 1 0 0 0 1
delta=delta
}
C 23300 64800 1 180 1 three_port_kerr_cavity-3.sym
{
T 23595 62505 5 8 0 0 180 6 1
device=ThreePortKerrCavity
T 24400 64400 5 8 1 1 180 6 1
refdes=Filter
T 24300 65600 5 10 1 0 0 0 1
kappa_1=kappa_F
T 24300 65400 5 10 1 0 0 0 1
kappa_2=gamma_F
T 24300 65200 5 10 1 0 0 0 1
kappa_3=eta_F
T 24300 64800 5 10 1 0 0 0 1
chi=chi_F
T 24300 65000 5 10 1 0 0 0 1
Delta=Delta_F
}
N 23900 64100 22500 64100 4
C 26600 64300 1 180 0 output-1.sym
{
T 26600 63400 5 10 0 0 180 0 1
device=OPAD
T 26600 64100 5 10 1 1 0 0 1
refdes=sb_ref
T 26600 64300 5 10 1 0 0 0 1
pinseq=o2
}
N 21900 62500 23000 62500 4
C 22800 63000 1 180 0 phase-1.sym
{
T 21805 61505 5 8 0 0 180 0 1
device=Phase
T 21397 62115 5 8 1 1 180 0 1
refdes=P
T 21000 62800 5 10 1 0 0 0 1
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
N 20700 62500 18800 62500 4
N 18800 62500 18800 63200 4
N 18800 63500 19000 63500 4
C 26600 63700 1 180 0 input-1.sym
{
T 26600 62800 5 10 0 0 180 0 1
device=IPAD
T 26600 63200 5 10 1 1 0 0 1
refdes=sig
T 26600 63400 5 10 1 0 0 0 1
pinseq=i2
}
N 23000 62500 23000 63500 4
N 23000 63500 23900 63500 4
N 18800 63200 19000 63200 4
T 17500 66400 8 10 1 1 0 0 1
params=kappa:real;Delta:real;delta:real;gamma:real;eta:real;chi:real;chi_C:real;kappa_F:real;gamma_F:real;eta_F:real;Delta_F:real;chi_F:real;phi:real;phi_1:real:3.14159265359;phi_2:real:-3.14159265359
T 18600 67400 8 10 1 1 0 0 1
module-name=PhaseLock2
C 23500 64600 1 180 0 output-1.sym
{
T 23500 63700 5 10 0 0 180 0 1
device=OPAD
T 22700 64800 5 10 1 1 0 0 1
refdes=common_out
T 22700 65000 5 10 1 0 0 0 1
pinseq=o1
}
N 22600 64400 22500 64400 4
N 25300 64100 25700 64100 4
N 25300 63500 25700 63500 4

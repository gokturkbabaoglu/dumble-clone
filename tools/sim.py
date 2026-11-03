import numpy as np
f=np.array([82,150,300,500,700,1000,1500,2500,4000,6000])
w=2*np.pi*f; j=1j
par=lambda a,b:a*b/(a+b)
gm=1/322; Rd=2000; Rs=1000
def jfet(mode):
    if mode=='dark': Zb=1/(j*w*10e-6)
    elif mode=='bright': Zb=1/(j*w*10e-6)+par(500,1/(j*w*100e-9))
    elif mode=='old': Zb=1/(j*w*100e-9)
    Zs=par(Rs,Zb); return gm*Rd/(1+gm*Zs)
def db(x): return 20*np.log10(abs(x))
print('f   ',f)
for m in ['dark','bright','old']: print(m.ljust(7),np.round(db(jfet(m)),1))
# bridged-T shape network: source Rsrc=2k, C7 100n series, bridged T (C,C series, Rb across, Rg from mid to gnd), load RL
def shape(Rb,C,Rg,RL=50e3,Rsrc=2000):
    Zc=1/(j*w*C); Zsrc=Rsrc+1/(j*w*100e-9)
    # nodal: nodes A(in of T), M(mid), B(out). source V=1 through Zsrc into A
    out=[]
    for k in range(len(f)):
        zc=Zc[k]
        Y=np.array([[1/Zsrc[k]+1/zc+1/Rb, -1/zc, -1/Rb],
                    [-1/zc, 2/zc+1/Rg, -1/zc],
                    [-1/Rb, -1/zc, 1/zc+1/Rb+1/RL]],dtype=complex)
        I=np.array([1/Zsrc[k],0,0]); V=np.linalg.solve(Y,I); out.append(V[2])
    return np.array(out)
def ref(RL=50e3,Rsrc=2000):
    Zsrc=Rsrc+1/(j*w*100e-9); return RL/(RL+Zsrc)
for Rb,C,P in [(22e3,22e-9,22e3),(47e3,22e-9,22e3),(22e3,47e-9,22e3),(10e3,47e-9,22e3),(47e3,22e-9,10e3),(100e3,22e-9,20e3)]:
    print(f'\nRb={Rb/1e3:.0f}k C={C*1e9:.0f}n pot={P/1e3:.0f}k (+1k min)')
    for frac in [0,0.25,0.5,1.0]:
        Rg=1000+P*frac
        print(f'  pot {frac:4}:',np.round(db(shape(Rb,C,Rg)/ref()),1))
print('\n=== Rg sweep')
for Rb,C in [(10e3,47e-9),(4.7e3,47e-9),(10e3,22e-9),(5e3,94e-9)]:
    print(f'Rb={Rb/1e3}k C={C*1e9:.0f}n')
    for Rg in [1e3,2e3,4e3,8e3,20e3,60e3,200e3,500e3]:
        for RL in [50e3]:
            print(f'  Rg={Rg/1e3:5.0f}k',np.round(db(shape(Rb,C,Rg,RL)/ref(RL)),1))
print('\n=== crossfade: pot P between A (T input) and B (T output), wiper -> load')
def xf(Rb,C,Rg,P,a,RL=50e3,Rsrc=2000):
    # a: 0 = wiper at B (notched), 1 = wiper at A (flat)
    Zc=1/(j*w*C); Zsrc=Rsrc+1/(j*w*100e-9); out=[]
    Ra=P*(1-a)+1e-3; Rbw=P*a+1e-3   # A-wiper, wiper-B
    for k in range(len(f)):
        zc=Zc[k]
        # nodes A,M,B,W
        Y=np.zeros((4,4),dtype=complex)
        def add(n1,n2,z):
            y=1/z
            if n1>=0: Y[n1,n1]+=y
            if n2>=0: Y[n2,n2]+=y
            if n1>=0 and n2>=0: Y[n1,n2]-=y; Y[n2,n1]-=y
        add(0,-1,Zsrc[k]); add(0,1,zc); add(1,2,zc); add(0,2,Rb); add(1,-1,Rg); add(0,3,Ra); add(3,2,Rbw); add(3,-1,RL)
        I=np.array([1/Zsrc[k],0,0,0]); V=np.linalg.solve(Y,I); out.append(V[3])
    return np.array(out)
for Rb,C,Rg,P in [(10e3,47e-9,2e3,500e3),(10e3,47e-9,2e3,22e3),(10e3,47e-9,1.5e3,22e3),(10e3,22e-9,1e3,22e3)]:
    print(f'Rb={Rb/1e3}k C={C*1e9:.0f}n Rg={Rg/1e3}k P={P/1e3:.0f}k')
    for a in [0,0.25,0.5,0.75,1]:
        print(f'  a={a:4}',np.round(db(xf(Rb,C,Rg,P,a)/ref()),1))

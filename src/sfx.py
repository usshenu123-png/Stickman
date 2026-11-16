import numpy as np, wave
sr=44100; dur=26.2; N=int(sr*dur); out=np.zeros(N)
rs=np.random.RandomState(1)
def add(t,x,g=1.0):
    i=int(t*sr); x=x[:max(0,N-i)]; out[i:i+len(x)]+=x*g
def env(n,a=.005,d=.2):
    t=np.arange(n)/sr; return np.minimum(t/a,1)*np.exp(-t/d)
def lp(x,k):
    return np.convolve(x,np.ones(k)/k,mode='same')
def whoosh(l=.35):
    n=int(sr*l); t=np.arange(n)/sr; nz=rs.randn(n)
    sw=np.sin(np.pi*t/l)**2
    x=lp(nz,6)*sw; x=x-lp(x,200)  # highpass-ish
    return x*.5
def impact(l=.5,f=70):
    n=int(sr*l); t=np.arange(n)/sr
    k=np.sin(2*np.pi*(f+160*np.exp(-t*22))*t)*np.exp(-t/.18)
    nz=lp(rs.randn(n),3)*np.exp(-t/.06)*.5
    return k*.9+nz
def pop(f=600,l=.12):
    n=int(sr*l);t=np.arange(n)/sr
    return np.sin(2*np.pi*(f*np.exp(-t*18)+200)*t)*np.exp(-t/.04)*.6
def splat(l=.35):
    n=int(sr*l);t=np.arange(n)/sr
    return lp(rs.randn(n),30)*np.exp(-t/.1)*1.4+np.sin(2*np.pi*90*t)*np.exp(-t/.1)*.5
def gulp():
    n=int(sr*.3);t=np.arange(n)/sr
    return np.sin(2*np.pi*(300-500*t)*t)*np.exp(-t/.12)*.7
def zap(l=.25):
    n=int(sr*l);t=np.arange(n)/sr
    return np.sign(np.sin(2*np.pi*(1200*np.exp(-t*8))*t))*np.exp(-t/.08)*.25
for t in [0.81,3.88,6.69,10.82,12.97,15.68,19.47,20.30,23.58]:
    add(t-.28,whoosh(.3),.7)
for t,g in [(0.435,1),(3.125,1),(5.77,1),(8.585,.8),(9.955,.8),(14.245,1),(19.74,.8),(22.5,1.2),(25.4,1.3),(0.81,.7),(3.88,.7),(23.58,.7),(21.715,.8),(19.47,.6)]:
    add(t,impact(),g*.8)
add(19.025,splat(),1.0); add(19.025,impact(.4,55),.8)
add(2.45,gulp(),1.0); add(7.6,splat(.3),.8)
for i,t in enumerate(np.arange(11.05,12.3,.17)): add(t,pop(500+i*60),.8)
for i in range(9): add(20.4+i*.35,pop(900),.35)
# swoosh through intestine (rising noise)
n=int(sr*3.3);tt=np.arange(n)/sr;x=lp(rs.randn(n),8)*(tt/3.3)**2*.25; add(15.68,x,1)
add(18.9,zap(.3),1)
# music: 140 bpm
bpm=140; beat=60/bpm; mus=np.zeros(N)
def mad(t,x,g):
    i=int(t*sr);x=x[:max(0,N-i)];mus[i:i+len(x)]+=x*g
kick=impact(.3,50)*.9
hat=lp(rs.randn(int(sr*.05)),2)*np.exp(-np.arange(int(sr*.05))/sr/.012); hat=hat-lp(hat,8)
notes=[55,55,65.4,49]  # A1 A1 C2 G1
b=0
while b*beat<dur:
    t=b*beat; mad(t,kick,.5)
    mad(t+beat/2,hat,.35)
    f=notes[(b//4)%4]*(2 if b%2 else 1)
    n=int(sr*beat*.9);tt=np.arange(n)/sr
    mad(t,np.sign(np.sin(2*np.pi*f*tt))*np.exp(-tt/.2)*.18,1)
    b+=1
vo=wave.open('vo.wav');v=np.frombuffer(vo.readframes(vo.getnframes()),dtype=np.int16)
# music ducked a bit (constant), sfx mixed; save stems
def norm(x,p): return x/ (np.max(np.abs(x))+1e-9)*p
sfx=norm(out,.8); mus=norm(mus,.35)
mix=np.clip(sfx*.9+mus*.5,-1,1)
w=wave.open('fx.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((mix*32767).astype(np.int16).tobytes());w.close()
print('ok')

import numpy as np, json, wave
w=wave.open('vo.wav'); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(float)/32768
dur=len(x)/sr
# envelope 200Hz
hop=sr//200; n=len(x)//hop
env=np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop+hop]**2)) for i in range(n)])
def sm(a,k): return np.convolve(a,np.ones(k)/k,mode='same')
envs=sm(env,5)
segs=[
(0.0,0.64,[("WHAT",1),("THE",1),("FUCK",1)]),
(0.81,3.41,[("HAPPENS",2),("WHEN",1),("YOU",1),("SWALLOW",2),("CHEWING",2),("GUM?!",1)]),
(3.88,5.61,[("Well,",1),("congratulations,",4)]),
(5.77,6.39,[("dumbass.",2)]),
(6.69,10.42,[("Your",1),("stomach",2),("just",1),("received",2),("a",1),("piece",1),("of",1),("rubber",2),("it",1),("can't",1),("properly",3),("digest.",2)]),
(10.82,12.73,[("Your",1),("stomach",2),("breaks",1),("down",1),("the",1),("food",1),("around",2),("it,",1)]),
(12.97,15.29,[("but",1),("the",1),("gum",1),("base",1),("mostly",2),("survives",2),("the",1),("journey.",2)]),
(15.68,19.15,[("It",1),("travels",2),("through",1),("your",1),("intestines",3),("and",1),("eventually",4),("comes",1),("out",1),("in",1),("your",1),("shit.",1)]),
(19.47,20.11,[("And",1),("no,",1)]),
(20.30,22.32,[("it",1),("doesn't",2),("stay",1),("inside",2),("you",1),("for",1),("seven",2),("fucking",2)]),
(22.50,23.32,[("years.",1)]),
(23.58,25.94,[("Your",1),("stomach",2),("isn't",2),("a",1),("goddamn",2),("storage",2),("facility!",3)]),
]
words=[]
for s,e,ws in segs:
    tot=sum(w for _,w in ws); t=s; bounds=[s]
    c=0
    for _,wt in ws[:-1]:
        c+=wt; b=s+(e-s)*c/tot
        # snap to valley within ±0.07
        i0=int((b-0.07)*200); i1=int((b+0.07)*200)
        j=i0+int(np.argmin(envs[i0:i1+1])); b=j/200
        bounds.append(b)
    bounds.append(e)
    for k,(wd,_) in enumerate(ws):
        words.append(dict(w=wd,s=round(bounds[k],3),e=round(bounds[k+1],3)))
fps=30; nf=int(np.ceil(dur*fps))
mouth=[]
mx=np.percentile(envs,97)
for f in range(nf):
    t=f/fps; i0=int(t*200); i1=int((t+1/fps)*200)+1
    mouth.append(float(min(1,np.mean(envs[i0:i1])/mx)))
json.dump(dict(dur=dur,words=words,mouth=mouth,fps=fps),open('timing.json','w'))
print(dur,nf,len(words)); print([ (w['w'],w['s']) for w in words][:12])

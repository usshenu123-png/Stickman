const {chromium}=require('playwright');
(async()=>{
  const times=process.argv.slice(2).map(Number);
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('console',m=>console.log('console:',m.text()));p.on('pageerror',e=>console.log('PAGEERR',e.message));
  await p.goto('file://'+process.cwd()+'/index.html');
  await p.waitForFunction('window.READY===true',null,{timeout:30000});
  for(const t of times){const t0=Date.now();
    await p.evaluate(f=>window.renderFrame(f),Math.round(t*30));
    await p.screenshot({path:`prev_${String(t).replace('.','_')}.jpg`,type:'jpeg',quality:85});
    console.log(t,Date.now()-t0,'ms');}
  await b.close();
})();

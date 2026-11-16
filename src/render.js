const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{
  const N=784;
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','silent.mp4'],{stdio:['pipe','inherit','inherit']});
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>console.log('PAGEERR',e.message));
  await p.goto('file://'+process.cwd()+'/index.html');
  await p.waitForFunction('window.READY===true',null,{timeout:30000});
  for(let f=0;f<N;f++){
    await p.evaluate(x=>window.renderFrame(x),f);
    const buf=await p.screenshot({type:'jpeg',quality:93});
    if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));
    if(f%100==0)console.log('frame',f);
  }
  ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done');
})();

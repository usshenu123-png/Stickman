const {chromium}=require('playwright');
(async()=>{
  const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>console.log('PAGEERR',e.message));
  await p.goto('file://'+process.cwd()+'/index.html');
  await p.waitForFunction('window.READY===true',null,{timeout:30000});
  await p.evaluate(()=>{
    SC.forEach(s=>s.g.visible=false);
    renderer.setSize(1080,1080);cam.aspect=1;
    document.getElementById('cap').innerHTML='';document.getElementById('flash').style.opacity=0;
    document.getElementById('vig').style.display='none';
    const g=new THREE.Group();scene.add(g);
    g.add(backdrop('#ffe03a','#ffb800',22,-8,60));
    const man=makeMan();g.add(man);
    man.pose({hip:[0,1.02,0],lean:0,handL:[-1.0,1.9,.4],handR:[1.0,1.9,.4],footL:[-.26,0,0],footR:[.26,0,0],
      head:[.12,0,-.1],mouth:.75,mouthW:1.15,eyeSize:1.25,eyeOpen:.8,angry:1,browY:.0,look:[0,-.1]});
    // fist shake: show clenched hands near shoulders
    rim1.color.setHex(0xff3300);rim2.color.setHex(0xffffff);
    cam.position.set(0,2.05,4.1);cam.lookAt(0,1.95,0);cam.fov=40;cam.updateProjectionMatrix();
    scene.background=new THREE.Color(0xffc800);scene.fog=null;camLight.intensity=0;
    renderer.render(scene,cam);
  });
  const c=await p.$('canvas');
  await c.screenshot({path:'pfp.png',type:'png'});
  await b.close();
})();

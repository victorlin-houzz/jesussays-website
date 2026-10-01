// Fluid equations and framebuffer approach adapted from Pavel Dobryakov, MIT.
// Attribution: LICENSE.webgl-fluid.txt. Rendering, pigment, controls and bridge adapted for Still Waters.
/*
 * Still Waters: local, pigment-on-paper GPU fluid canvas.
 * Fluid projection and framebuffer patterns adapted from WebGL Fluid Simulation
 * Copyright (c) 2017 Pavel Dobryakov (MIT; see LICENSE.webgl-fluid.txt).
 * No remote resources, analytics, or generated image sprites.
 */
(() => {
  'use strict';
  const canvas = document.getElementById('water');
  const events = [];
  const emit = (event, details = {}) => {
    const message = { event, ...details };
    events.push(message);
    if (events.length > 40) events.shift();
    window.webkit?.messageHandlers?.stillWaters?.postMessage(message);
  };
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const state = {
    playing: false, active: true, reducedMotion: false, disposed: false,
    ink: 1, rotate: false, time: 0, frames: 0, drops: 0, washes: 0, fps: 0,
    quietTop: 0, quietBottom: 0, quietEnabled: false,
    // Defaults mirror AppTheme. Flutter sends the canonical values on ready.
    paper: [250 / 255, 248 / 255, 243 / 255],
    palette: [[26, 26, 26], [29, 54, 105], [185, 58, 43], [47, 93, 73]].map(c => c.map(v => v / 255)),
  };
  let gl, programs, velocity, pigment, pressure, divergence, curl, forward, reverse;
  let diagnosticTarget, paperTexture, vertexBuffer, animation = 0, lastFrame = 0, lastInput = -65;
  let washLeft = 0, autoElapsed = 0, autoStroke = null, autoIndex = 0;
  let frameTimes = [], lastMetrics = 0, lastDropTime = -100;
  const pointers = new Map();
  const resources = { shaders: [], programs: [], targets: [] };
  const SIM_SHORT = 192;
  const DYE_SHORT = 768;
  // A ~5-second half-life leaves time for curls, then makes room for new ink.
  // This is elapsed-time decay, including on devices drawing below 30 fps.
  const INK_FADE = Math.LN2 / 5;
  // A tap blooms over BLOOM_SECONDS instead of appearing all at once.
  const BLOOM_SECONDS = .65;
  const blooms = [];
  const VERTEX = `#version 300 es
    precision highp float;
    layout(location=0) in vec2 position;
    out vec2 uv;
    void main(){uv=position*.5+.5;gl_Position=vec4(position,0.,1.);}`;
  const HEAD = `#version 300 es
    precision highp float;
    precision highp sampler2D;
    in vec2 uv; out vec4 result;
    uniform vec2 texel;
  `;
  const NOISE = `
    float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
    float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
      return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
    float fbm(vec2 p){return .57*noise(p)+.28*noise(p*2.03+7.1)+.15*noise(p*4.07+19.3);}
  `;
  const SHADERS = {
    copy: `uniform sampler2D source; uniform float scale;
      void main(){result=texture(source,uv)*scale;}`,
    advect: `uniform sampler2D source, velocity; uniform float dt, decay;
      void main(){vec2 p=uv-dt*texture(velocity,uv).xy*texel;
        result=texture(source,p)*exp(-decay*abs(dt));}`,
    correct: `uniform sampler2D source, velocity, forwardField, reverseField;
      uniform vec2 dyeTexel; uniform float dt, fadeDt, decay;
      void main(){
        vec2 departure=uv-dt*texture(velocity,uv).xy*texel;
        vec2 grid=(floor(departure/dyeTexel-.5)+.5)*dyeTexel;
        vec4 a=texture(source,grid),b=texture(source,grid+vec2(dyeTexel.x,0));
        vec4 c=texture(source,grid+vec2(0,dyeTexel.y)),d=texture(source,grid+dyeTexel);
        vec4 lo=min(min(a,b),min(c,d)),hi=max(max(a,b),max(c,d));
        vec4 corrected=texture(forwardField,uv)+.5*(texture(source,uv)-texture(reverseField,uv));
        result=clamp(corrected,lo,hi)*exp(-decay*fadeDt);
      }`,
    curl: `uniform sampler2D velocity;
      void main(){float l=texture(velocity,uv-vec2(texel.x,0)).y;
        float r=texture(velocity,uv+vec2(texel.x,0)).y;
        float t=texture(velocity,uv+vec2(0,texel.y)).x;
        float b=texture(velocity,uv-vec2(0,texel.y)).x;
        result=vec4(.5*(r-l-t+b),0,0,1);}`,
    vorticity: `uniform sampler2D velocity,curl;uniform float dt,strength;
      void main(){float l=texture(curl,uv-vec2(texel.x,0)).x;
        float r=texture(curl,uv+vec2(texel.x,0)).x;
        float t=texture(curl,uv+vec2(0,texel.y)).x;
        float b=texture(curl,uv-vec2(0,texel.y)).x;
        float c=texture(curl,uv).x;vec2 force=.5*vec2(abs(t)-abs(b),abs(r)-abs(l));
        force=force/(length(force)+.0001)*strength*c;force.y=-force.y;
        result=vec4(clamp(texture(velocity,uv).xy+force*dt,vec2(-160),vec2(160)),0,1);}`,
    // A touch of viscosity: removes the grid-scale jitter that vorticity
    // confinement amplifies, which otherwise shows as frosty, blocky ink.
    viscosity: `uniform sampler2D velocity;uniform float amount;
      void main(){vec2 c=texture(velocity,uv).xy;
        vec2 n=texture(velocity,uv-vec2(texel.x,0)).xy+texture(velocity,uv+vec2(texel.x,0)).xy+
          texture(velocity,uv-vec2(0,texel.y)).xy+texture(velocity,uv+vec2(0,texel.y)).xy;
        result=vec4(mix(c,n*.25,amount),0,1);}`,
    divergence: `uniform sampler2D velocity;
      void main(){vec2 c=texture(velocity,uv).xy;
        float l=uv.x<texel.x?-c.x:texture(velocity,uv-vec2(texel.x,0)).x;
        float r=uv.x>1.-texel.x?-c.x:texture(velocity,uv+vec2(texel.x,0)).x;
        float b=uv.y<texel.y?-c.y:texture(velocity,uv-vec2(0,texel.y)).y;
        float t=uv.y>1.-texel.y?-c.y:texture(velocity,uv+vec2(0,texel.y)).y;
        result=vec4(.5*(r-l+t-b),0,0,1);}`,
    pressure: `uniform sampler2D pressure,divergence;
      void main(){float l=texture(pressure,uv-vec2(texel.x,0)).x;
        float r=texture(pressure,uv+vec2(texel.x,0)).x;
        float b=texture(pressure,uv-vec2(0,texel.y)).x;
        float t=texture(pressure,uv+vec2(0,texel.y)).x;
        result=vec4((l+r+b+t-texture(divergence,uv).x)*.25,0,0,1);}`,
    project: `uniform sampler2D velocity,pressure;
      void main(){float l=texture(pressure,uv-vec2(texel.x,0)).x;
        float r=texture(pressure,uv+vec2(texel.x,0)).x;
        float b=texture(pressure,uv-vec2(0,texel.y)).x;
        float t=texture(pressure,uv+vec2(0,texel.y)).x;
        result=vec4(texture(velocity,uv).xy-vec2(r-l,t-b),0,1);}`,
    impulse: `uniform sampler2D source;uniform vec2 point,push;uniform float aspect,radius;
      void main(){vec2 p=(uv-point)*vec2(aspect,1.);float g=exp(-dot(p,p)/(radius*radius));
        result=vec4(clamp(texture(source,uv).xy+push*g,vec2(-160),vec2(160)),0,1);}`,
    drop: `${NOISE}
      uniform sampler2D source;uniform vec2 point;uniform vec4 ink;
      uniform float aspect,radius,seed,amount;
      void main(){vec2 p=(uv-point)*vec2(aspect,1.)/radius;
        // A soft bloom with a gently irregular outline and a faint darker
        // edge, like a drop settling into wet paper.
        float n=fbm(p*2.2+seed);float d=length(p)*(.9+.2*n);
        float core=exp(-d*d*2.4);
        float rim=exp(-pow((d-.95)*4.5,2.))*.1;
        vec4 old=texture(source,uv);
        result=min(old+ink*(core+rim)*amount,vec4(4.));}`,
    diagnostics: `uniform sampler2D pigment,velocity;
      void main(){float density=dot(max(texture(pigment,uv),vec4(0)),vec4(1));
        result=vec4(min(1.,density/4.),min(1.,length(texture(velocity,uv).xy)/160.),step(.035,density),1.);}`,
    display: `${NOISE}
      uniform sampler2D pigment,paperTexture;uniform vec2 viewport;
      uniform vec3 paper,ink0,ink1,ink2,ink3;uniform vec3 quietBand;
      void main(){
        vec4 w=max(texture(pigment,uv),vec4(0));
        // Smoothly compress density, preserving color ratios and soft edges.
        // Even repeated overlapping strokes remain a translucent wash.
        float total=dot(w,vec4(1));w*=.95/(.95+total);
        float y=1.-uv.y;
        float quiet=smoothstep(quietBand.x-.025,quietBand.x+.035,y)*(1.-smoothstep(quietBand.y-.035,quietBand.y+.025,y))*quietBand.z;
        w*=1.-quiet*.45;
        // A hair of bare paper at the sheet's edge hides boundary streaks.
        vec2 inset=min(uv,1.-uv)*viewport;
        w*=smoothstep(2.,14.,min(inset.x,inset.y));
        vec3 absorption=w.r*-log(max(ink0,vec3(.025)))+w.g*-log(max(ink1,vec3(.025)))+
          w.b*-log(max(ink2,vec3(.025)))+w.a*-log(max(ink3,vec3(.025)));
        float grain=texture(paperTexture,uv*viewport/512.).r;
        float mottling=fbm(uv*viewport/165.);
        vec3 sheet=paper*(.965+.032*grain+.027*mottling);
        float density=dot(w,vec4(1));
        // Pigment settles into the paper's grain; no neon bloom or 3D shine.
        absorption*=.9+grain*.16;
        vec3 color=sheet*exp(-absorption);
        float edge=length(dFdx(w))+length(dFdy(w));
        color*=1.-min(.06,edge*.5)*smoothstep(.03,.25,density);
        result=vec4(color,1.);
      }`,
  };

  function compile(type, text) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, text); gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      const error = gl.getShaderInfoLog(shader); gl.deleteShader(shader); throw new Error(error);
    }
    resources.shaders.push(shader); return shader;
  }
  function makeProgram(fragment) {
    const program = gl.createProgram();
    gl.attachShader(program, compile(gl.VERTEX_SHADER, VERTEX));
    gl.attachShader(program, compile(gl.FRAGMENT_SHADER, HEAD + fragment));
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
    resources.programs.push(program);
    const uniforms = {};
    for (let i = 0; i < gl.getProgramParameter(program, gl.ACTIVE_UNIFORMS); i++) {
      const name = gl.getActiveUniform(program, i).name;
      uniforms[name] = gl.getUniformLocation(program, name);
    }
    return { program, uniforms };
  }
  function target(width, height, floating = true) {
    const texture = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texImage2D(gl.TEXTURE_2D, 0, floating ? gl.RGBA16F : gl.RGBA8, width, height, 0, gl.RGBA, floating ? gl.HALF_FLOAT : gl.UNSIGNED_BYTE, null);
    const fbo = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, texture, 0);
    if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE) throw new Error('Floating point render target unavailable');
    gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
    const value = { width, height, texture, fbo };
    resources.targets.push(value); return value;
  }
  function pair(w, h) {
    return { read: target(w, h), write: target(w, h), swap() { [this.read, this.write] = [this.write, this.read]; } };
  }
  function run(name, output, values = {}) {
    const p = programs[name]; gl.useProgram(p.program);
    let unit = 0;
    for (const [key, value] of Object.entries(values)) {
      const location = p.uniforms[key];
      if (location === undefined) continue;
      if (value?.texture) {
        gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, value.texture);
        gl.uniform1i(location, unit++);
      } else if (Array.isArray(value)) {
        if (value.length === 2) gl.uniform2fv(location, value);
        if (value.length === 3) gl.uniform3fv(location, value);
        if (value.length === 4) gl.uniform4fv(location, value);
      } else gl.uniform1f(location, value);
    }
    gl.bindFramebuffer(gl.FRAMEBUFFER, output?.fbo ?? null);
    gl.viewport(0, 0, output?.width ?? canvas.width, output?.height ?? canvas.height);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
  function sizeFor(shortSide) {
    const aspect = canvas.width / canvas.height;
    return aspect >= 1 ? [Math.round(shortSide * aspect), shortSide] : [shortSide, Math.round(shortSide / aspect)];
  }
  function releaseTargets() {
    for (const t of resources.targets) { gl.deleteTexture(t.texture); gl.deleteFramebuffer(t.fbo); }
    resources.targets.length = 0;
  }
  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(1, Math.round(canvas.clientWidth * dpr));
    const height = Math.max(1, Math.round(canvas.clientHeight * dpr));
    if (width === canvas.width && height === canvas.height && pigment) return;
    canvas.width = width; canvas.height = height;
    const old = pigment?.read;
    const oldTargets = resources.targets.splice(0);
    const sim = sizeFor(SIM_SHORT);
    const dye = sizeFor(Math.min(DYE_SHORT, Math.round(1536 / Math.max(width / height, height / width))));
    velocity = pair(...sim); pressure = pair(...sim);
    divergence = target(...sim); curl = target(...sim);
    pigment = pair(...dye); forward = target(...dye); reverse = target(...dye);
    diagnosticTarget = target(48, 96, false);
    if (old) run('copy', pigment.read, { source: old, scale: 1 });
    for (const t of oldTargets) { gl.deleteTexture(t.texture); gl.deleteFramebuffer(t.fbo); }
  }
  function makePaper() {
    const paper = document.createElement('canvas'); paper.width = paper.height = 512;
    const ctx = paper.getContext('2d');
    let seed = 1701;
    const random = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
    const pixels = ctx.createImageData(512, 512);
    for (let i = 0; i < pixels.data.length; i += 4) {
      const v = 135 + Math.round(random() * 60);
      pixels.data[i] = pixels.data[i + 1] = pixels.data[i + 2] = v; pixels.data[i + 3] = 255;
    }
    ctx.putImageData(pixels, 0, 0); ctx.strokeStyle = 'rgba(65,65,65,.18)'; ctx.lineWidth = .55;
    for (let i = 0; i < 950; i++) {
      const x = random() * 512, y = random() * 512, angle = random() * Math.PI;
      const length = 2 + random() * 12; ctx.beginPath(); ctx.moveTo(x, y);
      ctx.lineTo(x + Math.cos(angle) * length, y + Math.sin(angle) * length); ctx.stroke();
    }
    const texture = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, paper);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
    return { texture };
  }
  function flow(x, y, dx, dy, radius = .052) {
    if (state.reducedMotion) return;
    run('impulse', velocity.write, { source: velocity.read, point: [x, 1 - y], push: [dx, -dy], aspect: canvas.width / canvas.height, radius });
    velocity.swap();
  }
  function drop(x, y, color = state.ink, amount = 1.25, radius = .043, count = false) {
    const ink = [0, 0, 0, 0]; ink[clamp(Math.round(color), 0, 3)] = 1;
    run('drop', pigment.write, { source: pigment.read, point: [x, 1 - y], ink, aspect: canvas.width / canvas.height, radius, seed: state.time * 7.13 + state.drops * 11.9, amount });
    pigment.swap(); lastInput = state.time;
    if (count) { state.drops++; emit('drop', { count: state.drops }); }
  }
  function bloom(x, y, color, amount = 1.7, radius = .085, count = true) {
    blooms.push({ x, y, color, amount, radius, t: 0 });
    drop(x, y, color, amount * .35, radius * .45, count);
  }
  function growBlooms(dt) {
    for (let i = blooms.length - 1; i >= 0; i--) {
      const b = blooms[i]; b.t += dt;
      const k = clamp(b.t / BLOOM_SECONDS, 0, 1);
      drop(b.x, b.y, b.color, b.amount * .65 * dt / BLOOM_SECONDS, b.radius * (.45 + .55 * Math.sqrt(k)));
      if (k >= 1) blooms.splice(i, 1);
    }
  }
  function simulate(dt, fadeDt) {
    const texel = [1 / velocity.read.width, 1 / velocity.read.height];
    if (!state.reducedMotion) {
      run('curl', curl, { velocity: velocity.read, texel });
      run('vorticity', velocity.write, { velocity: velocity.read, curl, texel, dt, strength: 8 }); velocity.swap();
      run('viscosity', velocity.write, { velocity: velocity.read, texel, amount: .4 }); velocity.swap();
      run('divergence', divergence, { velocity: velocity.read, texel });
      run('copy', pressure.write, { source: pressure.read, scale: .75 }); pressure.swap();
      for (let i = 0; i < 16; i++) { run('pressure', pressure.write, { pressure: pressure.read, divergence, texel }); pressure.swap(); }
      run('project', velocity.write, { velocity: velocity.read, pressure: pressure.read, texel }); velocity.swap();
      run('advect', velocity.write, { source: velocity.read, velocity: velocity.read, texel, dt, decay: .22 }); velocity.swap();
      run('advect', forward, { source: pigment.read, velocity: velocity.read, texel, dt, decay: 0 });
      run('advect', reverse, { source: forward, velocity: velocity.read, texel, dt: -dt, decay: 0 });
      run('correct', pigment.write, { source: pigment.read, velocity: velocity.read, forwardField: forward, reverseField: reverse,
        texel, dyeTexel: [1 / pigment.read.width, 1 / pigment.read.height], dt, fadeDt, decay: washLeft > 0 ? 5.5 : INK_FADE });
    } else run('copy', pigment.write, { source: pigment.read, scale: Math.exp(-(washLeft > 0 ? 5.5 : INK_FADE) * fadeDt) });
    pigment.swap();
    if (washLeft > 0) { washLeft -= dt; if (washLeft <= 0) clear(); }
  }
  function render() {
    run('display', null, { pigment: pigment.read, paperTexture, viewport: [canvas.width, canvas.height], paper: state.paper,
      ink0: state.palette[0], ink1: state.palette[1], ink2: state.palette[2], ink3: state.palette[3],
      quietBand: [state.quietTop, state.quietBottom, state.quietEnabled ? 1 : 0] });
  }
  function clear() {
    blooms.length = 0;
    for (const t of resources.targets) { gl.bindFramebuffer(gl.FRAMEBUFFER, t.fbo); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT); }
    autoStroke = null; autoElapsed = -2; lastInput = state.time - 65;
  }
  function autoPaint(dt) {
    if (!state.playing || washLeft > 0 || pointers.size) return;
    autoElapsed += dt;
    if (!autoStroke) {
      if (autoElapsed < 1.1) return;
      // Anchors cover the whole sheet; each cycle drifts them a little.
      const anchors = [[.28,.30],[.72,.55],[.30,.78],[.68,.22],[.50,.50],[.24,.58],[.76,.82],[.46,.14]];
      const anchor = anchors[autoIndex % anchors.length];
      const cycle = Math.floor(autoIndex / anchors.length);
      const x = anchor[0] + Math.sin(cycle * 2.4 + autoIndex) * .06;
      const y = anchor[1] + Math.sin(cycle * 1.7 + autoIndex * .8) * .05;
      const color = (state.ink + autoIndex) % 4;
      const angle = (autoIndex * 2.39996) % (Math.PI * 2);
      autoStroke = { x, y, elapsed: 0, color, angle, direction: autoIndex % 2 ? -1 : 1, lastX: x, lastY: y, emitted: -1 };
      autoIndex++; autoElapsed = 0;
      bloom(x, y, color, 1.5, .09, false);
    }
    const s = autoStroke; s.elapsed += dt;
    if (state.reducedMotion) { autoStroke = null; autoElapsed = -3; return; }
    const duration = 5.2;
    const p = clamp(s.elapsed / duration, 0, 1);
    // A long S-curve along the stroke's heading.
    const along = (p - .15) * .5;
    const across = s.direction * Math.sin(p * Math.PI * 1.6) * .12;
    const ca = Math.cos(s.angle), sa = Math.sin(s.angle);
    const x = clamp(s.x + ca * along - sa * across, .04, .96);
    const y = clamp(s.y + sa * along + ca * across, .04, .96);
    if (Math.floor(s.elapsed * 30) !== s.emitted) {
      s.emitted = Math.floor(s.elapsed * 30);
      if (p > .12) {
        flow(x, y, (x - s.lastX) * 1700, (y - s.lastY) * 1700, .075);
        drop(x, y, s.color, .11 + .08 * Math.sin(p * 19) ** 2, .034);
      }
      s.lastX = x; s.lastY = y;
    }
    if (p >= 1) { autoStroke = null; autoElapsed = -1.2; }
  }
  function point(e) { const r = canvas.getBoundingClientRect(); return [clamp((e.clientX - r.left) / r.width, 0, 1), clamp((e.clientY - r.top) / r.height, 0, 1)]; }
  function nextInk() {
    if (state.rotate) state.ink = (state.ink + 1) % 4;
    return state.ink;
  }
  // Touches arrive from Flutter ('touch' commands), which hit-tests the
  // controls drawn over the water; DOM pointers are kept for the web preview.
  function touchDown(id, x, y) {
    if (!state.active) return;
    const color = nextInk();
    pointers.set(id, { x, y, color, travelled: 0 });
    bloom(x, y, color); lastDropTime = state.time; wake();
  }
  function pointerDown(e) {
    if (!state.active) return; e.preventDefault(); const [x, y] = point(e);
    canvas.setPointerCapture?.(e.pointerId);
    touchDown(e.pointerId, x, y);
  }
  function pointerMove(e) {
    if (!pointers.has(e.pointerId)) return; e.preventDefault(); const [x, y] = point(e);
    touchMove(e.pointerId, x, y);
  }
  function touchMove(id, x, y) {
    const p = pointers.get(id); if (!p) return;
    const dx = x - p.x, dy = y - p.y, dist = Math.hypot(dx, dy);
    flow(x, y, clamp(dx * 2400, -80, 80), clamp(dy * 2400, -80, 80), .06);
    // A continuous ribbon of ink along the drag, thinning as it runs dry.
    p.travelled += dist;
    const load = .55 * Math.exp(-p.travelled * 2.2) + .12;
    const steps = Math.min(12, Math.ceil(dist / .008));
    for (let i = 1; i <= steps; i++) {
      const t = i / steps;
      drop(p.x + dx * t, p.y + dy * t, p.color, load / Math.max(1, steps * .6), .03);
    }
    p.x = x; p.y = y; lastInput = state.time; wake();
  }
  function pointerUp(e) { pointers.delete(e.pointerId); }
  function diagnosticSnapshot() {
    if (!diagnosticTarget || gl.isContextLost()) return {};
    run('diagnostics', diagnosticTarget, { pigment: pigment.read, velocity: velocity.read });
    const pixels = new Uint8Array(48 * 96 * 4);
    gl.readPixels(0, 0, 48, 96, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
    let total = 0, peak = 0, coverage = 0, speed = 0, checksum = 2166136261;
    for (let i = 0; i < pixels.length; i += 4) {
      total += pixels[i]; peak = Math.max(peak, pixels[i]); coverage += pixels[i + 2]; speed += pixels[i + 1];
      checksum = Math.imul(checksum ^ pixels[i], 16777619) >>> 0;
    }
    const count = pixels.length / 4;
    return { pigmentMean: total / count / 255 * 4, pigmentPeak: peak / 255 * 4,
      coverage: coverage / count / 255, velocityMean: speed / count / 255 * 160, pigmentChecksum: checksum };
  }
  function metrics(diagnostics = false) {
    return { ...(diagnostics ? diagnosticSnapshot() : {}), renderer: 'webgl2-fluid', fps: Math.round(state.fps), frames: state.frames, drops: state.drops, washes: state.washes,
      dyeWidth: pigment?.read.width ?? 0, dyeHeight: pigment?.read.height ?? 0, active: state.active, playing: state.playing,
      reducedMotion: state.reducedMotion, settled: !state.playing && !pointers.size && washLeft <= 0 && state.time - lastInput >= 65, contextLost: gl?.isContextLost() ?? true, events };
  }
  function tick(now) {
    animation = 0;
    if (!state.active || document.hidden || state.disposed || gl.isContextLost()) return;
    if (lastFrame && now - lastFrame < 1000 / 60 - 1) { animation = requestAnimationFrame(tick); return; }
    const elapsed = lastFrame ? (now - lastFrame) / 1000 : 1 / 60;
    const dt = Math.min(elapsed, 1 / 30); lastFrame = now; state.time += dt;
    try { resize(); autoPaint(dt); growBlooms(dt); simulate(dt, elapsed); render(); state.frames++; }
    catch (error) { emit('failed', { reason: String(error.message || error) }); dispose(); return; }
    frameTimes.push(elapsed); if (frameTimes.length > 90) frameTimes.shift();
    state.fps = frameTimes.length / frameTimes.reduce((a,b) => a+b,0);
    if (now - lastMetrics > 3000) { lastMetrics = now; emit('metrics', { ...metrics(), events: undefined }); }
    if (state.playing || washLeft > 0 || pointers.size || blooms.length || state.time - lastInput < 65) animation = requestAnimationFrame(tick);
  }
  function wake() { if (!animation && state.active && !state.disposed) { lastFrame = 0; animation = requestAnimationFrame(tick); } }
  function command(message) {
    if (!message || state.disposed) return;
    if (message.type === 'configure') {
      if (Array.isArray(message.palette) && message.palette.length === 4) state.palette = message.palette;
      if (Array.isArray(message.paper) && message.paper.length === 3) state.paper = message.paper;
      if (Number.isInteger(message.ink)) state.ink = clamp(message.ink,0,3);
      if (typeof message.rotate === 'boolean') state.rotate = message.rotate;
      if (typeof message.reducedMotion === 'boolean') {
        if (message.reducedMotion && !state.reducedMotion) {
          for (const t of [velocity.read, velocity.write, pressure.read, pressure.write]) {
            gl.bindFramebuffer(gl.FRAMEBUFFER, t.fbo); gl.clearColor(0,0,0,0); gl.clear(gl.COLOR_BUFFER_BIT);
          }
          autoStroke = null;
        }
        state.reducedMotion = message.reducedMotion;
      }
      if (typeof message.playing === 'boolean') state.playing = message.playing;
      if (typeof message.active === 'boolean') state.active = message.active;
      if (Array.isArray(message.quietBand)) [state.quietTop,state.quietBottom,state.quietEnabled] = message.quietBand;
      if (!state.active) { cancelAnimationFrame(animation); animation = 0; pointers.clear(); }
      else wake();
    } else if (message.type === 'wash') { washLeft = .85; autoStroke = null; state.washes++; wake(); }
    else if (message.type === 'clear') { clear(); render(); wake(); }
    else if (message.type === 'drop') { bloom(clamp(message.x,0,1),clamp(message.y,0,1),message.ink ?? nextInk()); wake(); }
    else if (message.type === 'touch') {
      const id = 'f' + message.id, x = clamp(message.x, 0, 1), y = clamp(message.y, 0, 1);
      if (message.phase === 'down') touchDown(id, x, y);
      else if (message.phase === 'move') touchMove(id, x, y);
      else pointers.delete(id);
    }
    else if (message.type === 'stir') { flow(clamp(message.x,0,1),clamp(message.y,0,1),clamp(message.dx,-65,65),clamp(message.dy,-65,65)); lastInput=state.time; wake(); }
    else if (message.type === 'dispose') dispose();
  }
  function dispose() {
    state.disposed = true; cancelAnimationFrame(animation); animation = 0;
    canvas.removeEventListener('pointerdown', pointerDown); canvas.removeEventListener('pointermove', pointerMove);
    canvas.removeEventListener('pointerup', pointerUp); canvas.removeEventListener('pointercancel', pointerUp);
    window.removeEventListener('resize', wake);
    if (gl && !gl.isContextLost()) {
      releaseTargets(); for (const p of resources.programs) gl.deleteProgram(p);
      for (const s of resources.shaders) gl.deleteShader(s);
      gl.deleteBuffer(vertexBuffer); if (paperTexture) gl.deleteTexture(paperTexture.texture);
      gl.getExtension('WEBGL_lose_context')?.loseContext();
    }
  }
  window.StillWaters = { command, metrics };
  try {
    gl = canvas.getContext('webgl2', { alpha: false, depth: false, stencil: false, antialias: false, preserveDrawingBuffer: false, powerPreference: 'high-performance' });
    if (!gl || !gl.getExtension('EXT_color_buffer_float')) throw new Error('WebGL 2 floating point rendering is unavailable');
    gl.disable(gl.BLEND); gl.disable(gl.DEPTH_TEST);
    programs = Object.fromEntries(Object.entries(SHADERS).map(([name, source]) => [name, makeProgram(source)]));
    vertexBuffer = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,1,1]), gl.STATIC_DRAW);
    gl.vertexAttribPointer(0,2,gl.FLOAT,false,0,0); gl.enableVertexAttribArray(0);
    paperTexture = makePaper(); resize(); render();
    canvas.addEventListener('pointerdown',pointerDown,{passive:false}); canvas.addEventListener('pointermove',pointerMove,{passive:false});
    canvas.addEventListener('pointerup',pointerUp); canvas.addEventListener('pointercancel',pointerUp);
    window.addEventListener('resize', wake);
    canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); if (!state.disposed) emit('failed',{reason:'context-lost'}); });
    document.addEventListener('visibilitychange', () => { if (document.hidden) { cancelAnimationFrame(animation); animation=0; } else wake(); });
    emit('ready', { renderer:'webgl2-fluid' }); wake();
    // Standalone local preview. The embedded app controls playback explicitly.
    if (new URLSearchParams(location.search).has('drift')) command({type:'configure',playing:true});
  } catch (error) { emit('failed',{reason:String(error.message || error)}); console.error(error); }
})();

# GLSL Noise Algorithms
# https://gist.github.com/patriciogonzalezvivo/670c22f3966e662d2f83

class Noise:
  def __init__(self, renderer):
    self.renderer = renderer
    self.genProgram()
    self.genModel()

  def genProgram(self):
    self.program = _, attribs, uniforms = checkProgram(newProgram("""
attribute vec2 vPos;
attribute vec2 vUV;

uniform mat4 uMatrix;
uniform float uTime;

varying vec3 vaNormal;

float rand(float n) { return fract(sin(n) * 43758.5453123); }
float rand(vec2 n) { return fract(sin(dot(n, vec2(12.9898, 4.1414))) * 43758.5453); }

float noise_1(float p) {
  float fl = floor(p);
  float fc = fract(p);
  return mix(rand(fl), rand(fl + 1.), fc);
}

float noise_1(vec2 n) {
  const vec2 d = vec2(0., 1.);
  vec2 b = floor(n), f = smoothstep(vec2(0.), vec2(1.), fract(n));
  return mix(mix(rand(b), rand(b + d.yx), f.x), mix(rand(b + d.xy), rand(b + d.yy), f.x), f.y);
}

float noise_2(vec2 p){
  vec2 ip = floor(p);
  vec2 u = fract(p);
  u = u * u * (3. - 2. * u);
  
  float res = mix(
    mix(rand(ip), rand(ip + vec2(1., 0.)), u.x),
    mix(rand(ip + vec2(0., 1.)), rand(ip + vec2(1., 1.)), u.x), u.y);
  return res*res;
}

//  Classic Perlin 3D Noise 
//  by Stefan Gustavson (https://github.com/stegu/webgl-noise)
//
vec4 permute(vec4 x){ return mod(((x*34.)+1.)*x, 289.); }
vec4 taylorInvSqrt(vec4 r){ return 1.79284291400159 - 0.85373472095314 * r; }
vec3 fade(vec3 t) { return t*t*t*(t*(t*6.-15.)+10.); }

float cnoise(vec3 P) {
  vec3 Pi0 = floor(P); // Integer part for indexing
  vec3 Pi1 = Pi0 + vec3(1.); // Integer part + 1
  Pi0 = mod(Pi0, 289.);
  Pi1 = mod(Pi1, 289.);
  vec3 Pf0 = fract(P); // Fractional part for interpolation
  vec3 Pf1 = Pf0 - vec3(1.); // Fractional part - 1.
  vec4 ix = vec4(Pi0.x, Pi1.x, Pi0.x, Pi1.x);
  vec4 iy = vec4(Pi0.yy, Pi1.yy);
  vec4 iz0 = Pi0.zzzz;
  vec4 iz1 = Pi1.zzzz;

  vec4 ixy = permute(permute(ix) + iy);
  vec4 ixy0 = permute(ixy + iz0);
  vec4 ixy1 = permute(ixy + iz1);

  vec4 gx0 = ixy0 / 7.;
  vec4 gy0 = fract(floor(gx0) / 7.) - 0.5;
  gx0 = fract(gx0);
  vec4 gz0 = vec4(0.5) - abs(gx0) - abs(gy0);
  vec4 sz0 = step(gz0, vec4(0.));
  gx0 -= sz0 * (step(0., gx0) - 0.5);
  gy0 -= sz0 * (step(0., gy0) - 0.5);

  vec4 gx1 = ixy1 / 7.;
  vec4 gy1 = fract(floor(gx1) / 7.) - 0.5;
  gx1 = fract(gx1);
  vec4 gz1 = vec4(0.5) - abs(gx1) - abs(gy1);
  vec4 sz1 = step(gz1, vec4(0.));
  gx1 -= sz1 * (step(0., gx1) - 0.5);
  gy1 -= sz1 * (step(0., gy1) - 0.5);

  vec3 g000 = vec3(gx0.x, gy0.x, gz0.x);
  vec3 g100 = vec3(gx0.y, gy0.y, gz0.y);
  vec3 g010 = vec3(gx0.z, gy0.z, gz0.z);
  vec3 g110 = vec3(gx0.w, gy0.w, gz0.w);
  vec3 g001 = vec3(gx1.x, gy1.x, gz1.x);
  vec3 g101 = vec3(gx1.y, gy1.y, gz1.y);
  vec3 g011 = vec3(gx1.z, gy1.z, gz1.z);
  vec3 g111 = vec3(gx1.w, gy1.w, gz1.w);

  vec4 norm0 = taylorInvSqrt(vec4(dot(g000, g000), dot(g010, g010), dot(g100, g100), dot(g110, g110)));
  g000 *= norm0.x;
  g010 *= norm0.y;
  g100 *= norm0.z;
  g110 *= norm0.w;
  vec4 norm1 = taylorInvSqrt(vec4(dot(g001, g001), dot(g011, g011), dot(g101, g101), dot(g111, g111)));
  g001 *= norm1.x;
  g011 *= norm1.y;
  g101 *= norm1.z;
  g111 *= norm1.w;

  float n000 = dot(g000, Pf0);
  float n100 = dot(g100, vec3(Pf1.x, Pf0.yz));
  float n010 = dot(g010, vec3(Pf0.x, Pf1.y, Pf0.z));
  float n110 = dot(g110, vec3(Pf1.xy, Pf0.z));
  float n001 = dot(g001, vec3(Pf0.xy, Pf1.z));
  float n101 = dot(g101, vec3(Pf1.x, Pf0.y, Pf1.z));
  float n011 = dot(g011, vec3(Pf0.x, Pf1.yz));
  float n111 = dot(g111, Pf1);

  vec3 fade_xyz = fade(Pf0);
  vec4 n_z = mix(vec4(n000, n100, n010, n110), vec4(n001, n101, n011, n111), fade_xyz.z);
  vec2 n_yz = mix(n_z.xy, n_z.zw, fade_xyz.y);
  float n_xyz = mix(n_yz.x, n_yz.y, fade_xyz.x); 
  return 2.2 * n_xyz;
}

//   <www.shadertoy.com/view/XsX3zB>
//  by Nikita Miropolskiy

vec3 random3(vec3 c) {
  float j = 4096.*sin(dot(c,vec3(17., 59.4, 15.)));
  vec3 r;
  r.z = fract(512.*j);
  j *= .125;
  r.x = fract(512.*j);
  j *= .125;
  r.y = fract(512.*j);
  return r-0.5;
}

const float F3 = 0.3333333;
const float G3 = 0.1666667;
float snoise(vec3 p) {
  vec3 s = floor(p + dot(p, vec3(F3)));
  vec3 x = p - s + dot(s, vec3(G3));
   
  vec3 e = step(vec3(0.), x - x.yzx);
  vec3 i1 = e*(1. - e.zxy);
  vec3 i2 = 1. - e.zxy*(1. - e);
     
  vec3 x1 = x - i1 + G3;
  vec3 x2 = x - i2 + 2.*G3;
  vec3 x3 = x - 1. + 3.*G3;
   
  vec4 w, d;
   
  w.x = dot(x, x);
  w.y = dot(x1, x1);
  w.z = dot(x2, x2);
  w.w = dot(x3, x3);
   
  w = max(0.6 - w, 0.);
   
  d.x = dot(random3(s), x);
  d.y = dot(random3(s + i1), x1);
  d.z = dot(random3(s + i2), x2);
  d.w = dot(random3(s + 1.), x3);
   
  w *= w;
  w *= w;
  d *= w;
   
  return dot(d, vec4(52.));
}

float snoiseFractal(vec3 m) {
  return 0.5333333* snoise(m)
		+0.2666667* snoise(2.*m)
		+0.1333333* snoise(4.*m)
		+0.0666667* snoise(8.*m);
}

// author: ?

vec3 normalNoise(vec2 _st, float _zoom, float _speed) {
  float expon = pow(10., _zoom*2.);
  vec2 v1 = _st / (1.*expon);
  vec2 v2 = _st / (0.62*expon);
  vec2 v3 = _st / (0.83*expon);
  float n = uTime * _speed;
  float nr = (snoise(vec3(v1, n)) + snoise(vec3(v2, n)) + snoise(vec3(v3, n))) / 6. + 0.5;
  n = uTime * _speed + 1000.;
  float ng = (snoise(vec3(v1, n)) + snoise(vec3(v2, n)) + snoise(vec3(v3, n))) / 6. + 0.5;
  return normalize(vec3(nr * 2. - 1., ng * 2. - 1., 0.));
}

void main() {
  // float n = (noise_1(vPos.x) + noise_1(vPos.y) + noise_1(vPos) + noise_2(vPos)) / 4.;
  float n = (cnoise(vec3(uTime / 2., vPos / 4.)) + cnoise(vec3(vPos, uTime))) / 2.;
  float n2 = snoise(vec3(vPos, uTime * 0.5));
  n = (n * 4. + n2) / 5.;
  gl_Position = uMatrix * vec4(vPos.x, -3. + n, vPos.y, 1.);
  vaNormal = normalNoise(vPos, 0.1, 0.5);
}
""", """
precision mediump float;

varying vec3 vaNormal;

void main() {
  float p = (vaNormal.y + 1.) * 0.5;
  vec3 color = mix(vec3(66., 170., 255.) / 255., vec3(93., 118., 203.) / 255., p);
  gl_FragColor = vec4(color, 0.8);
}
""", ('vPos',), ('uMatrix', 'uTime')))
    vPos = attribs["vPos"]
    self.uMatrix = uniforms["uMatrix"]
    self.uTime = uniforms["uTime"]
    def func():
      glVertexAttribPointer(vPos, 2, GL_FLOAT, False, 0, 0)
    self.func = func
    self.location = None
    self.textures = {}
    self.last_texture_id = 0

  def genModel(self):
    frags = []
    frags_append = frags.append
    T = 8
    T2 = T * 3
    for y in range(-T2, T2):
      y2 = (y + 1) / T
      y /= T
      for x in range(-T2, T2):
        x2 = (x + 1) / T
        x /= T
        a, b, c, d = (x, y), (x, y2), (x2, y), (x2, y2)
        frags_append((a, b, c))
        frags_append((c, b, d))
    VBOdata, IBOdata = buildModel(frags)
    self.model = Model(VBOdata, IBOdata, self)

  def draw(self):
    renderer = self.renderer
    enableProgram(self.program)
    # glUniform1i(self.uTexture, 0)
    glUniform1f(self.uTime, renderer.time2)
    glUniformMatrix4fv(self.uMatrix, 1, False, renderer.MVPmatrix, 0)
    # glBindTexture(GL_TEXTURE_2D, renderer.mainTexture)
    self.model.draw()

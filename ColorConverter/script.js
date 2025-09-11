const rgb = document.querySelector('#rgb')
const lab = document.querySelector('#lab')
const cmyk = document.querySelector('#cmyk')

const rgb_r = document.querySelector('#rgb_r')
const rgb_g = document.querySelector('#rgb_g')
const rgb_b = document.querySelector('#rgb_b')
const rgb_r_slider = document.querySelector('#rgb_r_slider')
const rgb_g_slider = document.querySelector('#rgb_g_slider')
const rgb_b_slider = document.querySelector('#rgb_b_slider')

const lab_l = document.querySelector('#lab_l')
const lab_a = document.querySelector('#lab_a')
const lab_b = document.querySelector('#lab_b')
const lab_l_slider = document.querySelector('#lab_l_slider')
const lab_a_slider = document.querySelector('#lab_a_slider')
const lab_b_slider = document.querySelector('#lab_b_slider')

const cmyk_c = document.querySelector('#cmyk_c')
const cmyk_m = document.querySelector('#cmyk_m')
const cmyk_y = document.querySelector('#cmyk_y')
const cmyk_k = document.querySelector('#cmyk_k')
const cmyk_c_slider = document.querySelector('#cmyk_c_slider')
const cmyk_m_slider = document.querySelector('#cmyk_m_slider')
const cmyk_y_slider = document.querySelector('#cmyk_y_slider')
const cmyk_k_slider = document.querySelector('#cmyk_k_slider')

const palette = document.querySelector('#palette')
const warning = document.querySelector('.warning')

// sliders connection
rgb_r_slider.addEventListener('input', () => {
  rgb_r.value = rgb_r_slider.value
  rgb.dispatchEvent(new Event('input'));
})
rgb_g_slider.addEventListener('input', () => {
  rgb_g.value = rgb_g_slider.value
  rgb.dispatchEvent(new Event('input'));
})
rgb_b_slider.addEventListener('input', () => {
  rgb_b.value = rgb_b_slider.value
  rgb.dispatchEvent(new Event('input'));
})
rgb_r.addEventListener('input', () => {
  rgb_r_slider.value = rgb_r.value
})
rgb_g.addEventListener('input', () => {
  rgb_g_slider.value = rgb_g.value
})
rgb_b.addEventListener('input', () => {
  rgb_b_slider.value = rgb_b.value
})

lab_l_slider.addEventListener('input', () => {
  lab_l.value = lab_l_slider.value
  lab.dispatchEvent(new Event('input'))
})
lab_a_slider.addEventListener('input', () => {
  lab_a.value = lab_a_slider.value
  lab.dispatchEvent(new Event('input'))
})
lab_b_slider.addEventListener('input', () => {
  lab_b.value = lab_b_slider.value
  lab.dispatchEvent(new Event('input'))
})
lab_l.addEventListener('input', () => {
  lab_l_slider.value = lab_l.value
})
lab_a.addEventListener('input', () => {
  lab_a_slider.value = lab_a.value
})
lab_b.addEventListener('input', () => {
  lab_b_slider.value = lab_b.value
})

cmyk_c_slider.addEventListener('input', () => {
  cmyk_c.value = cmyk_c_slider.value
  cmyk.dispatchEvent(new Event('input'))
})
cmyk_m_slider.addEventListener('input', () => {
  cmyk_m.value = cmyk_m_slider.value
  cmyk.dispatchEvent(new Event('input'))
})
cmyk_y_slider.addEventListener('input', () => {
  cmyk_y.value = cmyk_y_slider.value
  cmyk.dispatchEvent(new Event('input'))
})
cmyk_k_slider.addEventListener('input', () => {
  cmyk_k.value = cmyk_k_slider.value
  cmyk.dispatchEvent(new Event('input'))
})
cmyk_c.addEventListener('input', () => {
  cmyk_c_slider.value = cmyk_c.value
})
cmyk_m.addEventListener('input', () => {
  cmyk_m_slider.value = cmyk_m.value
})
cmyk_y.addEventListener('input', () => {
  cmyk_y_slider.value = cmyk_y.value
})
cmyk_k.addEventListener('input', () => {
  cmyk_k_slider.value = cmyk_k.value
})

// synchronize sliders
function synchronizeSliders() {
  rgb_r_slider.value = rgb_r.value
  rgb_g_slider.value = rgb_g.value
  rgb_b_slider.value = rgb_b.value

  lab_l_slider.value = lab_l.value
  lab_a_slider.value = lab_a.value
  lab_b_slider.value = lab_b.value

  cmyk_c_slider.value = cmyk_c.value
  cmyk_m_slider.value = cmyk_m.value
  cmyk_y_slider.value = cmyk_y.value
  cmyk_k_slider.value = cmyk_k.value
}

// event listeners
rgb.addEventListener('input', () => {
  const r = parseInt(rgb_r.value);
  const g = parseInt(rgb_g.value);
  const b = parseInt(rgb_b.value);

  const [cmyk_c_value, cmyk_m_value, cmyk_y_value, cmyk_k_value] = rgbToCmyk(r, g, b)
  cmyk_c.value = cmyk_c_value
  cmyk_m.value = cmyk_m_value
  cmyk_y.value = cmyk_y_value
  cmyk_k.value = cmyk_k_value

  const [lab_l_value, lab_a_value, lab_b_value] = xyzToLab(...rgbToXyz(rgb_r.value, rgb_g.value, rgb_b.value))
  lab_l.value = lab_l_value
  lab_a.value = lab_a_value
  lab_b.value = lab_b_value

  synchronizeSliders()
  updatePalette()
})

lab.addEventListener('input', () => {
  const l = parseFloat(lab_l.value)
  const a = parseFloat(lab_a.value)
  const b = parseFloat(lab_b.value)

  const [rgb_r_value, rgb_g_value, rgb_b_value] = xyzToRgb(...labToXyz(l, a, b))
  rgb_r.value = rgb_r_value
  rgb_g.value = rgb_g_value
  rgb_b.value = rgb_b_value

  const [cmyk_c_value, cmyk_m_value, cmyk_y_value, cmyk_k_value] = rgbToCmyk(rgb_r.value, rgb_g.value, rgb_b.value)
  cmyk_c.value = cmyk_c_value
  cmyk_m.value = cmyk_m_value
  cmyk_y.value = cmyk_y_value
  cmyk_k.value = cmyk_k_value

  synchronizeSliders()
  updatePalette()
})

cmyk.addEventListener('input', () => {
  const c = parseFloat(cmyk_c.value)
  const m = parseFloat(cmyk_m.value)
  const y = parseFloat(cmyk_y.value)
  const k = parseFloat(cmyk_k.value)

  const [rgb_r_value, rgb_g_value, rgb_b_value] = cmykToRgb(c, m, y, k)
  rgb_r.value = rgb_r_value
  rgb_g.value = rgb_g_value
  rgb_b.value = rgb_b_value

  const [lab_l_value, lab_a_value, lab_b_value] = xyzToLab(...rgbToXyz(rgb_r.value, rgb_g.value, rgb_b.value))
  lab_l.value = lab_l_value
  lab_a.value = lab_a_value
  lab_b.value = lab_b_value

  synchronizeSliders()
  updatePalette()
})

palette.addEventListener('input', () => {
  const hexColor = palette.value;
  
  const r = parseInt(hexColor.substr(1, 2), 16)
  const g = parseInt(hexColor.substr(3, 2), 16)
  const b = parseInt(hexColor.substr(5, 2), 16)
  
  rgb_r.value = r;
  rgb_g.value = g;
  rgb_b.value = b;

  rgb.dispatchEvent(new Event('input'));
})

// palette
function updatePalette() {
  const r = parseInt(rgb_r.value)
  const g = parseInt(rgb_g.value)
  const b = parseInt(rgb_b.value)
  
  const hexColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  
  palette.value = hexColor;
}

// transition functions (direct)
function rgbToCmyk(r, g, b) {
  let k = Math.min(1 - r / 255, 1 - g / 255, 1 - b / 255)
  let c = (1 - r / 255 - k) / (1 - k) || 0
  let m = (1 - g / 255 - k) / (1 - k) || 0
  let y = (1 - b / 255 - k) / (1 - k) || 0
  
  c = c.toFixed(2)
  m = m.toFixed(2)
  y = y.toFixed(2)
  k = k.toFixed(2)

  return [c, m, y, k]
}

function cmykToRgb(c, m, y, k) {
  let r = 255 * (1 - c) * (1 - k)
  let g = 255 * (1 - m) * (1 - k)
  let b = 255 * (1 - y) * (1 - k)
  
  r = Math.round(r)
  g = Math.round(g)
  b = Math.round(b)

  return [r, g, b]
}

// transition functions (auxiliary)
function xyzToRgb(x, y, z) {
  const f = (x) => {
    if (x >= 0.0031308) {
      return 1.055 * x ** (1 / 2.4) - 0.055
    } else {
      return 12.92 * x
    }
  }

  x /= 100
  y /= 100
  z /= 100

  let r = 3.2406 * x - 1.5372 * y - 0.4986 * z
  let g = -0.9689 * x + 1.8758 * y + 0.0415 * z
  let b = 0.0557 * x - 0.2040 * y + 1.0570 * z

  if (r < 0 || g < 0 || b < 0 || r > 1 || g > 1 || b > 1) {
    warning.classList.add('show')
  } else {
    warning.classList.remove('show')
  }

  r = f(r)
  g = f(g)
  b = f(b)

  r = Math.min(255, Math.max(0, Math.round(r * 255)))
  g = Math.min(255, Math.max(0, Math.round(g * 255)))
  b = Math.min(255, Math.max(0, Math.round(b * 255)))

  return [r, g, b]
}

function rgbToXyz(r, g, b) {
  const f = (x) => {
    if (x >= 0.04045) {
      return ((x + 0.055) / 1.055) ** 2.4
    } else {
      return x / 12.92
    }
  }

  if (r < 0 || g < 0 || b < 0 || r > 255 || g > 255 || b > 255) {
    warning.classList.add('show');
  } else {
    warning.classList.remove('show');
  }

  r = f(r / 255) * 100
  g = f(g / 255) * 100
  b = f(b / 255) * 100

  let x = 0.412453 * r + 0.357580 * g + 0.180423 * b
  let y = 0.212671 * r + 0.715160 * g + 0.072169 * b
  let z = 0.019334 * r + 0.119193 * g + 0.950227 * b

  return [x, y, z]
}

function xyzToLab(x, y, z) {
  const f = (x) => {
    if (x >= 0.008856) {
      return x ** (1 / 3)
    } else {
      return (7.787 * x) + (16 / 116)
    }
  }
  
  let l = (116 * f(y / 100) - 16).toFixed(2)
  let a = (500 * (f(x / 95.047) - f(y / 100))).toFixed(2)
  let b = (200 * (f(y / 100) - f(z / 108.883))).toFixed(2)
  
  return [l, a, b]
}

function labToXyz(l, a, b) {
  const f = (t) => {
    if (t ** 3 >= 0.008856) {
      return t ** 3
    } else {
      return (t - 16 / 116) / 7.787
    }
  };

  const fy = (l + 16) / 116
  const fx = fy + a / 500
  const fz = fy - b / 200

  const x = f(fx) * 95.047
  const y = f(fy) * 100
  const z = f(fz) * 108.883

  return [x, y, z];
}

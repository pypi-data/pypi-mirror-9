// captchaimage - Python extension to generate captcha images
//
// 2008, 2015 Fredrik Portstrom <https://portstrom.com>
//
// I, the copyright holder of this file, hereby release it into the
// public domain. This applies worldwide. In case this is not legally
// possible: I grant anyone the right to use this work for any
// purpose, without any conditions, unless such conditions are
// required by law.

#include <math.h>
#include <ft2build.h>
#include <Python.h>
#include <stdlib.h>
#include FT_FREETYPE_H
#include FT_GLYPH_H
#define RAISE(message) PyErr_SetString(PyExc_StandardError, message); \
  return NULL;
#define NOISE_DETAIL 3
#define NOISE_TABLE_SIZE 32
#define RAND_DOUBLE (rand() / (RAND_MAX + 1.))
// Used in plain_noise
#define WEIGHT(t) ((2. * (t < 0 ? -t : t) - 3) * t * t + 1)

// This is a special kind of Perlin noise that returns two-tuples
// instead of scalars. Therefore there are four gradient tables
// instead of two.
struct noise {
  int permutation_table[NOISE_TABLE_SIZE];
  double gradient_table_xx[NOISE_TABLE_SIZE];
  double gradient_table_xy[NOISE_TABLE_SIZE];
  double gradient_table_yx[NOISE_TABLE_SIZE];
  double gradient_table_yy[NOISE_TABLE_SIZE];
};

// Used in get_noise.
static inline void plain_noise(struct noise *noise, double x, double y, int s,
    double *result_x, double *result_y)
{
  x *= s;
  y *= s;
  int a = x;
  int b = y;
  int i;
  int j;

  for(i = 0; i < 2; i++)
    {
      for(j = 0; j < 2; j++)
	{
	  int n = noise->permutation_table[(a + i + noise->permutation_table[
	      (b + j) % NOISE_TABLE_SIZE]) % NOISE_TABLE_SIZE];
	  double x2 = x - a - i;
	  double y2 = y - b - j;
	  double w = WEIGHT(x2) * WEIGHT(y2);
	  *result_x += w * (x2 * noise->gradient_table_xx[n]
	      + y2 * noise->gradient_table_yx[n]);
	  *result_y += w * (x2 * noise->gradient_table_xy[n]
	      + y2 * noise->gradient_table_yy[n]);
	}
    }
}

// Used in create_image_internal.
static inline void get_noise(struct noise *noise, double x, double y,
    double *result_x, double *result_y)
{
  int i;

  for(i = 1; i <= NOISE_DETAIL; i++)
    {
      plain_noise(noise, x, y, i, result_x, result_y);
    }
}

// Used in captchaimage_create_image.
static inline PyObject *create_image_internal(FT_Library library,
    const char *font_face_path, int font_size, int image_size_y,
    const char *text, int seed)
{
  // Initialize font face

  FT_Face face;

  if(FT_New_Face(library, font_face_path, 0, &face))
    {
      RAISE("failed to load font face");
    }

  if(!FT_IS_SCALABLE(face))
    {
      // Non scalable fonts require other operations. There's no
      // reason to use them anyway.
      RAISE("font face is not scalable");
    }

  if(FT_Set_Pixel_Sizes(face, 0, font_size))
    {
      RAISE("failed to set font size");
    }

  // Allocate image

  int image_size_x = font_size * strlen(text);
  char *image = malloc(image_size_x * image_size_y);
  memset(image, 255, image_size_x * image_size_y);

  if(!image)
    {
      return PyErr_NoMemory();
    }

  // Seed pseudorandom number generator, used for initializing noise
  // and scaling, rotating and positioning glyphs.

  srand(seed);

  // Prepare the noise structure

  int i;
  struct noise noise;

  for(i = 0; i < NOISE_TABLE_SIZE; i++)
    {
      noise.permutation_table[i] = i;
    }

  for(i = 0; i < NOISE_TABLE_SIZE; i++)
    {
      double m1;
      double m2;
      int j = (int)(RAND_DOUBLE * NOISE_TABLE_SIZE);
      int tmp = noise.permutation_table[i];
      noise.permutation_table[i] = noise.permutation_table[j];
      noise.permutation_table[j] = tmp;

      for(;;)
	{
	  noise.gradient_table_xx[i] = 2 * RAND_DOUBLE - 1;
	  noise.gradient_table_yx[i] = 2 * RAND_DOUBLE - 1;
	  m1 = noise.gradient_table_xx[i] * noise.gradient_table_xx[i]
	      + noise.gradient_table_yx[i] * noise.gradient_table_yx[i];

	  if(m1 > 0 && m1 <= 1)
	    {
	      break;
	    }
	}

      for(;;)
	{
	  noise.gradient_table_xy[i] = 2 * RAND_DOUBLE - 1;
	  noise.gradient_table_yy[i] = 2 * RAND_DOUBLE - 1;
	  m2 = noise.gradient_table_xy[i] * noise.gradient_table_xy[i]
	      + noise.gradient_table_yy[i] * noise.gradient_table_yy[i];

	  if(m2 > 0 && m2 <= 1)
	    {
	      break;
	    }
	}

      m1 = sqrt(m1 + m2);
      noise.gradient_table_xx[i] /= m1;
      noise.gradient_table_xy[i] /= m1;
      noise.gradient_table_yx[i] /= m1;
      noise.gradient_table_yy[i] /= m1;
    }

  // Draw each letter

  int offset_x = 0;

  while(*text)
    {
      // Set rotation and scale

      {
	FT_Matrix matrix;
	double angle = (RAND_DOUBLE - .5) * M_PI / 4;
	double size = RAND_DOUBLE / 4 +  1;
	matrix.xx = (FT_Fixed)(size * cos(angle) * 0x10000);
	matrix.yx = (FT_Fixed)(size * sin(angle) * 0x10000);
	matrix.xy = -matrix.yx;
	matrix.yy = matrix.xx;
	FT_Set_Transform(face, &matrix, NULL);
      }

      if(FT_Load_Glyph(face, FT_Get_Char_Index(face, *text), FT_LOAD_DEFAULT))
	{
	  free(image);
	  RAISE("failed to load glyph");
	}

      // Distort outline

      {
	FT_Outline *outline = &face->glyph->outline;
	int i = outline->n_points;

	while(i)
	  {
	    i--;
	    double noise_x = 0;
	    double noise_y = 0;
	    get_noise(&noise, (outline->points[i].x / 64. + offset_x) / font_size / 3,
		outline->points[i].y / 192. / font_size, &noise_x, &noise_y);
	    outline->points[i].x += 16 * font_size * noise_x;
	    outline->points[i].y += 16 * font_size * noise_y;
	  }
      }

      if(FT_Render_Glyph(face->glyph, FT_RENDER_MODE_NORMAL))
	{
	  free(image);
	  RAISE("failed to render glyph");
	}

      // Copy glyph to the image

      FT_Bitmap *bitmap = &face->glyph->bitmap;
      int offset_y = bitmap->rows < image_size_y
	? RAND_DOUBLE * (image_size_y - bitmap->rows) : 0;
      int x;
      int x_max = bitmap->width < image_size_x - offset_x
	? bitmap->width : image_size_x - offset_x;
      int y_max = bitmap->rows < image_size_y ? bitmap->rows : image_size_y;

      for(x = 0; x < x_max; x++)
	{
	  int y;

	  for(y = 0; y < y_max; y++)
	    {
	      int value = bitmap->buffer[y * bitmap->pitch + x];

	      if(value)
		{
		  image[(y + offset_y) * image_size_x + x + offset_x] = 255
		      - value;
		}
	    }
	}

      offset_x += bitmap->width;
      text++;

      if(*text)
	{
	  offset_x -= font_size / 8;
	}
    }

  // Crop image

  char *cropped_image = malloc(offset_x * image_size_y);

  if(!cropped_image)
    {
      return PyErr_NoMemory();
    }

  {
    int y;

    for(y = 0; y < image_size_y; y++)
      {
	memmove(cropped_image + offset_x * y, image + image_size_x * y,
	    offset_x);
      }
  }

  free(image);
  PyObject *value = PyString_FromStringAndSize(cropped_image,
      offset_x * image_size_y);
  free(cropped_image);
  return value;
}

static PyObject *captchaimage_create_image(PyObject *self, PyObject *args)
{
  const char *font_face_path;
  const char *text;
  int font_size;
  int image_size_y;
  int seed = -1;
  FT_Library library;

  if(!PyArg_ParseTuple(args, "siis|i", &font_face_path, &font_size,
      &image_size_y, &text, &seed))
    {
      return NULL;
    }

  if(font_size < 1 || image_size_y < 1)
    {
      PyErr_SetString(PyExc_ValueError, "Size arguments must be positive.");
      return NULL;
    }

  if(FT_Init_FreeType(&library))
    {
      RAISE("Failed to initialize Freetype.");
    }

  if (seed == -1)
    {
      const char *p = text;

      while(*p)
	{
	  seed += *p;
	  p++;
	}
    }

  PyObject *value = create_image_internal(library, font_face_path, font_size,
      image_size_y, text, seed);
  FT_Done_FreeType(library);
  return value;
}

PyDoc_STRVAR(captchaimage_create_image__doc__,
    "create_image(font_face_path, font_size, image_size_y, text[, seed])"
    "-> image_data\n"
    "Create captcha image. It's recommended that 'text' is only uppercase "
    "letters and numbers. Returns a string with one byte per pixel. Image "
    "height is 'image_size_y'. Image width is the length of the return value "
    "divided by 'image_size_y'. The argument 'seed' is an integer that "
    "specifies the random seed used for distorting the text. It's recommended "
    "to generate a new random seed every time when generating a new challenge, "
    "so the same text will not be displayed in the same way if it's displayed "
    "in multiple challenges. If the argument is not specified (deprecated), a "
    "seed is deterministically chosen based on the text.");

static PyMethodDef captchaimage_methods[] = {
  {"create_image", captchaimage_create_image, METH_VARARGS,
   captchaimage_create_image__doc__},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initcaptchaimage(void)
{
  Py_InitModule("captchaimage", captchaimage_methods);
}

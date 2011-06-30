/* Consolidated version of my_cquantizer from jquant1 and jquant2.
 * They seem sufficiently diverse not to fuck up any structure by combining them.
 */

typedef struct {
  struct jpeg_color_quantizer pub; /* public fields */

  /* Space for the eventually created colormap is stashed here */
  JSAMPARRAY sv_colormap;	/* colormap allocated at init time */
  int desired;			/* desired # of colors = size of colormap */

  /* Variables for accumulating image statistics */
  hist3d histogram;		/* pointer to the histogram */

  boolean needs_zeroed;		/* TRUE if next pass must zero histogram */

  /* Variables for Floyd-Steinberg dithering */
  FSERRPTR fserrors;		/* accumulated errors */
  boolean on_odd_row;		/* flag to remember which row we are on */
  int * error_limiter;		/* table for clamping the applied error */

  struct jpeg_color_quantizer pub; /* public fields */

  /* Initially allocated colormap is saved here */
  JSAMPARRAY sv_colormap;	/* The color map as a 2-D pixel array */
  int sv_actual;		/* number of entries in use */

  JSAMPARRAY colorindex;	/* Precomputed mapping for speed */
  /* colorindex[i][j] = index of color closest to pixel value j in component i,
   * premultiplied as described above.  Since colormap indexes must fit into
   * JSAMPLEs, the entries of this array will too.
   */
  boolean is_padded;		/* is the colorindex padded for odither? */

  int Ncolors[MAX_Q_COMPS];	/* # of values alloced to each component */

  /* Variables for ordered dithering */
  int row_index;		/* cur row's vertical index in dither matrix */
  ODITHER_MATRIX_PTR odither[MAX_Q_COMPS]; /* one dither array per component */

  /* Variables for Floyd-Steinberg dithering */
  FSERRPTR fserrors[MAX_Q_COMPS]; /* accumulated errors */
  boolean on_odd_row;		/* flag to remember which row we are on */
} my_cquantizer;

typedef my_cquantizer * my_cquantize_ptr;
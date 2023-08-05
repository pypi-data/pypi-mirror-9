#ifdef _WIN32

#define HAVE_BOOLEAN

#include <windows.h>	/* required for all Windows applications */
#define DLLEXPORT __declspec(dllexport)

#ifdef __cplusplus
extern "C" {
#endif

#else

#ifdef __cplusplus
#define DLLEXPORT extern "C"
#else
#define DLLEXPORT
#endif

#endif

typedef struct {
  double x, y;
} vertex_t;

DLLEXPORT void gr_opengks(void);
DLLEXPORT void gr_closegks(void);
DLLEXPORT void gr_inqdspsize(double *, double *, int *, int *);
DLLEXPORT void gr_openws(int, char *, int);
DLLEXPORT void gr_closews(int);
DLLEXPORT void gr_activatews(int);
DLLEXPORT void gr_deactivatews(int);
DLLEXPORT void gr_clearws(void);
DLLEXPORT void gr_updatews(void);
DLLEXPORT void gr_polyline(int, double *, double *);
DLLEXPORT void gr_polymarker(int, double *, double *);
DLLEXPORT void gr_text(double, double, char *);
DLLEXPORT void gr_inqtext(double, double, char *, double *, double *);
DLLEXPORT void gr_fillarea(int, double *, double *);
DLLEXPORT void gr_cellarray(
  double, double, double, double, int, int, int, int, int, int, int *);
DLLEXPORT void gr_spline(int, double *, double *, int, int);
DLLEXPORT void gr_gridit(
  int, double *, double *, double *, int, int, double *, double *, double *);
DLLEXPORT void gr_setlinetype(int);
DLLEXPORT void gr_inqlinetype(int *);
DLLEXPORT void gr_setlinewidth(double);
DLLEXPORT void gr_setlinecolorind(int);
DLLEXPORT void gr_inqlinecolorind(int *);
DLLEXPORT void gr_setmarkertype(int);
DLLEXPORT void gr_inqmarkertype(int *);
DLLEXPORT void gr_setmarkersize(double);
DLLEXPORT void gr_setmarkercolorind(int);
DLLEXPORT void gr_inqmarkercolorind(int *);
DLLEXPORT void gr_settextfontprec(int, int);
DLLEXPORT void gr_setcharexpan(double);
DLLEXPORT void gr_setcharspace(double);
DLLEXPORT void gr_settextcolorind(int);
DLLEXPORT void gr_setcharheight(double);
DLLEXPORT void gr_setcharup(double, double);
DLLEXPORT void gr_settextpath(int);
DLLEXPORT void gr_settextalign(int, int);
DLLEXPORT void gr_setfillintstyle(int);
DLLEXPORT void gr_setfillstyle(int);
DLLEXPORT void gr_setfillcolorind(int);
DLLEXPORT void gr_setcolorrep(int, double, double, double);
DLLEXPORT void gr_setwindow(double, double, double, double);
DLLEXPORT void gr_inqwindow(double *, double *, double *, double *);
DLLEXPORT void gr_setviewport(double, double, double, double);
DLLEXPORT void gr_selntran(int);
DLLEXPORT void gr_setclip(int);
DLLEXPORT void gr_setwswindow(double, double, double, double);
DLLEXPORT void gr_setwsviewport(double, double, double, double);
DLLEXPORT void gr_createseg(int);
DLLEXPORT void gr_copysegws(int);
DLLEXPORT void gr_redrawsegws(void);
DLLEXPORT void gr_setsegtran(
  int, double, double, double, double, double, double, double);
DLLEXPORT void gr_closeseg(void);
DLLEXPORT void gr_emergencyclosegks(void);
DLLEXPORT void gr_updategks(void);
DLLEXPORT int gr_setspace(double, double, int, int);
DLLEXPORT void gr_inqspace(double *, double *, int *, int *);
DLLEXPORT int gr_setscale(int);
DLLEXPORT void gr_inqscale(int *);
DLLEXPORT int gr_textext(double, double, char *);
DLLEXPORT void gr_inqtextext(double, double, char *, double *, double *);
DLLEXPORT void gr_axes(double, double, double, double, int, int, double);
DLLEXPORT void gr_axeslbl(double, double, double, double, int, int, double,
  void (*)(double, double, const char*), void (*)(double, double, const char*));
DLLEXPORT void gr_grid(double, double, double, double, int, int);
DLLEXPORT void gr_verrorbars(int, double *, double *, double *, double *);
DLLEXPORT void gr_herrorbars(int, double *, double *, double *, double *);
DLLEXPORT void gr_polyline3d(int, double *, double *, double *);
DLLEXPORT void gr_axes3d(
  double, double, double, double, double, double, int, int, int, double);
DLLEXPORT void gr_titles3d(char *, char *, char *);
DLLEXPORT void gr_surface(int, int, double *, double *, double *, int);
DLLEXPORT void gr_contour(
  int, int, int, double *, double *, double *, double *, int);
DLLEXPORT void gr_setcolormap(int);
DLLEXPORT void gr_inqcolormap(int *);
DLLEXPORT void gr_colormap(void);
DLLEXPORT void gr_inqcolor(int, int *);
DLLEXPORT int gr_inqcolorfromrgb(double, double, double);
DLLEXPORT void gr_hsvtorgb(
  double h, double s, double v, double *r, double *g, double *b);
DLLEXPORT double gr_tick(double, double);
DLLEXPORT void gr_adjustrange(double *, double *);
DLLEXPORT void gr_beginprint(char *);
DLLEXPORT void gr_beginprintext(char *, char *, char *, char *);
DLLEXPORT void gr_endprint(void);
DLLEXPORT void gr_ndctowc(double *, double *);
DLLEXPORT void gr_wctondc(double *, double *);
DLLEXPORT void gr_drawrect(double, double, double, double);
DLLEXPORT void gr_fillrect(double, double, double, double);
DLLEXPORT void gr_drawarc(double, double, double, double, int, int);
DLLEXPORT void gr_fillarc(double, double, double, double, int, int);
DLLEXPORT void gr_drawpath(int, vertex_t *, unsigned char *, int);
DLLEXPORT void gr_setarrowstyle(int);
DLLEXPORT void gr_drawarrow(double, double, double, double);
DLLEXPORT int gr_readimage(char *, int *, int *, int **);
DLLEXPORT void gr_drawimage(
  double, double, double, double, int, int, int *, int);
DLLEXPORT int gr_importgraphics(char *);
DLLEXPORT void gr_setshadow(double, double, double);
DLLEXPORT void gr_settransparency(double);
DLLEXPORT void gr_setcoordxform(double [3][2]);
DLLEXPORT void gr_begingraphics(char *);
DLLEXPORT void gr_endgraphics(void);
DLLEXPORT void gr_mathtex(double, double, char *);
DLLEXPORT void gr_beginselection(int, int);
DLLEXPORT void gr_endselection(void);
DLLEXPORT void gr_moveselection(double, double);
DLLEXPORT void gr_resizeselection(int, double, double);
DLLEXPORT void gr_inqbbox(double *, double *, double *, double *);

#ifdef _WIN32
#ifdef __cplusplus
}
#endif
#endif

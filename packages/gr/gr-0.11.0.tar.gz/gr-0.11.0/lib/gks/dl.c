
#include <string.h>
#include <stdlib.h>

#include "gks.h"
#include "gkscore.h"

#define SEGM_SIZE 262144 /* 256K */

#define COPY(s, n) memcpy(d->buffer + d->nbytes, (void *) s, n); d->nbytes += n

static
void reallocate(gks_display_list_t *d, int len)
{
  while (d->nbytes + len > d->size)
    d->size += SEGM_SIZE;

  d->buffer = (char *) gks_realloc(d->buffer, d->size + 1);
}

void gks_dl_write_item(gks_display_list_t *d,
  int fctid, int dx, int dy, int dimx, int *ia,
  int lr1, double *r1, int lr2, double *r2, int lc, char *c,
  gks_state_list_t *gkss)
{
  char s[132];
  int len, slen;

  switch (fctid)
    {
    case   2:                        /* open workstation */

      d->state = GKS_K_WS_INACTIVE;
      d->buffer = (char *) gks_malloc(SEGM_SIZE + 1);
      d->size = SEGM_SIZE;
      d->nbytes = d->position = 0;

      len = 2 * sizeof(int) + sizeof(gks_state_list_t);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(gkss, sizeof(gks_state_list_t));
      break;

    case   3:                        /* close workstation */

      free(d->buffer);
      d->buffer = NULL;
      break;

    case   4:                        /* activate workstation */

      d->state = GKS_K_WS_ACTIVE;
      break;

    case   5:                        /* deactivate workstation */

      d->state = GKS_K_WS_INACTIVE;
      break;

    case   6:                        /* clear workstation */

      d->nbytes = d->position = 0;

      len = 2 * sizeof(int) + sizeof(gks_state_list_t);
      fctid = 2;

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(gkss, sizeof(gks_state_list_t));
      break;

    case  12:                        /* polyline */
    case  13:                        /* polymarker */
    case  15:                        /* fill area */
      if (d->state == GKS_K_WS_ACTIVE)
        {
          len = 3 * sizeof(int) + 2 * ia[0] * sizeof(double);
          if (d->nbytes + len > d->size)
            reallocate(d, len);

          COPY(&len, sizeof(int));
          COPY(&fctid, sizeof(int));
          COPY(ia, sizeof(int));
          COPY(r1, ia[0] * sizeof(double));
          COPY(r2, ia[0] * sizeof(double));
        }
      break;

    case  14:                        /* text */

      if (d->state == GKS_K_WS_ACTIVE)
        {
          len = 3 * sizeof(int) + 2 * sizeof(double) + 132;
          if (d->nbytes + len > d->size)
            reallocate(d, len);

          memset((void *) s, 0, 132);
          slen = strlen(c);
          strncpy(s, c, slen);

          COPY(&len, sizeof(int));
          COPY(&fctid, sizeof(int));
          COPY(r1, sizeof(double));
          COPY(r2, sizeof(double));
          COPY(&slen, sizeof(int));
          COPY(s, 132);
        }
      break;

    case  16:                        /* cell array */
    case 201:                        /* draw image */

      if (d->state == GKS_K_WS_ACTIVE)
        {
          len = (5 + dimx * dy) * sizeof(int) + 4 * sizeof(double);
          if (d->nbytes + len > d->size)
            reallocate(d, len);

          COPY(&len, sizeof(int));
          COPY(&fctid, sizeof(int));
          COPY(r1, 2 * sizeof(double));
          COPY(r2, 2 * sizeof(double));
          COPY(&dx, sizeof(int));
          COPY(&dy, sizeof(int));
          COPY(&dimx, sizeof(int));
          COPY(ia, dimx * dy * sizeof(int));
        }
      break;

    case  19:                        /* set linetype */
    case  21:                        /* set polyline color index */
    case  23:                        /* set markertype */
    case  25:                        /* set polymarker color index */
    case  30:                        /* set text color index */
    case  33:                        /* set text path */
    case  36:                        /* set fillarea interior style */
    case  37:                        /* set fillarea style index */
    case  38:                        /* set fillarea color index */
    case  52:                        /* select normalization transformation */
    case  53:                        /* set clipping indicator */

      len = 3 * sizeof(int);
      if (d->nbytes + len > d->size)
        reallocate(d, len);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(ia, sizeof(int));
      break;

    case  27:                        /* set text font and precision */
    case  34:                        /* set text alignment */

      len = 4 * sizeof(int);
      if (d->nbytes + len > d->size)
        reallocate(d, len);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(ia, 2 * sizeof(int));
      break;

    case  20:                        /* set linewidth scale factor */
    case  24:                        /* set marker size scale factor */
    case  28:                        /* set character expansion factor */
    case  29:                        /* set character spacing */
    case  31:                        /* set character height */
    case 200:                        /* set text slant */
    case 203:                        /* set transparency */

      len = 2 * sizeof(int) + sizeof(double);
      if (d->nbytes + len > d->size)
        reallocate(d, len);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(r1, sizeof(double));
      break;

    case  32:                        /* set character up vector */

      len = 2 * sizeof(int) + 2 * sizeof(double);
      if (d->nbytes + len > d->size)
        reallocate(d, len);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(r1, sizeof(double));
      COPY(r2, sizeof(double));
      break;

    case  41:                        /* set aspect source flags */

      len = 15 * sizeof(int);
      if (d->nbytes + len > d->size)
        reallocate(d, len);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(ia, 13 * sizeof(int));
      break;

    case  48:                        /* set color representation */

      len = 3 * sizeof(int) + 3 * sizeof(double);
      if (d->nbytes + len > d->size)
        reallocate(d, len);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(&ia[1], sizeof(int));
      COPY(r1, 3 * sizeof(double));
      break;

    case  49:                        /* set window */
    case  50:                        /* set viewport */
    case  54:                        /* set workstation window */
    case  55:                        /* set workstation viewport */

      len = 3 * sizeof(int) + 4 * sizeof(double);
      if (d->nbytes + len > d->size)
        reallocate(d, len);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(ia, sizeof(int));
      COPY(r1, 2 * sizeof(double));
      COPY(r2, 2 * sizeof(double));
      break;

    case 202:                        /* set shadow */

      len = 2 * sizeof(int) + 3 * sizeof(double);
      if (d->nbytes + len >= d->size)
	reallocate(d, len);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(r1, 3 * sizeof(double));
      break;

    case 204:                        /* set coord xform */

      len = 2 * sizeof(int) + 6 * sizeof(double);
      if (d->nbytes + len >= d->size)
	reallocate(d, len);

      COPY(&len, sizeof(int));
      COPY(&fctid, sizeof(int));
      COPY(r1, 6 * sizeof(double));
      break;
    }

  if (d->buffer != NULL)
    {
      if (d->nbytes + 4 > d->size)
        reallocate(d, 4);

      memset(d->buffer + d->nbytes, 0, 4);
    }
}

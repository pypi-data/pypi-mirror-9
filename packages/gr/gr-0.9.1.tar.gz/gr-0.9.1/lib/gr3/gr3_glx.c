#define GR3_GLX_C
#include <stdlib.h>
#include "gr3.h"
#include "gr3_glx.h"
#include "gr3_internals.h"

/* OpenGL Context creation using GLX */

static Display *display; /*!< The used X display */
static Pixmap pixmap; /*!< The XPixmap (GLX < 1.4)*/
static GLXPbuffer pbuffer; /*!< The GLX Pbuffer (GLX >=1.4) */
static GLXContext context; /*!< The GLX context */

/*!
 * This function implements OpenGL context creation using GLX
 * and a Pbuffer if GLX version is 1.4 or higher, or a XPixmap
 * otherwise.
 * \returns
 * - ::GR3_ERROR_NONE         on success
 * - ::GR3_ERROR_INIT_FAILED  if initialization failed
 */
int gr3_initGL_GLX_(void) {
  int major, minor;
  int fbcount;
  GLXFBConfig *fbc;
  GLXFBConfig fbconfig;
  gr3_log_("gr3_initGL_GLX_();");
  
  display = XOpenDisplay(0);
  if (!display) {
    gr3_log_("Not connected to an X server!");
    return GR3_ERROR_INIT_FAILED;
  }
  
  context = glXGetCurrentContext();
  if (context != NULL) {
    gr3_appendtorenderpathstring_("GLX (existing context)");
  } else {
    glXQueryVersion(display,&major,&minor);
    if (major > 1 || minor >=4) {
      int fb_attribs[] =
      {
        GLX_DRAWABLE_TYPE   , GLX_PBUFFER_BIT,
        GLX_RENDER_TYPE     , GLX_RGBA_BIT,
        None
      };
      int pbuffer_attribs[] =
      {
        GLX_PBUFFER_WIDTH   , 1,
        GLX_PBUFFER_HEIGHT   , 1,
        None
      };
      gr3_log_("(Pbuffer)");
      
      fbc = glXChooseFBConfig(display, DefaultScreen(display), fb_attribs,
                              &fbcount);
      if (fbcount == 0) {
        gr3_log_("failed to find a valid a GLX FBConfig for a RGBA PBuffer");
        XFree(fbc);
        XCloseDisplay(display);
        return GR3_ERROR_INIT_FAILED;
      }
      fbconfig = fbc[0];
      XFree(fbc);
      pbuffer = glXCreatePbuffer(display, fbconfig, pbuffer_attribs);
      
      context = glXCreateNewContext(display, fbconfig, GLX_RGBA_TYPE, None, True);
      glXMakeContextCurrent(display,pbuffer,pbuffer,context);
      
      context_struct_.terminateGL = gr3_terminateGL_GLX_Pbuffer_;
      context_struct_.gl_is_initialized = 1;
      gr3_appendtorenderpathstring_("GLX (Pbuffer)");
    } else {
      XVisualInfo *visual;
      int fb_attribs[] =
      {
        GLX_DRAWABLE_TYPE   , GLX_PIXMAP_BIT,
        GLX_RENDER_TYPE     , GLX_RGBA_BIT,
        None
      };
      gr3_log_("(XPixmap)");
      fbc = glXChooseFBConfig(display, DefaultScreen(display), fb_attribs,
                              &fbcount);
      if (fbcount == 0) {
        gr3_log_("failed to find a valid a GLX FBConfig for a RGBA Pixmap");
        XFree(fbc);
        XCloseDisplay(display);
        return GR3_ERROR_INIT_FAILED;
      }
      fbconfig = fbc[0];
      XFree(fbc);
      
      context = glXCreateNewContext(display, fbconfig, GLX_RGBA_TYPE, None, True);
      visual = glXGetVisualFromFBConfig(display,fbconfig);
      pixmap = XCreatePixmap(display,XRootWindow(display,DefaultScreen(display)),1,1,visual->depth);
      
      if (glXMakeContextCurrent(display,pixmap,pixmap,context)) {
        context_struct_.terminateGL = gr3_terminateGL_GLX_Pixmap_;
        context_struct_.gl_is_initialized = 1;
        gr3_appendtorenderpathstring_("GLX (XPixmap)");
      } else {
        gr3_log_("failed to make GLX OpenGL Context current with a Pixmap");
        glXDestroyContext(display, context);
        XFreePixmap(display,pixmap);
        XCloseDisplay(display);
        return GR3_ERROR_INIT_FAILED;
      }
    }
  }
  /* Load Function pointers */ {
#ifdef GR3_CAN_USE_VBO
    glBufferData = (PFNGLBUFFERDATAPROC)glXGetProcAddress((const GLubyte *)"glBufferData");
    glBindBuffer = (PFNGLBINDBUFFERPROC)glXGetProcAddress((const GLubyte *)"glBindBuffer");
    glGenBuffers = (PFNGLGENBUFFERSPROC)glXGetProcAddress((const GLubyte *)"glGenBuffers");
    glDeleteBuffers = (PFNGLGENBUFFERSPROC)glXGetProcAddress((const GLubyte *)"glDeleteBuffers");
    glVertexAttribPointer = (PFNGLVERTEXATTRIBPOINTERPROC)glXGetProcAddress((const GLubyte *)"glVertexAttribPointer");
    glGetAttribLocation = (PFNGLGETATTRIBLOCATIONPROC)glXGetProcAddress((const GLubyte *)"glGetAttribLocation");
    glEnableVertexAttribArray = (PFNGLENABLEVERTEXATTRIBARRAYPROC)glXGetProcAddress((const GLubyte *)"glEnableVertexAttribArray");
    glUseProgram = (PFNGLUSEPROGRAMPROC)glXGetProcAddress((const GLubyte *)"glUseProgram");
    glDeleteShader = (PFNGLDELETESHADERPROC)glXGetProcAddress((const GLubyte *)"glDeleteShader");
    glLinkProgram = (PFNGLLINKPROGRAMPROC)glXGetProcAddress((const GLubyte *)"glLinkProgram");
    glAttachShader = (PFNGLATTACHSHADERPROC)glXGetProcAddress((const GLubyte *)"glAttachShader");
    glCreateShader = (PFNGLCREATESHADERPROC)glXGetProcAddress((const GLubyte *)"glCreateShader");
    glCompileShader = (PFNGLCOMPILESHADERPROC)glXGetProcAddress((const GLubyte *)"glCompileShader");
    glCreateProgram = (PFNGLCREATEPROGRAMPROC)glXGetProcAddress((const GLubyte *)"glCreateProgram");
    glDeleteProgram = (PFNGLDELETEPROGRAMPROC)glXGetProcAddress((const GLubyte *)"glDeleteProgram");
    glUniform3f = (PFNGLUNIFORM3FPROC)glXGetProcAddress((const GLubyte *)"glUniform3f");
    glUniformMatrix4fv = (PFNGLUNIFORMMATRIX4FVPROC)glXGetProcAddress((const GLubyte *)"glUniformMatrix4fv");
    glUniform4f = (PFNGLUNIFORM4FPROC)glXGetProcAddress((const GLubyte *)"glUniform4f");
    glGetUniformLocation = (PFNGLGETUNIFORMLOCATIONPROC)glXGetProcAddress((const GLubyte *)"glGetUniformLocation");
    glShaderSource = (PFNGLSHADERSOURCEPROC)glXGetProcAddress((const GLubyte *)"glShaderSource");
#endif
    glDrawBuffers = (PFNGLDRAWBUFFERSPROC)glXGetProcAddress((const GLubyte *)"glDrawBuffers");
    /*glBlendColor = (PFNGLBLENDCOLORPROC)glXGetProcAddress((const GLubyte *)"glBlendColor");*/
#ifdef GL_ARB_framebuffer_object
    glBindRenderbuffer = (PFNGLBINDRENDERBUFFERPROC)glXGetProcAddress((const GLubyte *)"glBindRenderbuffer");
    glCheckFramebufferStatus = (PFNGLCHECKFRAMEBUFFERSTATUSPROC)glXGetProcAddress((const GLubyte *)"glCheckFramebufferStatus");
    glFramebufferRenderbuffer = (PFNGLFRAMEBUFFERRENDERBUFFERPROC)glXGetProcAddress((const GLubyte *)"glFramebufferRenderbuffer");
    glRenderbufferStorage = (PFNGLRENDERBUFFERSTORAGEPROC)glXGetProcAddress((const GLubyte *)"glRenderbufferStorage");
    glBindFramebuffer = (PFNGLBINDFRAMEBUFFERPROC)glXGetProcAddress((const GLubyte *)"glBindFramebuffer");
    glGenFramebuffers = (PFNGLGENFRAMEBUFFERSPROC)glXGetProcAddress((const GLubyte *)"glGenFramebuffers");
    glGenRenderbuffers = (PFNGLGENRENDERBUFFERSPROC)glXGetProcAddress((const GLubyte *)"glGenRenderbuffers");
    glDeleteFramebuffers = (PFNGLDELETEFRAMEBUFFERSPROC)glXGetProcAddress((const GLubyte *)"glDeleteFramebuffers");
    glDeleteRenderbuffers = (PFNGLDELETERENDERBUFFERSPROC)glXGetProcAddress((const GLubyte *)"glDeleteRenderbuffers");
#endif
#ifdef GL_EXT_framebuffer_object
    glBindRenderbufferEXT = (PFNGLBINDRENDERBUFFEREXTPROC)glXGetProcAddress((const GLubyte *)"glBindRenderbufferEXT");
    glCheckFramebufferStatusEXT = (PFNGLCHECKFRAMEBUFFERSTATUSEXTPROC)glXGetProcAddress((const GLubyte *)"glCheckFramebufferStatusEXT");
    glFramebufferRenderbufferEXT = (PFNGLFRAMEBUFFERRENDERBUFFEREXTPROC)glXGetProcAddress((const GLubyte *)"glFramebufferRenderbufferEXT");
    glRenderbufferStorageEXT = (PFNGLRENDERBUFFERSTORAGEEXTPROC)glXGetProcAddress((const GLubyte *)"glRenderbufferStorageEXT");
    glBindFramebufferEXT = (PFNGLBINDFRAMEBUFFEREXTPROC)glXGetProcAddress((const GLubyte *)"glBindFramebufferEXT");
    glGenFramebuffersEXT = (PFNGLGENFRAMEBUFFERSEXTPROC)glXGetProcAddress((const GLubyte *)"glGenFramebuffersEXT");
    glGenRenderbuffersEXT = (PFNGLGENRENDERBUFFERSEXTPROC)glXGetProcAddress((const GLubyte *)"glGenRenderbuffersEXT");
    glDeleteFramebuffersEXT = (PFNGLDELETEFRAMEBUFFERSEXTPROC)glXGetProcAddress((const GLubyte *)"glDeleteFramebuffersEXT");
    glDeleteRenderbuffersEXT = (PFNGLDELETERENDERBUFFERSEXTPROC)glXGetProcAddress((const GLubyte *)"glDeleteRenderbuffersEXT");
#endif
  }
  return GR3_ERROR_NONE;
}

/*!
 * This function destroys the OpenGL context using GLX with a Pbuffer.
 */
void gr3_terminateGL_GLX_Pbuffer_(void) {
  gr3_log_("gr3_terminateGL_GLX_Pbuffer_();");
  
  glXMakeContextCurrent(display,None,None,NULL);
  glXDestroyContext(display, context);
  /*glXDestroyPbuffer(display, pbuffer);*/
  XCloseDisplay(display);
  context_struct_.gl_is_initialized = 0;
}

/*!
 * This function destroys the OpenGL context using GLX with a XPixmap.
 */
void gr3_terminateGL_GLX_Pixmap_(void) {
  gr3_log_("gr3_terminateGL_GLX_Pixmap_();");
  
  glXMakeContextCurrent(display,None,None,NULL);
  glXDestroyContext(display, context);
  XFreePixmap(display,pixmap);
  XCloseDisplay(display);
  context_struct_.gl_is_initialized = 0;
}

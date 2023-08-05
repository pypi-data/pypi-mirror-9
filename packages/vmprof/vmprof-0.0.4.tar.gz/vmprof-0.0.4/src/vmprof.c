/* VMPROF
 *
 * statistical sampling profiler specifically designed to profile programs
 * which run on a Virtual Machine and/or bytecode interpreter, such as Python,
 * etc.
 *
 * The logic to dump the C stack traces is partly stolen from the code in gperftools.
 * The file "getpc.h" has been entirely copied from gperftools.
 *
 * Tested only on gcc, linux, x86_64.
 *
 * Copyright (C) 2014-2015
 *   Antonio Cuni - anto.cuni@gmail.com
 *   Maciej Fijalkowski - fijall@gmail.com
 *
 */


#include "getpc.h"      // should be first to get the _GNU_SOURCE dfn
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include <assert.h>
#include <unistd.h>
#include <sys/time.h>
#include <sys/types.h>

#define UNW_LOCAL_ONLY
#include <libunwind.h>

#include "vmprof.h"

#define _unused(x) ((void)x)

#define MAX_FUNC_NAME 128
#define MAX_STACK_DEPTH 64

static FILE* profile_file = NULL;
void* vmprof_mainloop_func;
static ptrdiff_t mainloop_sp_offset;
static vmprof_get_virtual_ip_t mainloop_get_virtual_ip;


/* *************************************************************
 * functions to write a profile file compatible with gperftools
 * *************************************************************
 */

#define MARKER_STACKTRACE '\x01'
#define MARKER_VIRTUAL_IP '\x02'
#define MARKER_TRAILER '\x03'

static void prof_word(FILE* f, long x) {
    fwrite(&x, sizeof(x), 1, f);
}

static void prof_header(FILE* f, long period_usec) {
    prof_word(f, 0);
    prof_word(f, 3);
    prof_word(f, 0);
    prof_word(f, period_usec);
    prof_word(f, 0);
}

static void prof_write_stacktrace(FILE* f, void** stack, int depth, int count) {
    int i;
	char marker = MARKER_STACKTRACE;

	fwrite(&marker, 1, 1, f);
    prof_word(f, count);
    prof_word(f, depth);
    for(i=0; i<depth; i++)
        prof_word(f, (long)stack[i]);
}


/* ******************************************************
 * libunwind workaround for process JIT frames correctly
 * ******************************************************
 */

#include "get_custom_offset.c"

typedef struct {
    void* _unused1;
    void* _unused2;
    void* sp;
    void* ip;
    void* _unused3[sizeof(unw_cursor_t)/sizeof(void*) - 4];
} vmprof_hacked_unw_cursor_t;

static int vmprof_unw_step(unw_cursor_t *cp) {
	void* ip;
    void* sp;
    ptrdiff_t sp_offset;
    unw_get_reg (cp, UNW_REG_IP, (unw_word_t*)&ip);
    unw_get_reg (cp, UNW_REG_SP, (unw_word_t*)&sp);
    sp_offset = vmprof_unw_get_custom_offset(ip, cp);

    if (sp_offset == -1) {
        // it means that the ip is NOT in JITted code, so we can use the
        // stardard unw_step
        return unw_step(cp);
    }
    else {
        // this is a horrible hack to manually walk the stack frame, by
        // setting the IP and SP in the cursor
        vmprof_hacked_unw_cursor_t *cp2 = (vmprof_hacked_unw_cursor_t*)cp;
        void* bp = (void*)sp + sp_offset;
        cp2->sp = bp;
		bp -= sizeof(void*);
        cp2->ip = ((void**)bp)[0];
        // the ret is on the top of the stack minus WORD
        return 1;
    }
}


/* *************************************************************
 * functions to dump the stack trace
 * *************************************************************
 */

// stolen from pprof:
// Sometimes, we can try to get a stack trace from within a stack
// trace, because libunwind can call mmap (maybe indirectly via an
// internal mmap based memory allocator), and that mmap gets trapped
// and causes a stack-trace request.  If were to try to honor that
// recursive request, we'd end up with infinite recursion or deadlock.
// Luckily, it's safe to ignore those subsequent traces.  In such
// cases, we return 0 to indicate the situation.
//static __thread int recursive;
static int recursive; // XXX antocuni: removed __thread

int get_stack_trace(void** result, int max_depth, ucontext_t *ucontext) {
    void *ip;
    int n = 0;
    unw_cursor_t cursor;
    unw_context_t uc = *ucontext;
    if (recursive) {
        return 0;
    }
    ++recursive;

    int ret = unw_init_local(&cursor, &uc);
    assert(ret >= 0);
    _unused(ret);

    while (n < max_depth) {
        if (unw_get_reg(&cursor, UNW_REG_IP, (unw_word_t *) &ip) < 0) {
            break;
        }

        unw_proc_info_t pip;
        unw_get_proc_info(&cursor, &pip);

        /* char funcname[4096]; */
        /* unw_word_t offset; */
        /* unw_get_proc_name(&cursor, funcname, 4096, &offset); */
        /* printf("%s+%#lx <%p>\n", funcname, offset, ip); */

        /* if n==0, it means that the signal handler interrupted us while we
           were in the trampoline, so we are not executing (yet) the real main
           loop function; just skip it */
        if (vmprof_mainloop_func && 
            (void*)pip.start_ip == (void*)vmprof_mainloop_func &&
            n > 0) {
          // found main loop stack frame
          void* sp;
          unw_get_reg(&cursor, UNW_REG_SP, (unw_word_t *) &sp);
          void *arg_addr = (char*)sp + mainloop_sp_offset;
          void **arg_ptr = (void**)arg_addr;
          // fprintf(stderr, "stacktrace mainloop: rsp %p   &f2 %p   offset %ld\n", 
          //         sp, arg_addr, mainloop_sp_offset);
          ip = mainloop_get_virtual_ip(*arg_ptr);
        }

        result[n++] = ip;
		n = vmprof_write_header_for_jit_addr(result, n, ip, max_depth);
        if (vmprof_unw_step(&cursor) <= 0) {
            break;
        }
    }
    --recursive;
    return n;
}


static int __attribute__((noinline)) frame_forcer(int rv) {
    return rv;
}

static void sigprof_handler(int sig_nr, siginfo_t* info, void *ucontext) {
    void* stack[MAX_STACK_DEPTH];
    stack[0] = GetPC((ucontext_t*)ucontext);
    int depth = frame_forcer(get_stack_trace(stack+1, MAX_STACK_DEPTH-1, ucontext));
    depth++;  // To account for pc value in stack[0];
    prof_write_stacktrace(profile_file, stack, depth, 1);
}

/* *************************************************************
 * functions to enable/disable the profiler
 * *************************************************************
 */

static int open_profile(int fd, long period_usec, int write_header, char *s,
						int slen) {
	if ((fd = dup(fd)) == -1) {
		return -1;
	}
    profile_file = fdopen(fd, "wb");
	if (!profile_file) {
		return -1;
	}
	if (write_header)
		prof_header(profile_file, period_usec);
	if (s)
		fwrite(s, slen, 1, profile_file);
	return 0;
}

static int close_profile(void) {
	// XXX all of this can happily fail
    FILE* src;
    char buf[BUFSIZ];
    size_t size;
	int marker = MARKER_TRAILER;
	fwrite(&marker, 1, 1, profile_file);

    // copy /proc/PID/maps to the end of the profile file
    sprintf(buf, "/proc/%d/maps", getpid());
    src = fopen(buf, "r");    
    while ((size = fread(buf, 1, BUFSIZ, src))) {
        fwrite(buf, 1, size, profile_file);
    }
    fclose(src);
    fclose(profile_file);
	return 0;
}


static int install_sigprof_handler(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = sigprof_handler;
    sa.sa_flags = SA_RESTART | SA_SIGINFO;
    if (sigemptyset(&sa.sa_mask) == -1 ||
		sigaction(SIGPROF, &sa, NULL) == -1) {
		return -1;
	}
	return 0;
}

static int remove_sigprof_handler(void) {
    //sighandler_t res = signal(SIGPROF, SIG_DFL);
	//if (res == SIG_ERR) {
	//	return -1;
	//}
	return 0;
};

static int install_sigprof_timer(long period_usec) {
    static struct itimerval timer;
    timer.it_interval.tv_sec = 0;
    timer.it_interval.tv_usec = period_usec;
    timer.it_value = timer.it_interval;
    if (setitimer(ITIMER_PROF, &timer, NULL) != 0) {
		return -1;
    }
	return 0;
}

static int remove_sigprof_timer(void) {
    static struct itimerval timer;
    timer.it_interval.tv_sec = 0;
    timer.it_interval.tv_usec = 0;
    timer.it_value = timer.it_interval;
    if (setitimer(ITIMER_PROF, &timer, NULL) != 0) {
		return -1;
    }
	return 0;
}

/* *************************************************************
 * public API
 * *************************************************************
 */

void vmprof_set_mainloop(void* func, ptrdiff_t sp_offset, 
                         vmprof_get_virtual_ip_t get_virtual_ip) {
    vmprof_mainloop_func = func;
    mainloop_sp_offset = sp_offset;
    mainloop_get_virtual_ip = get_virtual_ip;
}

int vmprof_enable(int fd, long period_usec, int write_header, char *s,
				  int slen)
{
    if (period_usec == -1)
        period_usec = 1000000 / 100; /* 100hz */
    if (open_profile(fd, period_usec, write_header, s, slen) == -1) {
		return -1;
	}
    if (install_sigprof_handler() == -1) {
		return -1;
	}
    if (install_sigprof_timer(period_usec) == -1) {
		return -1;
	}
	return 0;
}

int vmprof_disable(void) {
    if (remove_sigprof_timer() == -1) {
		return -1;
	}
    if (remove_sigprof_handler() == -1) {
		return -1;
	}
    if (close_profile() == -1) {
		return -1;
	}
	return 0;
}

void vmprof_register_virtual_function(const char* name, void* start, void* end) {
    // for now *end is simply ignored
	char buf[1024];
	int lgt = strlen(name) + 2 * sizeof(long) + 1;

	if (lgt > 1024) {
		lgt = 1024;
	}
	buf[0] = MARKER_VIRTUAL_IP;
	((void **)(((void*)buf) + 1))[0] = start;
	((long *)(((void*)buf) + 1 + sizeof(long)))[0] = lgt - 2 * sizeof(long) - 1;
	strncpy(buf + 2 * sizeof(long) + 1, name, 1024 - 2 * sizeof(long) - 1);
	fwrite(buf, lgt, 1, profile_file);
}

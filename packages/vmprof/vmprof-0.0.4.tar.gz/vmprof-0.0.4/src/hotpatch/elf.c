#define HAVE_ELF
#if defined(HAVE_ELF)
#define _GNU_SOURCE
#include "bin_api.h"
#include "arch.h"
#include "util.h"

#include <assert.h>
#include <dwarf.h>
#include <err.h>
#include <error.h>
#include <errno.h>
#include <fcntl.h>
#include <libdwarf.h>
#include <libelf/gelf.h>
#include <libgen.h>
#include <limits.h>
#include <link.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sysexits.h>
#include <unistd.h>

#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

extern struct memprof_config memprof_config;

/* The size of a PLT entry */
#define PLT_ENTRY_SZ  (16)

/* The system-wide debug symbol directory */
/* XXX this should be set via extconf and not hardcoded */
#define DEBUGDIR   "/usr/lib/debug"

/* Keep track of whether this ruby is built with a shared library or not */
static int libruby = 0;

static Dwarf_Debug dwrf = NULL;

/* Set of ELF specific state about this Ruby binary/shared object */
static struct elf_info *ruby_info = NULL;

struct elf_info {
  int fd;
  Elf *elf;

  GElf_Addr base_addr;

  void *text_segment;
  size_t text_segment_len;

  GElf_Addr got_addr;

  GElf_Addr relplt_addr;
  Elf_Data *relplt;
  size_t relplt_count;

  GElf_Addr plt_addr;
  Elf_Data *plt;
  size_t plt_size;
  size_t plt_count;

  Elf_Data *debuglink_data;

  GElf_Ehdr ehdr;

  Elf_Data *dynsym;
  size_t dynsym_count;
  const char *dynstr;

  GElf_Shdr symtab_shdr;
  Elf_Data *symtab_data;

  const char *filename;

  struct elf_info *debug_data;
};

/* These callback return statuses are used to tell the invoker of the callback
 * (walk_linkmap) whether to continue walking or bail out.
 */
typedef enum {
  CB_CONTINUE,
  CB_EXIT,
} linkmap_cb_status;

/* A callback type that specifies a function that can be fired on each link map
 * entry.
 */
typedef linkmap_cb_status (*linkmap_cb)(struct link_map *, void *);
typedef void (*linkmap_lib_cb)(struct elf_info *lib, void *data);

static void open_elf(struct elf_info *info);
static int dissect_elf(struct elf_info *info, int find_debug);
static void *find_plt_addr(const char *symname, struct elf_info *info);
static void walk_linkmap(linkmap_cb cb, void *data);

/*
 * plt_entry - procedure linkage table entry
 *
 * This struct is intended to be "laid onto" a piece of memory to ease the
 * parsing, use, modification, and length calculation of PLT entries.
 *
 * For example:
 *    jmpq  *0xaaf00d(%rip)   # jump to GOT entry
 *
 *    # the following instructions are only hit if function has not been
 *    # resolved previously.
 *
 *    pushq  $0x4e            # push ID
 *    jmpq  0xcafebabefeedface # invoke the link linker
 */
struct plt_entry {
    unsigned char jmp[2];
    int32_t jmp_disp;

    /* There is no reason (currently) to represent the pushq and jmpq
     * instructions which invoke the linker.
     *
     * We don't need those to hook the GOT; we only need the jmp_disp above.
     *
     * TODO represent the extra instructions
     */
    unsigned char pad[10];
} __attribute__((__packed__));

/*
 * get_got_addr - given a PLT entry, return the global offset table entry that
 * the entry uses.
 */
static void *
get_got_addr(struct plt_entry *plt, struct elf_info *info)
{
  void *addr = NULL;

  assert(plt != NULL);
  assert(plt->jmp[0] == 0xff);

  if (plt->jmp[1] == 0x25) {
#if defined(_ARCH_x86_64_)
    // jmpq   *0x2ccf3a(%rip)
    addr = (void *)&(plt->pad) + plt->jmp_disp;
#else
    // jmp    *0x81060f0
    addr = (void *)(plt->jmp_disp);
#endif
  } else if (plt->jmp[1] == 0xa3) {
    // jmp    *0x130(%ebx)
    addr = (void *)(info->base_addr + info->got_addr + plt->jmp_disp);
  }

  dbg_printf("PLT addr: %p, .got.plt slot: %p\n", plt, addr);
  return addr;
}

/*
 * overwrite_got - given the address of a PLT entry, overwrite the address
 * in the GOT that the PLT entry uses with the address in tramp.
 *
 * returns the original function address
 */
static void *
overwrite_got(void *plt, const void *tramp, struct elf_info *info)
{
  assert(plt != NULL);
  assert(tramp != NULL);
  void *ret = NULL;

  memcpy(&ret, get_got_addr(plt, info), sizeof(void *));
  copy_instructions(get_got_addr(plt, info), &tramp, sizeof(void *));
  dbg_printf("GOT value overwritten to: %p, from: %p\n", tramp, ret);
  return ret;
}

struct plt_hook_data {
  const char *sym;
  void *addr;
};

struct dso_iter_data {
  linkmap_lib_cb cb;
  void *passthru;
};

static linkmap_cb_status
for_each_dso_cb(struct link_map *map, void *data)
{
  struct dso_iter_data *iter_data = data;
  struct elf_info curr_lib;

  /* skip a few things we don't care about */
  if (strstr(map->l_name, "linux-vdso")) {
    dbg_printf("found vdso (skipping): %s\n", map->l_name);
    return CB_CONTINUE;
  } else if (strstr(map->l_name, "ld-linux")) {
    dbg_printf("found ld-linux (skipping): %s\n", map->l_name);
    return CB_CONTINUE;
  } else if (strstr(map->l_name, "libruby")) {
    dbg_printf("found libruby (skipping): %s\n", map->l_name);
    return CB_CONTINUE;
  } else if (strstr(map->l_name, "memprof")) {
    dbg_printf("found memprof (skipping): %s\n", map->l_name);
    return CB_CONTINUE;
  } else if (!map->l_name || map->l_name[0] == '\0') {
    dbg_printf("found an empty string (skipping)\n");
    return CB_CONTINUE;
  }
  memset(&curr_lib, 0, sizeof(curr_lib));
  dbg_printf("trying to open elf object: %s\n", map->l_name);
  curr_lib.filename = map->l_name;
  open_elf(&curr_lib);

  if (curr_lib.elf == NULL) {
    dbg_printf("opening the elf object (%s) failed! (skipping)\n", map->l_name);
    return CB_CONTINUE;
  }

  curr_lib.base_addr = map->l_addr;
  curr_lib.filename = map->l_name;

  if (dissect_elf(&curr_lib, 0) == 2) {
    dbg_printf("elf file, %s hit an unrecoverable error (skipping)\n", map->l_name);
    elf_end(curr_lib.elf);
    close(curr_lib.fd);
    return CB_CONTINUE;
  }

  dbg_printf("dissected the elf file: %s, base: %lx\n",
      curr_lib.filename, (unsigned long)curr_lib.base_addr);

  iter_data->cb(&curr_lib, iter_data->passthru);

  elf_end(curr_lib.elf);
  close(curr_lib.fd);
  return CB_CONTINUE;
}

static void
for_each_dso(linkmap_lib_cb cb, void *passthru)
{
  struct dso_iter_data data;
  data.cb = cb;
  data.passthru = passthru;
  walk_linkmap(for_each_dso_cb, &data);
}

static void
hook_required_objects(struct elf_info *info, void *data)
{
  assert(info != NULL);
  struct plt_hook_data *hook_data = data;
  void *trampee_addr = NULL;

  if ((trampee_addr = find_plt_addr(hook_data->sym, info)) != NULL) {
    dbg_printf("found: %s @ %p\n", hook_data->sym, trampee_addr);
    overwrite_got(trampee_addr, hook_data->addr, info);
  }

  return;
}

/*
 * do_bin_allocate_page - internal page allocation routine
 *
 * This function allocates a page suitable for stage 2 trampolines. This page
 * is allocated based on the location of the text segment of the Ruby binary
 * or libruby.
 *
 * The page has to be located in a 32bit window from the Ruby code so that
 * jump and call instructions can redirect execution there.
 *
 * This function returns the address of the page found or NULL if no page was
 * found.
 */
static void *
do_bin_allocate_page(struct elf_info *info)
{
  void * ret = NULL, *addr = NULL;
  uint32_t count = 0;

  if (!info)
    return NULL;

  if (libruby) {
    /* There is a libruby. Start at the end of the text segment and search for
     * a page.
     */
    addr = info->text_segment + info->text_segment_len;
    for (; count < USHRT_MAX; addr += memprof_config.pagesize, count += memprof_config.pagesize) {
      ret = mmap(addr, memprof_config.pagesize, PROT_WRITE|PROT_READ|PROT_EXEC, MAP_ANON|MAP_PRIVATE, -1, 0);
      if (ret != MAP_FAILED) {
        memset(ret, 0x90, memprof_config.pagesize);
        return ret;
      }
    }
  } else {
    /* if there is no libruby, use the linux specific MAP_32BIT flag which will
     * grab a page in the lower 4gb of the address space.
     */
    assert((size_t)info->text_segment <= UINT_MAX);
#ifndef MAP_32BIT
#define MAP_32BIT 0 // no MAP_32BIT defined on certain 32bit systems
#endif
    return mmap(NULL, memprof_config.pagesize, PROT_WRITE|PROT_READ|PROT_EXEC, MAP_ANON|MAP_PRIVATE|MAP_32BIT, -1, 0);
  }

  return NULL;
}

/*
 * bin_allocate_page - allocate a page suitable for holding stage 2 trampolines
 *
 * This function is just a wrapper which passes through some internal state.
 */
void *
bin_allocate_page()
{
  return do_bin_allocate_page(ruby_info);
}

/*
 * get_plt_addr - architecture specific PLT entry retrieval
 *
 * Given the internal data and an index, this function returns the address of
 * the PLT entry at that address.
 *
 * A PLT entry takes the form:
 *
 * jmpq *0xfeedface(%rip)
 * pushq $0xaa
 * jmpq 17110
 */
static inline GElf_Addr
get_plt_addr(struct elf_info *info, size_t ndx) {
  assert(info != NULL);
  dbg_printf("file: %s, base: %lx\n", info->filename, (unsigned long)info->base_addr);
  return info->base_addr + info->plt_addr + (ndx + 1) * PLT_ENTRY_SZ;
}

/*
 * find_got_addr - find the global offset table entry for specific symbol name.
 *
 * Given:
 *  - syname - the symbol name
 *  - info   - internal information about the ELF object to search
 *
 * This function searches the .rela.plt section of an ELF binary, searcing for
 * entries that match the symbol name passed in. If one is found, the address
 * of corresponding entry in .plt is returned.
 */
static void *
find_plt_addr(const char *symname, struct elf_info *info)
{
  assert(symname != NULL);

  size_t i = 0;

  if (info == NULL) {
    info = ruby_info;
  }

  assert(info != NULL);

  /* Search through each of the .rela.plt entries */
  for (i = 0; i < info->relplt_count; i++) {
    GElf_Rel rel;
    GElf_Rela rela;
    GElf_Sym sym;
    GElf_Addr addr;
    void *ret = NULL;
    const char *name;

    if (info->relplt->d_type == ELF_T_RELA) {
      ret = gelf_getrela(info->relplt, i, &rela);
      if (ret == NULL
          || ELF64_R_SYM(rela.r_info) >= info->dynsym_count
          || gelf_getsym(info->dynsym, ELF64_R_SYM(rela.r_info), &sym) == NULL)
        continue;

    } else if (info->relplt->d_type == ELF_T_REL) {
      ret = gelf_getrel(info->relplt, i, &rel);
      if (ret == NULL
          || ELF64_R_SYM(rel.r_info) >= info->dynsym_count
          || gelf_getsym(info->dynsym, ELF64_R_SYM(rel.r_info), &sym) == NULL)
        continue;
    } else {
      dbg_printf("unknown relplt entry type: %d\n", info->relplt->d_type);
      continue;
    }

    name = info->dynstr + sym.st_name;

    /* The name matches the name of the symbol passed in, so get the PLT entry
     * address and return it.
     */
    if (strcmp(symname, name) == 0) {
      addr = get_plt_addr(info, i);
      return (void *)addr;
    }
  }

  return NULL;
}

/*
 * do_bin_find_symbol - internal symbol lookup function.
 *
 * Given:
 *  - sym - the symbol name to look up
 *  - size - an optional out argument holding the size of the symbol
 *  - elf - an elf information structure
 *
 * This function will return the address of the symbol (setting size if desired)
 * or NULL if nothing can be found.
 */
static void *
do_bin_find_symbol(const char *sym, size_t *size, struct elf_info *elf)
{
  const char *name = NULL;

  assert(sym != NULL);
  assert(elf != NULL);

  ElfW(Sym) *esym, *lastsym = NULL;
  if (elf->symtab_data && elf->symtab_data->d_buf) {
    dbg_printf("checking symtab....\n");
    esym = (ElfW(Sym)*) elf->symtab_data->d_buf;
    lastsym = (ElfW(Sym)*) ((char*) elf->symtab_data->d_buf + elf->symtab_data->d_size);

    assert(esym <= lastsym);

    for (; esym < lastsym; esym++){
      /* ignore numeric/empty symbols */
      if ((esym->st_value == 0) ||
          (ELF32_ST_BIND(esym->st_info)== STB_NUM))
        continue;

      name = elf_strptr(elf->elf, elf->symtab_shdr.sh_link, (size_t)esym->st_name);

      if (name && strcmp(name, sym) == 0) {
        if (size) {
          *size = esym->st_size;
        }
        dbg_printf("Found symbol: %s in symtab\n", sym);
        return elf->base_addr + (void *)esym->st_value;
      }
    }
  }

  if (elf->dynsym && elf->dynsym->d_buf) {
    dbg_printf("checking dynsymtab....\n");
    esym = (ElfW(Sym) *) elf->dynsym->d_buf;
    lastsym = (ElfW(Sym) *) ((char *) elf->dynsym->d_buf + elf->dynsym->d_size);

    for (; esym < lastsym; esym++){
      /* ignore numeric/empty symbols */
      if ((esym->st_value == 0) ||
          (elf->dynstr == 0) ||
          (ELF32_ST_BIND(esym->st_info)== STB_NUM))
        continue;

      name = elf->dynstr + esym->st_name;

      if (name && strcmp(name, sym) == 0) {
        if (size) {
          *size = esym->st_size;
        }
        dbg_printf("Found symbol: %s in dynsym\n", sym);
        return elf->base_addr + (void *)esym->st_value;
      }
    }
  }

  dbg_printf("Couldn't find symbol: %s in dynsym\n", sym);
  return NULL;
}

static void
find_symbol_cb(struct elf_info *info, void *data)
{
  assert(info != NULL);
  void *trampee_addr = NULL;
  struct plt_hook_data *hook_data = data;
  void *ret = do_bin_find_symbol(hook_data->sym, NULL, info);
  if (ret) {
    hook_data->addr = ret;
    dbg_printf("found %s @ %p, fn addr: %p\n", hook_data->sym, trampee_addr,
        hook_data->addr);
  }
}

/*
 * bin_find_symbol - find the address of a given symbol and set its size if
 * desired.
 *
 * This function is just a wrapper for the internal symbol lookup function.
 */
void *
bin_find_symbol(const char *sym, size_t *size, int search_libs)
{
  void *ret = do_bin_find_symbol(sym, size, ruby_info);

  if (!ret && search_libs) {
    dbg_printf("Didn't find symbol: %s in ruby, searching other libs\n", sym);
    struct plt_hook_data hd;
    hd.sym = sym;
    hd.addr = NULL;
    for_each_dso(find_symbol_cb, &hd);
    ret = hd.addr;
  }

  return ret;
}

/*
 * do_bin_find_symbol_name - internal symbol name lookup function.
 *
 * Given:
 *  - sym - the symbol address to look up
 *  - elf - an elf information structure
 *
 * This function will return the name of the symbol
 * or NULL if nothing can be found.
 */
static const char *
do_bin_find_symbol_name(void *sym, struct elf_info *elf)
{
  char *name = NULL;
  void *ptr;

  assert(sym != NULL);
  assert(elf != NULL);

  assert(elf->symtab_data != NULL);
  assert(elf->symtab_data->d_buf != NULL);

  ElfW(Sym) *esym = (ElfW(Sym)*) elf->symtab_data->d_buf;
  ElfW(Sym) *lastsym = (ElfW(Sym)*) ((char*) elf->symtab_data->d_buf + elf->symtab_data->d_size);

  assert(esym <= lastsym);

  for (; esym < lastsym; esym++){
    /* ignore weak/numeric/empty symbols */
    if ((esym->st_value == 0) ||
        (ELF32_ST_BIND(esym->st_info)== STB_WEAK) ||
        (ELF32_ST_BIND(esym->st_info)== STB_NUM))
      continue;

    ptr = elf->base_addr + (void *)esym->st_value;
    name = elf_strptr(elf->elf, elf->symtab_shdr.sh_link, (size_t)esym->st_name);

    if (ptr == sym)
      return name;
  }

  return NULL;
}

/*
 * Do the same thing as in bin_find_symbol above, but compare addresses and return the string name.
 */
const char *
bin_find_symbol_name(void *sym) {
  return do_bin_find_symbol_name(sym, ruby_info);
}

/*
 * bin_update_image - update the ruby binary image in memory.
 *
 * Given -
 *  trampee - the name of the symbol to hook
 *  tramp - the stage 2 trampoline entry
 *  orig_func - out parameter storing the address of the function that was
 *  originally called.
 *
 * This function will update the ruby binary image so that all calls to trampee
 * will be routed to tramp.
 *
 * Returns 0 on success
 */
int
bin_update_image(const char *trampee, struct tramp_st2_entry *tramp, void **orig_func)
{
  void *trampee_addr = NULL;

  assert(trampee != NULL);
  assert(tramp != NULL);
  assert(tramp->addr != NULL);

  /* first check if the symbol is in the PLT */
  trampee_addr = find_plt_addr(trampee, NULL);

  if (trampee_addr) {
    void *ret = NULL;
    dbg_printf("Found %s in the PLT, inserting tramp...\n", trampee);
    ret = overwrite_got(trampee_addr, tramp->addr, ruby_info);

    assert(ret != NULL);

    if (orig_func) {
      *orig_func = ret;
      dbg_printf("setting orig function: %p\n", *orig_func);
    }
  } else {
    trampee_addr = bin_find_symbol(trampee, NULL, 0);
    dbg_printf("Couldn't find %s in the PLT...\n", trampee);

    if (trampee_addr) {
      unsigned char *byte = ruby_info->text_segment;
      size_t count = 0;
      int num = 0;

      assert(byte != NULL);

      if (orig_func) {
        *orig_func = trampee_addr;
      }

      for(; count < ruby_info->text_segment_len; byte++, count++) {
        if (arch_insert_st1_tramp(byte, trampee_addr, tramp) == 0) {
          num++;
        }
      }

      dbg_printf("Inserted %d tramps for: %s\n", num, trampee);
    }
  }

  dbg_printf("Trying to hook %s in other libraries...\n", trampee);

  struct plt_hook_data data;
  data.addr = tramp->addr;
  data.sym = trampee;
  for_each_dso(hook_required_objects, &data);

  dbg_printf("Done searching other libraries for %s\n", trampee);

  return 0;
}


static Dwarf_Die
check_die(Dwarf_Die die, const char *search, Dwarf_Half type)
{
  char *name = 0;
  Dwarf_Error error = 0;
  Dwarf_Half tag = 0;
  int ret = 0;
  int res = dwarf_diename(die,&name,&error);
  if (res == DW_DLV_ERROR) {
    printf("Error in dwarf_diename\n");
    exit(1);
  }
  if (res == DW_DLV_NO_ENTRY) {
    return 0;
  }

  res = dwarf_tag(die,&tag,&error);
  if (res != DW_DLV_OK) {
    printf("Error in dwarf_tag\n");
    exit(1);
  }

  if (tag == type && strcmp(name, search) == 0){
    //printf("tag: %d name: '%s' die: %p\n",tag,name,die);
    ret = 1;
  }

  dwarf_dealloc(dwrf,name,DW_DLA_STRING);

  return ret ? die : 0;
}

static Dwarf_Die
search_dies(Dwarf_Die die, const char *name, Dwarf_Half type)
{
  int res = DW_DLV_ERROR;
  Dwarf_Die cur_die=die;
  Dwarf_Die child = 0;
  Dwarf_Error error;
  Dwarf_Die ret = 0;

  ret = check_die(cur_die, name, type);
  if (ret)
    return ret;

  for(;;) {
    Dwarf_Die sib_die = 0;
    res = dwarf_child(cur_die,&child,&error);
    if (res == DW_DLV_ERROR) {
      printf("Error in dwarf_child\n");
      exit(1);
    }
    if (res == DW_DLV_OK) {
      ret = search_dies(child,name,type);
      if (ret) {
        if (cur_die != die && cur_die != ret)
          dwarf_dealloc(dwrf,cur_die,DW_DLA_DIE);
        return ret;
      }
    }
    /* res == DW_DLV_NO_ENTRY */

    res = dwarf_siblingof(dwrf,cur_die,&sib_die,&error);
    if (res == DW_DLV_ERROR) {
      printf("Error in dwarf_siblingof\n");
      exit(1);
    }
    if (res == DW_DLV_NO_ENTRY) {
      /* Done at this level. */
      break;
    }
    /* res == DW_DLV_OK */

    if (cur_die != die)
      dwarf_dealloc(dwrf,cur_die,DW_DLA_DIE);

    cur_die = sib_die;
    ret = check_die(cur_die, name, type);
    if (ret)
      return ret;
  }
  return 0;
}

static Dwarf_Die
find_die(const char *name, Dwarf_Half type)
{
  Dwarf_Die ret = 0;
  Dwarf_Unsigned cu_header_length = 0;
  Dwarf_Half version_stamp = 0;
  Dwarf_Unsigned abbrev_offset = 0;
  Dwarf_Half address_size = 0;
  Dwarf_Unsigned next_cu_header = 0;
  Dwarf_Error error;
  int cu_number = 0;

  Dwarf_Die no_die = 0;
  Dwarf_Die cu_die = 0;
  int res = DW_DLV_ERROR;

  for (;;++cu_number) {
    no_die = 0;
    cu_die = 0;
    res = DW_DLV_ERROR;

    res = dwarf_next_cu_header(dwrf, &cu_header_length, &version_stamp, &abbrev_offset, &address_size, &next_cu_header, &error);

    if (res == DW_DLV_ERROR) {
      printf("Error in dwarf_next_cu_header\n");
      exit(1);
    }
    if (res == DW_DLV_NO_ENTRY) {
      /* Done. */
      return 0;
    }

    /* The CU will have a single sibling, a cu_die. */
    res = dwarf_siblingof(dwrf,no_die,&cu_die,&error);

    if (res == DW_DLV_ERROR) {
      printf("Error in dwarf_siblingof on CU die \n");
      exit(1);
    }
    if (res == DW_DLV_NO_ENTRY) {
      /* Impossible case. */
      printf("no entry! in dwarf_siblingof on CU die \n");
      exit(1);
    }

    ret = search_dies(cu_die,name,type);

    if (cu_die != ret)
      dwarf_dealloc(dwrf,cu_die,DW_DLA_DIE);

    if (ret)
      break;
  }

  /* traverse to the end to reset */
  while ((dwarf_next_cu_header(dwrf, &cu_header_length, &version_stamp, &abbrev_offset, &address_size, &next_cu_header, &error)) != DW_DLV_NO_ENTRY);

  return ret ? ret : 0;
}

/*
 * find_libruby_cb - a callback which attempts to locate libruby in the linkmap
 *
 * This callback is fired from walk_linkmap for each item on the linkmap. This
 * function searchs for libruby and stores data about it in the object passed
 * through.
 *
 * This function return CB_EXIT once libruby is found to terminate the link map
 * walker. If libruby isn't found, this function returns CB_CONTINUE.
 */
static linkmap_cb_status
find_libruby_cb(struct link_map *map, void *data)
{
  struct elf_info *lib = data;

  assert(map != NULL);
  assert(data != NULL);

  if (strstr(map->l_name, "libruby")) {
    dbg_printf("Found a libruby.so!\n");
    if (lib) {
      lib->base_addr = (GElf_Addr)map->l_addr;
      lib->filename = strdup(map->l_name);
    }
    libruby = 1;
    return CB_EXIT;
  }
  return CB_CONTINUE;
}

/*
 * walk_linkmap - walk the linkmap firing a callback along the way.
 *
 * Given:
 *  - cb - a callback function
 *  - data - and any private data to pass through (optional)
 *
 * This function will crawl the linkmap and fire the callback on each item
 * found.
 *
 * If the callback returns CB_CONTINUE, this function will move to the next
 * (if any) item in the link map.
 *
 * If the callback returns CB_EXIT, this function will return immediately.
 */
static void
walk_linkmap(linkmap_cb cb, void *data)
{
  struct link_map *map = _r_debug.r_map;

  assert(map);

  while (map) {
    dbg_printf("Found a linkmap entry: %s\n", map->l_name);
    if (cb(map, data) == CB_EXIT)
      break;
    map = map->l_next;
  }

  return;
}

/*
 * has_libruby - check if this ruby binary is linked against libruby.so
 *
 * This function checks if the curreny binary is linked against libruby. If
 * so, it sets libruby = 1, and fill internal state in the elf_info structure.
 *
 * Returns 1 if this binary is linked to libruby.so, 0 if not.
 */
static int
has_libruby(struct elf_info *lib)
{
  libruby = 0;
  walk_linkmap(find_libruby_cb, lib);
  return libruby;
}

size_t
bin_type_size(const char *name)
{
  Dwarf_Unsigned size = 0;
  Dwarf_Error error;
  int res = DW_DLV_ERROR;
  Dwarf_Die die = 0;

  die = find_die(name, DW_TAG_structure_type);

  if (die) {
    res = dwarf_bytesize(die, &size, &error);
    dwarf_dealloc(dwrf,die,DW_DLA_DIE);
    if (res == DW_DLV_OK)
      return size;
  }

  return 0;
}

int
bin_type_member_offset(const char *type, const char *member)
{
  Dwarf_Error error;
  int res = DW_DLV_ERROR;
  Dwarf_Die die = 0, child = 0;
  Dwarf_Attribute attr = 0;

  die = find_die(type, DW_TAG_structure_type);

  if (die) {
    child = search_dies(die, member, DW_TAG_member);
    dwarf_dealloc(dwrf,die,DW_DLA_DIE);

    if (child) {
      res = dwarf_attr(child, DW_AT_data_member_location, &attr, &error);
      if (res == DW_DLV_OK) {
        Dwarf_Locdesc *locs = 0;
        Dwarf_Signed num = 0;

        res = dwarf_loclist(attr, &locs, &num, &error);
        if (res == DW_DLV_OK && num > 0) {
          return locs[0].ld_s[0].lr_number;
        }
      }
    }
  }

  return -1;
}

/*
 * open_elf - Opens a file from disk and gets the elf reader started.
 *
 * Given a filename, this function attempts to open the file and start the
 * elf reader.
 *
 * Returns an elf_info object that must be freed by the caller.
 */
static void
open_elf(struct elf_info *info)
{

  assert(info != NULL);

  if (elf_version(EV_CURRENT) == EV_NONE)
    errx(EX_SOFTWARE, "ELF library initialization failed: %s", elf_errmsg(-1));

  if ((info->fd = open(info->filename, O_RDONLY, 0)) < 0)
    err(EX_NOINPUT, "open \%s\" failed", info->filename);

  if ((info->elf = elf_begin(info->fd, ELF_C_READ, NULL)) == NULL)
    errx(EX_SOFTWARE, "elf_begin() failed: %s.", elf_errmsg(-1));

  if (elf_kind(info->elf) != ELF_K_ELF)
    errx(EX_DATAERR, "%s is not an ELF object.", info->filename);

  return;
}

static char *
get_debuglink_info(struct elf_info *elf, unsigned long *crc_out)
{
  char *basename = (char *) elf->debuglink_data->d_buf;
  unsigned long offset = strlen(basename) + 1;
  offset = (offset + 3) & ~3;

  memcpy(crc_out, elf->debuglink_data->d_buf + offset, 4);

  return basename;
}

static int
verify_debug_checksum(const char *filename, unsigned long crc)
{
  struct stat stat_buf;
  void *region = NULL;
  int fd = open(filename, O_RDONLY);
  unsigned long crc_check = 0;

  if (fd == -1) {
    dbg_printf("Couldn't open debug file: %s, because: %s\n", filename, strerror(errno));
    return 1;
  }

  if (fstat(fd, &stat_buf) == -1) {
    dbg_printf("Couldn't stat debug file: %s, because: %s\n", filename, strerror(errno));
    return 1;
  }

  region = mmap(NULL, stat_buf.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
  if (region == MAP_FAILED) {
    dbg_printf("mapping a section of size: %zd has failed!\n", stat_buf.st_size);
    return 1;
  }

  crc_check = gnu_debuglink_crc32(crc_check, region, stat_buf.st_size);
  dbg_printf("supposed crc: %lx, computed crc:  %lx\n", crc, crc_check);

  munmap(region, stat_buf.st_size);
  close(fd);

  return !(crc == crc_check);
}

static int
find_debug_syms(struct elf_info *elf)
{
  /*
   * XXX TODO perhaps allow users to specify an env var (or something) pointing
   * to where the debug symbols live?
   */
  unsigned long crc = 0;
  char *basename = get_debuglink_info(elf, &crc);
  char *debug_file = NULL, *dir = NULL;
  char *tmp = strdup(elf->filename);

  assert(basename != NULL);
  dbg_printf(".gnu_debuglink base file name: %s, crc: %lx\n", basename, crc);

  dir = dirname(tmp);
  debug_file = calloc(1, strlen(DEBUGDIR) + strlen(dir) +
                         strlen("/") + strlen(basename) + 1);

  strncat(debug_file, DEBUGDIR, strlen(DEBUGDIR));
  strncat(debug_file, dir, strlen(dir));
  strncat(debug_file, "/", strlen("/"));
  strncat(debug_file, basename, strlen(basename));

  elf->debug_data = calloc(1, sizeof(*elf->debug_data));
  elf->debug_data->filename = debug_file;

  dbg_printf("Possible debug symbols in: %s\n", elf->debug_data->filename);

  if (verify_debug_checksum(elf->debug_data->filename, crc)) {
    dbg_printf("Checksum verification of debug file: %s failed!", elf->debug_data->filename);
    free(debug_file);
    free(elf->debug_data);
    return 1;
  }

  open_elf(elf->debug_data);

  if (dissect_elf(elf->debug_data, 0) != 0) {
    /* free debug_data */
    dbg_printf("Dissection of debug data failed!\n");
    free(debug_file);
    free(elf->debug_data);
    return 1;
  }

  elf->symtab_data = elf->debug_data->symtab_data;
  elf->symtab_shdr = elf->debug_data->symtab_shdr;

  /* XXX free stuff */
  /* LEAK elf_end(elf->elf); */

  elf->elf = elf->debug_data->elf;
  close(elf->debug_data->fd);

  dbg_printf("Finished dissecting debug data\n");
  return 0;
}

/*
 * dissect_elf - Parses and stores internal data about an ELF object.
 *
 * Given an elf_info structure, this function will attempt to parse the object
 * and store important state needed to rewrite the object later.
 *
 * TODO better error handling
 *
 * Returns 1 on hard errors.
 * Returns 2 on recoverable errors (missing symbol table).
 * Returns 0 on success.
 */
static int
dissect_elf(struct elf_info *info, int find_debug)
{
  assert(info != NULL);

  size_t shstrndx = 0, j = 0;
  Elf *elf = info->elf;
  Elf_Scn *scn = NULL;
  GElf_Shdr shdr;
  int ret = 0;

  if (elf_getshdrstrndx(elf, &shstrndx) == -1) {
    dbg_printf("getshstrndx() failed: %s.", elf_errmsg(-1));
    ret = 1;
    goto out;
  }

  if (gelf_getehdr(elf, &(info->ehdr)) == NULL) {
    dbg_printf("Couldn't get elf header.");
    ret = 1;
    goto out;
  }

  /* search each ELF header and store important data for each header... */
  while ((scn = elf_nextscn(elf, scn)) != NULL) {
    if (gelf_getshdr(scn, &shdr) != &shdr) {
      dbg_printf("getshdr() failed: %s.", elf_errmsg(-1));
      ret = 1;
      goto out;
    }

    /*
     * The .dynamic section contains entries that are important to memprof.
     * Specifically, the .rela.plt section information. The .rela.plt section
     * indexes the .plt, which will be important for hooking functions in
     * shared objects.
     */
    if (shdr.sh_type == SHT_DYNAMIC) {
      Elf_Data *data;
      data = elf_getdata(scn, NULL);
      /* for each entry in the dyn section...  */
      for (j = 0; j < shdr.sh_size / shdr.sh_entsize; ++j) {
        GElf_Dyn dyn;
        if (gelf_getdyn(data, j, &dyn) == NULL) {
          dbg_printf("Couldn't get .dynamic data from loaded library.");
          ret = 1;
          goto out;
        }

        if (dyn.d_tag == DT_JMPREL) {
          info->relplt_addr = dyn.d_un.d_ptr;
        }
        else if (dyn.d_tag == DT_PLTGOT) {
          info->got_addr = dyn.d_un.d_ptr;
        }
        else if (dyn.d_tag == DT_PLTRELSZ) {
          info->plt_size = dyn.d_un.d_val;
        }
      }
    }
    /*
     * The .dynsym section has useful pieces, too, like the dynamic symbol
     * table. This table is used when walking the .rela.plt section.
     */
    else if (shdr.sh_type == SHT_DYNSYM) {
      Elf_Data *data;

      info->dynsym = elf_getdata(scn, NULL);
      info->dynsym_count = shdr.sh_size / shdr.sh_entsize;
      if (info->dynsym == NULL || elf_getdata(scn, info->dynsym) != NULL) {
        dbg_printf("Couldn't get .dynsym data ");
        ret = 1;
        goto out;
      }

      scn = elf_getscn(elf, shdr.sh_link);
      if (scn == NULL || gelf_getshdr(scn, &shdr) == NULL) {
        dbg_printf("Couldn't get section header.");
        ret = 1;
        goto out;
      }

      data = elf_getdata(scn, NULL);
      if (data == NULL || elf_getdata(scn, data) != NULL
          || shdr.sh_size != data->d_size) {// condition true on 32bit: || data->d_off) {
        dbg_printf("Couldn't get .dynstr data\n");
        ret = 1;
        goto out;
      }

      info->dynstr = data->d_buf;
    }
    /*
     * Pull out information (start address and length) of the .text section.
     */
    else if (shdr.sh_type == SHT_PROGBITS &&
        (shdr.sh_flags == (SHF_ALLOC | SHF_EXECINSTR)) &&
        strcmp(elf_strptr(elf, shstrndx, shdr.sh_name), ".text") == 0) {

      info->text_segment = (void *)shdr.sh_addr + info->base_addr;
      info->text_segment_len = shdr.sh_size;
    }
    /*
     * Pull out information (start address) of the .plt section.
     */
    else if (shdr.sh_type == SHT_PROGBITS) {
      if (strcmp(elf_strptr(elf, shstrndx, shdr.sh_name), ".plt") == 0) {
        info->plt_addr = shdr.sh_addr;
      } else if (strcmp(elf_strptr(elf, shstrndx, shdr.sh_name), ".got.plt") == 0) {
        info->got_addr = shdr.sh_addr;
      } else if (strcmp(elf_strptr(elf, shstrndx, shdr.sh_name), ".gnu_debuglink") == 0) {
        dbg_printf("gnu_debuglink section found\n", shdr.sh_size);
        if ((info->debuglink_data = elf_getdata(scn, NULL)) == NULL ||
             info->debuglink_data->d_size == 0) {
          dbg_printf(".gnu_debuglink section existed, but wasn't readable.\n");
          ret = 2;
          goto out;
        }
        dbg_printf("gnu_debuglink section read (size: %zd)\n", shdr.sh_size);
      }
    }
    /*
     * The symbol table is also needed for bin_find_symbol
     */
    else if (shdr.sh_type == SHT_SYMTAB) {
      info->symtab_shdr = shdr;
      if ((info->symtab_data = elf_getdata(scn, info->symtab_data)) == NULL ||
          info->symtab_data->d_size == 0) {
        dbg_printf("shared lib has a broken symbol table. Is it stripped? "
                   "memprof only works on shared libs that are not stripped!\n");
        ret = 2;
        goto out;
      }
    }
  }

  /* If this object has no symbol table there's nothing else to do but fail */
  if (!info->symtab_data) {
    if (info->debuglink_data) {
      dbg_printf("binary is stripped, but there is debug symbol information. memprof will try to read debug symbols in.\n");
    } else {
      dbg_printf("binary is stripped, and no debug symbol info was found. memprof only works on binaries that are not stripped!\n");
    }
    ret = 1;
  }

  /*
   * Walk the sections, pull out, and store the .plt section
   */
  for (j = 1; j < info->ehdr.e_shnum; j++) {
    scn =  elf_getscn(elf, j);
    if (scn == NULL || gelf_getshdr(scn, &shdr) == NULL) {
      dbg_printf("Couldn't get section header from library.");
      ret = 1;
      goto out;
    }

    if (shdr.sh_addr == info->relplt_addr
        && shdr.sh_size == info->plt_size) {
      info->relplt = elf_getdata(scn, NULL);
      info->relplt_count = shdr.sh_size / shdr.sh_entsize;
      if (info->relplt == NULL || elf_getdata(scn, info->relplt) != NULL) {
        dbg_printf("Couldn't get .rel*.plt data from");
        ret = 1;
        goto out;
      }
      break;
    }
  }

out:
  if (find_debug && ret == 1) {
    if (info->debuglink_data) {
      find_debug_syms(info);
    } else {
      dbg_printf("=== WARNING: Object %s was STRIPPED and had no debuglink section. Nothing left to try.\n", info->filename);
    }
  }
  return ret;
}


/*
 * bin_init - initialize the binary parsing/modification layer.
 *
 * This function starts the elf parser and sets up internal state.
 */
void
bin_init()
{
  Dwarf_Error dwrf_err;

  ruby_info = calloc(1, sizeof(*ruby_info));

  if (!ruby_info) {
    errx(EX_UNAVAILABLE, "Unable to allocate memory to start binary parsing layer");
  }

  if (!has_libruby(ruby_info)) {
    dbg_printf("This ruby binary has no libruby\n");
    char *filename = calloc(1, 255);
    if (readlink("/proc/self/exe", filename, 255) == -1) {
      errx(EX_UNAVAILABLE, "Unable to follow /proc/self/exe symlink: %s", strerror(errno));
    }
    ruby_info->filename = filename;
    ruby_info->base_addr = 0;
    dbg_printf("The path to the binary is: %s\n", ruby_info->filename);
  }

  open_elf(ruby_info);

  if (dissect_elf(ruby_info, 1) == 2) {
    errx(EX_DATAERR, "Error trying to parse elf file: %s\n", ruby_info->filename);
  }

  if (dwarf_elf_init(ruby_info->elf, DW_DLC_READ, NULL, NULL, &dwrf, &dwrf_err) != DW_DLV_OK) {
    errx(EX_DATAERR, "unable to read debugging data from binary. was it compiled with -g? is it unstripped?");
  }

  dbg_printf("bin_init finished\n");
}
#endif

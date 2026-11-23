#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ff.h"
#include "diskio.h"

static FILE *image;
static int sync_token;
DSTATUS disk_initialize(BYTE drive) { return drive == 0 && image ? 0 : STA_NOINIT; }
DSTATUS disk_status(BYTE drive) { return disk_initialize(drive); }
DRESULT disk_read(BYTE drive, BYTE *buffer, DWORD sector, UINT count) {
    if (drive || fseek(image, (long)sector * 512, SEEK_SET)) return RES_ERROR;
    return fread(buffer, 512, count, image) == count ? RES_OK : RES_ERROR;
}
DRESULT disk_write(BYTE drive, const BYTE *buffer, DWORD sector, UINT count) {
    if (drive || fseek(image, (long)sector * 512, SEEK_SET)) return RES_ERROR;
    return fwrite(buffer, 512, count, image) == count ? RES_OK : RES_ERROR;
}
DRESULT disk_ioctl(BYTE drive, BYTE command, void *buffer) {
    if (drive) return RES_PARERR;
    if (command == CTRL_SYNC) return fflush(image) ? RES_ERROR : RES_OK;
    if (command == GET_SECTOR_COUNT) { *(DWORD *)buffer = 131072; return RES_OK; }
    if (command == GET_SECTOR_SIZE) { *(WORD *)buffer = 512; return RES_OK; }
    if (command == GET_BLOCK_SIZE) { *(DWORD *)buffer = 1; return RES_OK; }
    return RES_PARERR;
}
/* Single-threaded host adapter; production synchronization is unchanged. */
int ff_cre_syncobj(BYTE volume, FF_SYNC_t *object) { *object = &sync_token; return 1; }
int ff_del_syncobj(FF_SYNC_t object) { return 1; }
int ff_req_grant(FF_SYNC_t object) { return 1; }
void ff_rel_grant(FF_SYNC_t object) { }

static void check(FRESULT result, const char *step) {
    if (result != FR_OK) { fprintf(stderr, "FAIL %s: FatFs result %d\n", step, result); exit(1); }
}
static void write_file(const char *path, const char *data) {
    FIL file;
    UINT written;
    check(f_open(&file, path, FA_CREATE_ALWAYS | FA_WRITE), "create UTF-8 path");
    check(f_write(&file, data, (UINT)strlen(data), &written), "write payload");
    if (written != strlen(data)) exit(2);
    check(f_close(&file), "close write");
}
static void read_file(const char *path, const char *expected) {
    FIL file;
    UINT size;
    char data[128] = {0};
    check(f_open(&file, path, FA_READ), "open UTF-8 path");
    check(f_read(&file, data, sizeof(data) - 1, &size), "read payload");
    if (size != strlen(expected) || memcmp(data, expected, size)) exit(3);
    check(f_close(&file), "close read");
}
int main(int argc, char **argv) {
    FATFS fs;
    DIR directory;
    FILINFO info;
    int found_nds = 0, found_sav = 0;
    if (argc != 2 || !(image = fopen(argv[1], "r+b"))) return 4;
    check(f_mount(&fs, "fat:", 1), "mount FAT32 image");
    if (fs.fs_type != FS_FAT32) return 5;
    check(f_mkdir("fat:/中文目录"), "mkdir Chinese");
    check(f_mkdir("fat:/中文目录/角色扮演"), "mkdir nested Chinese");
    write_file("fat:/中文目录/角色扮演/宝可梦.nds", "NDS path test");
    write_file("fat:/中文目录/角色扮演/宝可梦.sav", "SAVE persistence test");
    check(f_opendir(&directory, "fat:/中文目录/角色扮演"), "enumerate Chinese folder");
    while (1) {
        check(f_readdir(&directory, &info), "read UTF-8 directory entry");
        if (!info.fname[0]) break;
        found_nds |= !strcmp(info.fname, "宝可梦.nds");
        found_sav |= !strcmp(info.fname, "宝可梦.sav");
    }
    check(f_closedir(&directory), "close directory");
    if (!found_nds || !found_sav) return 6;
    check(f_rename("fat:/中文目录/角色扮演/宝可梦.nds", "fat:/中文目录/角色扮演/宝可梦 汉化.nds"), "rename mixed name");
    check(f_mount(NULL, "fat:", 0), "unmount");
    check(f_mount(&fs, "fat:", 1), "remount");
    read_file("fat:/中文目录/角色扮演/宝可梦 汉化.nds", "NDS path test");
    read_file("fat:/中文目录/角色扮演/宝可梦.sav", "SAVE persistence test");
    write_file("fat:/English.nds", "ASCII regression");
    read_file("fat:/English.nds", "ASCII regression");
    check(f_mount(NULL, "fat:", 0), "final unmount");
    fclose(image);
    puts("PASS: FAT32 nested Chinese directories, UTF-8 enumeration, NDS/SAV read-write, rename, remount persistence, ASCII regression");
    return 0;
}

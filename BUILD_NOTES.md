# Local Chinese filename integration

This is the official LNH-team Pico Launcher with a selective integration of the
Chinese-font work from PR #37, not the complete Chinese-enhanced fork.

Official base: `dc64a34cabe26a9ac12d5592ada2d729cdfc6328`.
Chinese source: `cad2209e5f5cf3274ca1b80913843c6ddc4da454`.

The complete PR has extensive conflicts with the current official branch. Its
own notes also report freezing when rapidly navigating folders. This local merge
therefore intentionally imports only the Chinese bitmap font, its license and
generation script. It preserves the official browser and game-loading logic.
The merge's second parent records the exact Chinese source, but unrelated fork
features are intentionally excluded.

Changes:

- Share the fork's WenQuanYi 12px bitmap font across normal filename/title sizes.
- Keep the original 7.5pt font for compact English UI labels.
- Unpack the shared Chinese font once, avoiding duplicate font RAM usage.
- Keep UTF-8 long filenames (`FF_LFN_UNICODE=2`) and enable CP936 conversion for
  Chinese OEM short filenames (`FF_CODE_PAGE=936`).
- The menu itself remains English. The font contains the 6,763 GB2312 Chinese
  characters, not all Unicode characters; rare characters and emoji can be absent.

Build environment:

- Existing Windows MSYS2 shell and GNU Make.
- Wonderful ARM GCC 16.2.0, binutils 2.47, picolibc 1.8.13.
- BlocksDS 1.25.0, official Windows packages.
- libtwl submodule `aa3b2a23c10185a10449ffa685bb7933d5d5a784`.
- No Docker/WSL installation was required.

The fork recommends BlocksDS 1.15.7 for its full feature set. This build instead
uses the currently available native Windows SDK and the official application
code. Console runtime behavior has not been verified; do not interpret a
successful build as proof that every hardware combination works.

Validation:

- NDS ARM9/ARM7 compilation and link succeeded.
- ndstool verified header, Nintendo logo and secure-area CRCs.
- Font structure, glyph indices and representative Chinese characters checked.
- The actual modified `ff.c` and `ffunicode.c` were compiled into a Windows host
  harness using the production `ffconf.h`. A private 64 MiB FAT32 image passed
  nested Chinese directory creation, UTF-8 enumeration, `.nds` and `.sav` payload
  read/write, mixed-name rename, unmount/remount persistence, and ASCII checks.
- The host harness uses a single-threaded synchronization adapter and a file-backed
  disk. It does not test DS hardware, the menu graphics or actual game execution.
- Neither a physical TF card nor its games/saves were modified during this task.

Deployment: use the packaged `_picoboot.nds` in the TF root. Existing
`_pico` loader files, settings and games can remain. The full SD file package
also includes the previously SHA256-verified official DSPICO Loader v1.7.1.
Keep the old `_picoboot.nds` to roll back.


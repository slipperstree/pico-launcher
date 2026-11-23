"""Compile the actual icon constructor and StringUtil against real font metrics.

Only the graphics-independent constructor is extracted; DS graphics are not
emulated. The old byte-copy constructor fails the Chinese assertions here.
"""
from pathlib import Path
import argparse
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('repo', type=Path)
parser.add_argument('--compiler', default=r'C:\msys64\mingw64\bin\g++.exe')
args = parser.parse_args()
repo = args.repo
source = (repo / 'arm9/source/romBrowser/Theme/Material/MaterialFileIcon.cpp').read_text(encoding='utf-8')
constructor = source[source.index('MaterialFileIcon::MaterialFileIcon('):source.index('\nvoid MaterialFileIcon::UploadGraphics')]

prelude = r'''
#include <cstdint>
#include <fstream>
#include <vector>
#include <string>
#include <iostream>
#include <cassert>
#include "common.h"
#include "StringUtil.h"
using TCHAR = char;
struct MaterialColorScheme {};
struct Glyph { int left=0, width=0, right=0; };
struct nft2_header_t { Glyph glyphs[65536]; int height=15; };
static nft2_header_t font;
enum class FontType { Medium11 };
struct IFontRepository {
 const nft2_header_t* GetFont(FontType) const { return &font; }
};
void nft2_measureString(const nft2_header_t* f, const char16_t* s, u32& w, u32& h) {
 int x=0, max=0;
 while (*s) { const auto& g=f->glyphs[*s++]; x+=g.left+g.width; if(x>max)max=x; x+=g.right; }
 w=max; h=f->height;
}
class MaterialFileIcon {
public:
 MaterialFileIcon(const TCHAR*, const MaterialColorScheme*, const IFontRepository*);
 char16_t _displayName[4];
private:
 const MaterialColorScheme* _materialColorScheme;
 const IFontRepository* _fontRepository;
};
'''
postlude = r'''
static uint16_t le16(const std::vector<unsigned char>& b, size_t p) {
 return b[p] | (b[p+1]<<8);
}
static uint32_t le32(const std::vector<unsigned char>& b, size_t p) {
 return le16(b,p) | (uint32_t(le16(b,p+2))<<16);
}
int main() {
 std::ifstream input("font.nft2",std::ios::binary);
 std::vector<unsigned char> data((std::istreambuf_iterator<char>(input)),{});
 assert(data.size()>20);
 size_t table=le32(data,4), map=le32(data,8);
 while (uint16_t n=le16(data,map)) {
  uint16_t start=le16(data,map+2);
  for (unsigned i=0;i<n;++i) {
   uint16_t index=le16(data,map+4+i*2);
   size_t p=table+index*8;
   font.glyphs[start+i]={int(int8_t(data[p+4])),int(data[p+3]),int(int8_t(data[p+5]))};
  }
  map+=4+n*2;
 }
 const IFontRepository repository;
 struct Case {const char* name;const char16_t* expected;};
 const Case cases[]={
  {"学外语",u"学外"}, {"其他类",u"其他"}, {"冒险类",u"冒险"},
  {"角色扮演",u"角色"}, {"3DS-R4卡游戏",u"3DS"}, {"Games",u"Gam"},
  {"学A语",u"学A语"}, {"AB中文",u"AB中"}, {"中",u"中"},
  {"AB",u"AB"}, {"",u""}, {nullptr,u""}
 };
 unsigned i=0;
 for(const auto& c:cases) {
  MaterialFileIcon icon(c.name,nullptr,&repository);
  if(std::u16string(icon._displayName)!=c.expected) {
   std::cerr<<"FAIL icon label case "<<i<<"\n";return 1;
  }
  u32 width,height;
  nft2_measureString(&font,icon._displayName,width,height);
  if(width>32) return 2;
  ++i;
 }
 std::cout<<"PASS: "<<i<<" icon label cases (Chinese, mixed, ASCII, short, empty, null); all fit 32 pixels\n";
}
'''
with tempfile.TemporaryDirectory(prefix='dspico-icon-') as directory:
    work = Path(directory)
    (work/'common.h').write_text('#pragma once\n#include <cstdint>\nusing u32=uint32_t;\n', encoding='utf-8')
    for name in ['StringUtil.cpp', 'StringUtil.h']:
        shutil.copy2(repo/'arm9/source/core'/name, work/name)
    shutil.copy2(repo/'arm9/data/WenQuanYi-Bitmap-12.nft2', work/'font.nft2')
    (work/'test.cpp').write_text(prelude+constructor+postlude, encoding='utf-8')
    subprocess.run([args.compiler,'-std=c++17','-O2','-static','-finput-charset=UTF-8',
                    'test.cpp','StringUtil.cpp','-o','test.exe'],cwd=work,check=True)
    subprocess.run([str(work/'test.exe')],cwd=work,check=True)

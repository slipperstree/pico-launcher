#include "common.h"
#include "NotoSansJP-Medium-7_5_nft2.h"
#include "WenQuanYi-Bitmap-12_nft2.h"
#include "DefaultFontRepository.h"

const nft2_header_t* DefaultFontRepository::GetFont(FontType fontType) const
{
    // Preserve compact English UI labels; filenames and titles use the shared
    // GB2312 Chinese bitmap font from chaye7417's chinese branch.
    switch (fontType)
    {
        case FontType::Medium7_5:
            return (const nft2_header_t*)NotoSansJP_Medium_7_5_nft2;
        case FontType::Regular10:
        case FontType::Medium10:
        case FontType::Medium11:
            return (const nft2_header_t*)WenQuanYi_Bitmap_12_nft2;
        default:
            return nullptr;
    }
}

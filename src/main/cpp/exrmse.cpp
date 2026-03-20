#include <string>
#include <map>
#include <chrono>
#include <numeric>
#include <cmath>
#include <iterator>
#include <mutex>

#include <openexr.h>
#include "ojphl.h"
#include "nlt.h"

#include "cxxopts.hpp"
#include <float.h>
#include <half.h>


#define CHANNEL_COUNT 3

void dif(exr_result_t r)
{
    if (r != EXR_ERR_SUCCESS)
    {
        printf("fail");
        exit(-1);
    }
}

void read_image(std::string path, uint8_t **buffer, int &width, int &height, exr_pixel_type_t &pixelType)
{
    exr_context_t f;
    dif(exr_start_read(&f, path.c_str(), NULL));

    int partCount;
    dif(exr_get_count(f, &partCount));

    if (partCount != 1)
    {
        std::cout << "The files must contain at most one part" << std::endl;
        exit(-1);
    }

    exr_storage_t stortype;
    dif(exr_get_storage(f, 0, &stortype));
    if (stortype != EXR_STORAGE_SCANLINE)
    {
        std::cout << "Only supports scanline files" << std::endl;
        exit(-1);
    }

    const exr_attr_chlist_t *channels;
    dif(exr_get_channels(f, 0, &channels));
    if (channels->num_channels != CHANNEL_COUNT)
    {
        std::cout << "The files must contain exactly three channels" << std::endl;
        exit(-1);
    }

    exr_attr_box2i_t dw;
    dif(exr_get_data_window(f, 0, &dw));
    width = dw.max.x - dw.min.x + 1;
    height = dw.max.y - dw.min.y + 1;

    /* allocate basband image buffer */
    uint8_t pixelstride = 0;

    uint8_t ch_offset[CHANNEL_COUNT];
    for (int ch_id = 0; ch_id < channels->num_channels; ++ch_id)
    {
        if (ch_id == 0)
        {
            pixelType = channels->entries[ch_id].pixel_type;
        }
        else if (pixelType != channels->entries[ch_id].pixel_type)
        {
            std::cout << "All channels must have the same pixel type"
                      << std::endl;
            exit(-1);
        }
        ch_offset[ch_id] = pixelstride;
        pixelstride += pixelType == EXR_PIXEL_HALF ? 2 : 4;
    }
    int32_t linestride = pixelstride * width;
    *buffer = (uint8_t *)malloc(height * width * pixelstride);

    /* read the source file */

    bool first = true;
    exr_decode_pipeline_t decoder;
    exr_chunk_info_t src_chunk;
    exr_encode_pipeline_t encoder;
    exr_chunk_info_t out_chunk;

    int32_t scansperchunk;
    dif(exr_get_scanlines_per_chunk(f, 0, &scansperchunk));

    uint8_t *chunk_buf = *buffer;
    for (int y = dw.min.y; y <= dw.max.y; y += scansperchunk)
    {
        dif(exr_read_scanline_chunk_info(f, 0, y, &src_chunk));

        if (first)
        {
            dif(exr_decoding_initialize(f, 0, &src_chunk, &decoder));
        }
        else
        {
            dif(exr_decoding_update(f, 0, &src_chunk, &decoder));
        }

        for (int ch_id = 0; ch_id < decoder.channel_count; ++ch_id)
        {
            const exr_coding_channel_info_t &dec_ch = decoder.channels[ch_id];

            if (decoder.channels[ch_id].height == 0)
            {
                decoder.channels[ch_id].decode_to_ptr = NULL;
                decoder.channels[ch_id].user_pixel_stride = 0;
                decoder.channels[ch_id].user_line_stride = 0;
                continue;
            }

            decoder.channels[ch_id].decode_to_ptr = chunk_buf + ch_offset[ch_id];
            decoder.channels[ch_id].user_pixel_stride = pixelstride;
            decoder.channels[ch_id].user_line_stride = linestride;
        }

        if (first)
        {
            dif(
                exr_decoding_choose_default_routines(f, 0, &decoder));
        }
        dif(exr_decoding_run(f, 0, &decoder));

        first = false;
        chunk_buf += linestride * scansperchunk;
    }

    dif(exr_decoding_destroy(f, &decoder));
    dif(exr_finish(&f));
}

int main(int argc, char *argv[])
{
    cxxopts::Options options(
        "exrpsnr", "Compute the PSNR between two EXR images");

    options.add_options()(
        "apath", "Image A path", cxxopts::value<std::string>())(
        "bpath", "Image B path", cxxopts::value<std::string>())(
        "n", "NLT MSE")(
        "a", "arcsinh MSE");

    options.parse_positional({"apath", "bpath"});

    options.show_positional_help();

    auto args = options.parse(argc, argv);

    if (args.count("apath") != 1 || args.count("bpath") != 1)
    {
        std::cout << options.help() << std::endl;
        exit(-1);
    }

    bool nlt_mse = args.count("n") == 1;
    bool arcsinh_mse = args.count("a") == 1;

    exr_result_t r;

    /* file A */

    auto &a_fn = args["apath"].as<std::string>();

    uint8_t *a_buf;
    int a_width, a_height;
    exr_pixel_type_t a_pixeltype;

    read_image(a_fn, &a_buf, a_width, a_height, a_pixeltype);

    /* file B */

    auto &b_fn = args["bpath"].as<std::string>();

    uint8_t *b_buf;
    int b_width, b_height;
    exr_pixel_type_t b_pixeltype;

    read_image(b_fn, &b_buf, b_width, b_height, b_pixeltype);

    /* compare images */

    if (a_width != b_width || a_height != b_height ||
        a_pixeltype != b_pixeltype)
    {
        std::cout << "Image dimensions or pixel types do not match"
                  << std::endl;
        exit(-1);
    }

    if (a_pixeltype != EXR_PIXEL_HALF)
    {
        std::cout << "Only half pixel type is supported" << std::endl;
        exit(-1);
    }

    double mse = 0.0;
    int count = 0;
    for (size_t i = 0; i < a_width * a_height * 3; i++)
    {
        half a_bits;
        a_bits.setBits (*(uint16_t*)(a_buf + i * 2));

        half b_bits;
        b_bits.setBits (*(uint16_t*)(b_buf + i * 2));

        if (!a_bits.isFinite() || !b_bits.isFinite())
        {
            continue;
        }

        double a_pix = nlt_mse ? from_linear((float) a_bits) : (float) a_bits;
        double b_pix = nlt_mse ? from_linear((float) b_bits) : (float) b_bits;

        if (arcsinh_mse) {
            a_pix = std::asinh(a_pix/0.0001);
            b_pix = std::asinh(b_pix/0.0001);
        }

        mse += ((a_pix - b_pix) * (a_pix - b_pix));
        count++;
    }

    mse /= count;

    std::cout << mse << std::endl;

    /* free baseband buffers */
    free(a_buf);
    free(b_buf);

    return 0;
}
#ifndef __FUNCTION_H__
#define __FUNCTION_H__

#include <stdlib.h>
#include "generator.h"
#include "defs.h"

void hsv_to_rgb(int32_t hue, int32_t sat, int32_t value, color_t &color)
{
}

class Function
{
    public:

        virtual void calculate(uint32_t t, color_t &col) = 0;
};

class FunctionConstantColor : public Function
{
    public:

        FunctionConstantColor(color_t &col)
        {
            color = col;
        };
        void calculate(uint32_t t, color_t &col)
        {
            col = color;
        }

    protected:

        color_t color;
};

class FunctionRandomColorSequence : public Function
{
    public:

        FunctionRandomColorSequence(int32_t _period, uint32_t _seed)
        {
            period = _period;
            seed = _seed;
        };
        void calculate(uint32_t t, color_t col)
        {
            srand((uint32_t)(t * SCALE_FACTOR / period));
            hsv_to_rgb(rand() % SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR, col);
        }

    protected:

        int32_t  period;
        uint32_t seed;
};

class FunctionHSV : public Function
{
    public:

        FunctionHSV(Generator *_gen, Generator *_gen2 = NULL, Generator *_gen3 = NULL)
        {
            gen = _gen;
            gen2 = _gen2;
            gen3 = _gen3;
        };
        void calculate(uint32_t t, color_t col)
        {
            if (gen2 && gen3)
                hsv_to_rgb(gen->calculate(t), gen2->calculate(t), gen3->calculate(t), col);
            else
            if (gen2)
                hsv_to_rgb(gen->calculate(t), gen2->calculate(t), 1.0, col);
            else
                hsv_to_rgb(gen->calculate(t), 1.0, 1.0, col);
        }

    protected:

        Generator *gen, *gen2, *gen3;
};

class FunctionRainbow : public Function
{
    public:

        FunctionRainbow(Generator *_gen)
        {
            gen = _gen;
        };
        void calculate(uint32_t t, color_t col)
        {
            uint8_t wheel_pos;

            wheel_pos = 255 - int(255 * gen->calculate(t) / SCALE_FACTOR);
            if (wheel_pos < 85)
            {
                col.c[0] = int(255 - wheel_pos * 3);
                col.c[1] = 0;
                col.c[2] = int(wheel_pos * 3);
            }
            else
            if (wheel_pos < 170)
            {
                wheel_pos -= 85;
                col.c[0] = 0;
                col.c[1] = int(wheel_pos * 3);
                col.c[2] = 255 - int(wheel_pos * 3);
            }
            else
            {
                wheel_pos -= 170;
                col.c[0] = int(wheel_pos * 3);
                col.c[1] = 255 - int(wheel_pos * 3);
                col.c[2] = 0;
            }
        };

    protected:

        Generator *gen;
};

#endif

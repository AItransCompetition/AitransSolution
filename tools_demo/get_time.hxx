#include <sys/time.h>
#include <stdint.h>
#include <stdio.h>

uint64_t getCurrentUsec()  //usec
{
    struct timeval tv;
    gettimeofday(&tv, NULL);  //该函数在sys/time.h头文件中
    return tv.tv_sec * 1000*1000 + tv.tv_usec;
}
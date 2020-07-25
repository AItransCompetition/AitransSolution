#ifndef AITRANS_H_
#define AITRANS_H_
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <map>
using namespace std;
static map<string, uint64_t> your_parameter;
extern "C" {
    struct AckInfo {
        char *event_type;
    };
    struct Blocks {
        uint64_t *blocks_id, *blocks_deadline, *blocks_priority,
            *blocks_create_time;
        uint64_t block_num;
    };
    uint64_t SolutionSelectPacket(struct Blocks blocks, uint64_t current_time);
    uint64_t CSelectBlock(char *blocks_string, uint64_t block_num,
                        uint64_t current_time);
    uint64_t SolutionCcTrigger(AckInfo* ack_infos, uint64_t ack_num, uint64_t cwnd);
    uint64_t Ccc_trigger(AckInfo* ack_infos, uint64_t ack_num, uint64_t cwnd);
}

#endif /* AITRANS_H_ */
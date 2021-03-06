#ifndef SOLUTION_H_
#define SOLUTION_H_
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <string.h>
#include <unordered_map>
using namespace std;
static unordered_map<string, uint64_t> your_parameter;
static unordered_map<string, double> float_parameter;
extern "C" {
    struct CcInfo {
        char event_type;
        uint64_t event_time;
        uint64_t rtt;
        uint64_t bytes_in_flight;
        uint64_t packet_id;
    };
    struct Block {
        uint64_t block_id;
        uint64_t block_deadline;
        uint64_t block_priority;
        uint64_t block_create_time;
        uint64_t block_size;
        uint64_t remaining_size;
    };

    void SolutionInit(uint64_t *init_congestion_window, uint64_t *init_pacing_rate);
    uint64_t SolutionSelectBlock(Block* blocks, uint64_t block_num, uint64_t next_packet_id, uint64_t current_time);
    void SolutionCcTrigger(CcInfo* cc_infos, uint64_t cc_num, uint64_t *congestion_window, uint64_t *pacing_rate);
}

#endif /* SOLUTION_H_ */
#include <torch/script.h> // One-stop header.

#include <iostream>
#include <memory>
#include <algorithm>
#include <vector>
#include <cmath>

#include "solution.hxx"


double get_number_res_from_order(char* order) {
    FILE* fp = NULL;
    double ret = 0;
    char buf[100];

    // call cmd in terminal
    fp = popen(order, "r");
    if (!fp) {
        printf("error in poen");
        return -1;
    }

    // get cmd output
    memset(buf, 0, sizeof(buf));
    fgets(buf, sizeof(buf)-1, fp);

    // parse double number
    ret = atof(buf);

    pclose(fp);
    return ret;
}

void SolutionInit(uint64_t *init_congestion_window, uint64_t *init_pacing_rate)
{
    your_parameter["max_packet_size"] = 1350;
    your_parameter["init_ssthresh"] = 2 * your_parameter["max_packet_size"];
    your_parameter["last_time"] = 0;
    your_parameter["ssthresh"] = your_parameter["init_ssthresh"];
    your_parameter["MAX_BANDWITH"] = 100*8*1024*1024;

    // call python
    // cout << "python result : " << get_number_res_from_order("python3 ./demo/hello_python3.py 1 1 999") << endl;

    cout << "python3 ./demo/demo_rl_torch.py 0" << endl;
    system("python3 ./demo/demo_rl_torch.py 0");
    // init model
    cout << "python3 ./demo/demo_rl_torch.py 1 ./demo/dqn.pkl" << endl;
    system("python3 ./demo/demo_rl_torch.py 1 ./demo/dqn.pkl");

    *init_pacing_rate = 100*1350*8;
    *init_congestion_window = 12345678;
}

uint64_t SolutionSelectBlock(Block* blocks, uint64_t block_num, uint64_t next_packet_id, uint64_t current_time)
{
    /************** START CODE HERE ***************/
    // return the id of block you want to send, for example:
    uint64_t last_time = your_parameter["last_time"];
    // fprintf(stderr,"last_time = %lu, current_time = %lu\n", last_time, current_time);

    your_parameter["last_time"] = current_time;
    return blocks[0].block_id;
    /************** END CODE HERE ***************/
}

void SolutionCcTrigger(CcInfo *cc_infos, uint64_t cc_num, uint64_t *congestion_window, uint64_t *pacing_rate)
{
    /************** START CODE HERE ***************/
    uint64_t cwnd = *congestion_window;
    vector<int> cc_types, rtt_sample;
    double loss_nums = 0, rtt_sum = 0;
    for (uint64_t i = 0; i < cc_num; i++)
    {
        char event_type = cc_infos[i].event_type;
        // fprintf(stderr, "event_type=%c\n", event_type);
        const uint64_t max_packet_size = 1350;
        rtt_sample.push_back(cc_infos[i].rtt);
        rtt_sum += cc_infos[i].rtt;

        if (event_type == 'F') {
            cc_types.push_back(0);
            loss_nums += 1;
        }
        else {
            cc_types.push_back(1);
        }
    }
    
    // construct input
    string ip_1, ip_2;
    for (int i=0;i < cc_num; i++) {
        ip_1.push_back((char) ('0' + cc_types[i]));
        
        ip_2 = ip_2 + to_string(rtt_sample[i]);
        if (i+1 < cc_num) {
            ip_1.push_back(',');
            ip_2.push_back(',');
        }
            
    }
    // learn and save
    string order = "python3 ./demo/demo_rl_torch.py 2 ./demo/dqn.pkl ";
    order.append(ip_1);
    order.append(" ");
    order.append(ip_2);
    order.append(" ");
    order.append(to_string(*pacing_rate));
    cout << order << endl;
    // make decision
    *pacing_rate = get_number_res_from_order((char *)order.data());

    // call torch model when submit model to system
    /*
    torch::jit::script::Module module;
    try
    {
        // Deserialize the ScriptModule from a file using torch::jit::load().
        module = torch::jit::load("./demo/eval_net.pt");
        // Create a vector of inputs.
        std::vector<torch::jit::IValue> inputs;
        vector<double> net_input;
        net_input.push_back(*pacing_rate);
        net_input.push_back(loss_nums / cc_num);
        net_input.push_back(rtt_sum / cc_num);
        net_input.push_back(rtt_sample[(int) (cc_num/2)]);
        net_input.push_back(rtt_sample[cc_num-1]);

        torch::Tensor scales_ = torch::tensor(net_input);

        inputs.push_back(scales_);

        // Execute the model and turn its output into a tensor.
        at::Tensor output = module.forward(inputs).toTensor();
        std::cout << output << '\n';
        std::cout << output.argmax() << '\n';

        int action = output.argmax().item().toInt();

        std::cout << action << '\n';
        if (action == 0) {
            *pacing_rate = (*pacing_rate) * 1.4;
        }
        else if (action == 1) {
            *pacing_rate = (*pacing_rate) * 1;
        }
        else if (action == 2) {
            *pacing_rate = (*pacing_rate) * 0.4;
        }
        if (*pacing_rate >= your_parameter["MAX_BANDWITH"] || *pacing_rate <= 10*1350*8) {
            *pacing_rate = your_parameter["MAX_BANDWITH"] / 2;
        }
    }
    catch (const c10::Error &e)
    {
        std::cout << e.msg() <<  endl;
        std::cerr << "error loading the model\n";
    }
    */
    std::cout << "ok\n";
    std::cout << *pacing_rate << std::endl;
    // fprintf(stderr,"new cwnd: %lu, ssthresh = %lu\n", cwnd, your_parameter["ssthresh"]);
    // *pacing_rate = 100*1350*8;
    //*congestion_window = cwnd;
    /************** END CODE HERE ***************/
}

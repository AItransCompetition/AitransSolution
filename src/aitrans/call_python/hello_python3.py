import sys, pickle, os


def addition(a, b):
    return a+b


def call_pickle_model(model_path):
    # load model
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            model = pickle.load(f)
    # initial model
    else:
        model = {
            "w1" : 0.1,
            "w2" : 0.2,
            "w3" : [0.1, 0.2, 0.3],
            "w4" : {
                "w_w1" : 0.5,
                "w_w2" : [0.4, 0.5]
            }
        }

    # do calculation
    model["w1"] += 0.1
    model["w2"] += model["w1"]
    model["w3"].append(model["w1"])

    # save model
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    return model["w3"][0]


if __name__ == "__main__":
    mode = sys.argv[1]

    if mode == '0':
        print("Hello python3!")
    elif mode == '1':
        print(addition(float(sys.argv[2]), float(sys.argv[3])))
    elif mode == '2':
        print(call_pickle_model(sys.argv[2]))

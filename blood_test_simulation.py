import simpy
import random
import statistics

test_time_per_tube = []

class Centrigufe(object):
    def __init__(self, env, config):
        self.env = env
        
class TestLine(object):
    def __init__(self, env, config):
        self.env = env
        self.filler = simpy.Resource(env, config["num_fillers"])
        self.centrifuge = simpy.Resource(env, config["num_centrifuges"])
        self.centrifuge_containers = simpy.Resource(env, config["num_centrifuges_containers"])
        self.cetrifuge_container_size = simpy.Container(env, config["centrifuge_container_size"])
    
    def trip(self, path_time):
        yield self.env.timeout(path_time)
        
    def place_to_track(self, tube):
        yield self.env.timeout(25/60)
        

def make_test(env, tube, testLine):
    start_test_time = env.now

    # zatraži ubacivanje epruvete na traku
    with testLine.filler.request() as request:
        yield request
        yield env.process(testLine.place_to_track(tube))

    # simulacija puta do centrifuge
    yield env.process(testLine.trip(2))

    # zatraži ubacivanje epruvete na centrifugu
    
    # simulacija puta do testera
    yield env.process(testLine.trip(5))

    # simulacija puta vraćanja epruvete
    yield env.process(testLine.trip(10))


    test_time_per_tube.append(env.now - start_test_time)


def run_test_line(env, data, config):
    testLine = TestLine(env, config)

    start_time = data[0]["time"]

    for i in range(len(data)):
        tube = data[i]
        # čekaj vremenski period prije ubacivanja sljedeće epruvete
        yield env.timeout(tube["time"] - start_time)
        start_time = tube["time"]

        # pošalji epruvetu u proces
        env.process(make_test(env, tube, testLine))


def get_average_wait_time(test_time_per_tube):
    average_wait = statistics.mean(test_time_per_tube)
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)


def main():
    #DATA
    ids = [1, 2, 3, 4, 5, 6, 7]
    tests = [['a','b','c'],
            ['a','b','c'],
            ['a','b','c'],
            ['a','b','c'],
            ['a','b','c'],
            ['a','b','c'],
            ['a','b','c']]
    time = [12, 17, 20, 26, 28, 29, 35]

    data = []
    for i in range(len(ids)):
        tube = {
            "id": ids[i],
            "tests": tests[i],
            "time": time[i]
            }
        data.append(tube)

    #CONFIG
    config = {
            "num_fillers": 2,
            "num_centrifuges": 2,
            "num_centrifuges_containers": 4,
            "centrifuge_container_size": 100,
            }

    #PROCESS
    env = simpy.Environment()
    env.process(run_test_line(env, data, config))
    env.run()

    #RESULTS
    mins, secs = get_average_wait_time(test_time_per_tube)
    print(
        "Running simulation...",
        f"\nThe average wait time is {mins} minutes and {secs} seconds.",
    )


if __name__ == "__main__":
    main()
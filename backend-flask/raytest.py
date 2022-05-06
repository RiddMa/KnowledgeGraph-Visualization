import ray

ray.init()


@ray.remote
def f():
    return 1


futures = f.remote()
print(ray.get(futures))

from core.runtime import Runtime


if __name__ == "__main__":
    runtime = Runtime.from_config("configs/example_step.json")
    runtime.run()

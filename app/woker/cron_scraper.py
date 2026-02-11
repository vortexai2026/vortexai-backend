from scraper_worker_v2 import run

if __name__ == "__main__":
    # SAFE START
    run(batch_size=25, delay=4)

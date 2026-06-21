from scheduler import run_scrape
import time

print("🚀 Running scraper...")
start_time = time.time()
run_scrape()
end_time = time.time()

print(f"✅ Scraper completed in {(end_time - start_time)/60:.1f} minutes")
input("Press Enter to exit...")
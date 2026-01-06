import json
from datetime import datetime, timedelta
from tqdm import tqdm
from playwright.sync_api import sync_playwright
import multiprocessing


if __name__ == "__main__":
    # Windows 需要这个保护
    multiprocessing.freeze_support()
    pass
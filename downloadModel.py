from modelscope import snapshot_download


def download_m3e_model():
    model_dir = snapshot_download("Jerry0/m3e-base", cache_dir="model")
    return model_dir

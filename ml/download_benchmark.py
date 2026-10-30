from huggingface_hub import snapshot_download

path = snapshot_download(
    repo_id="ash12321/ai-detector-benchmark-test-data",
    repo_type="dataset",
    local_dir="data/benchmark",
)
print("Downloaded to:", path)
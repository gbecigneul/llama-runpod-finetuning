import json, os, random, subprocess, tempfile
import runpod

args = json.loads(os.environ.get("LLAMA_ARGS", "{}"))
MODEL = args["model"]

#TODO: ssh, env_var

words = [
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", 
    "lambda", "mu", "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", 
    "chi", "psi", "omega", "lion", "tiger", "bear", "wolf", "panther", "leopard", "lynx", 
    "elephant", "giraffe", "buffalo", "cheetah", "hyena", "penguin", "dolphin", "whale", 
    "shark", "eagle", "falcon", "parrot", "owl", "flamingo", "peacock", "sparrow", "swan", 
    "raven", "cobra", "viper", "python", "anaconda", "iguana", "gecko", "alligator", "crocodile"
]
def generate_random_model_id(word_count=3):
    return '-'.join(random.sample(words, word_count))

def upload_to_vps(file_path, remote_path, remote_user, remote_host):
    scp_command = [
        "scp",
        file_path,
        f"{remote_user}@{remote_host}:{remote_path}"
    ]
    subprocess.run(scp_command, check=True)

def handler(event):
    model_id = generate_random_model_id()
    lora_output = f"{model_id}-lora-ITERATION.bin"

    data = event['data']
    remote_host = event['remote_host']
    remote_user = event['remote_user']
    remote_path = event['remote_path']

    with tempfile.NamedTemporaryFile(mode='w', delete=True, suffix='.txt') as tmp_file:

        tmp_file.write(data)
        tmp_file.flush()

        finetune_command = [
            "./finetune",
            "--model-base", f"models/{MODEL}",
            "--lora-out", lora_output,
            "--train-data", tmp_file.name,
            "--save-every", "10",
            "--threads", "6", "--adam-iter", "30", "--batch", "4", "--ctx", "64",
            "--use-checkpointing" # replace by --no-checkpointing to speed up process but double RAM usage
        ]

        result = subprocess.run(finetune_command, check=False)

        if result.returncode == 0:
            try:
                upload_to_vps(lora_output, remote_path, remote_user, remote_host)
                upload_status = "COMPLETED"
            except Exception as e:
                upload_status = f"FAILED: {e}"
            return {"finetune_status": "COMPLETED", "upload_status": upload_status}
        else:
            return {"finetune_status": f"FAILED: {result.returncode}"}
 
runpod.serverless.start({"handler": handler})

 

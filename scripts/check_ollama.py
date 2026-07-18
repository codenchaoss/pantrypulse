import subprocess
import httpx
import sys

def check_ollama():
    print("=== Ollama Environment Check ===")
    
    # 1. Check CLI installation
    cli_installed = False
    try:
        # On Windows, shell=True matches standard CMD/PowerShell resolution
        res = subprocess.run(["ollama", "--version"], capture_output=True, text=True, shell=True)
        if res.returncode == 0:
            cli_installed = True
            print("[PASS] Ollama CLI is installed.")
            print(f"       Version: {res.stdout.strip()}")
        else:
            print("[FAIL] Ollama CLI returned non-zero exit code.")
    except Exception as e:
        print(f"[FAIL] Ollama CLI not found or failed to execute: {str(e)}")

    # 2. Check if localhost:11434 is reachable
    service_running = False
    url = "http://localhost:11434"
    try:
        response = httpx.get(url, timeout=3.0)
        if response.status_code == 200:
            service_running = True
            print("[PASS] Ollama service is reachable at localhost:11434.")
        else:
            print(f"[FAIL] Ollama service responded with HTTP status: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Ollama service is not reachable at localhost:11434. Error: {str(e)}")

    # 3. Check if llama3 model is available
    model_available = False
    if service_running:
        tags_url = f"{url}/api/tags"
        try:
            res_tags = httpx.get(tags_url, timeout=3.0)
            if res_tags.status_code == 200:
                models_data = res_tags.json()
                models = [m.get("name") for m in models_data.get("models", [])]
                print(f"       Available Models: {models}")
                llama3_found = any("llama3" in m.lower() for m in models)
                if llama3_found:
                    model_available = True
                    print("[PASS] llama3 model is pulled and available.")
                else:
                    print("[FAIL] llama3 model is missing in Ollama.")
            else:
                print(f"[FAIL] Failed to retrieve tags, HTTP: {res_tags.status_code}")
        except Exception as e:
            print(f"[FAIL] Error checking models: {str(e)}")
            
    # Display suggestions if needed
    if not service_running or not model_available:
        print("\n!!! ACTION REQUIRED: Ollama setup is incomplete !!!")
        if not service_running:
            print("Please start the Ollama service:")
            print("  Run command: ollama serve")
        if not model_available:
            print("Please pull the llama3 model:")
            print("  Run command: ollama pull llama3")
        sys.exit(1)
        
    print("\nAll checks passed successfully! Ollama is ready.")
    sys.exit(0)

if __name__ == "__main__":
    check_ollama()

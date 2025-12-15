"""
Monitor GitHub Actions Build #12
Check deployment status for REST API fallback fix
"""
import requests
import time

RUN_URL = "https://api.github.com/repos/vik9541/super-brain-digital-twin/actions/runs/20222495932"

print("=== GITHUB ACTIONS BUILD #12 MONITOR ===\n")
print("Deploying: REST API fallback fix (commit 6452507)")
print("Build URL: https://github.com/vik9541/super-brain-digital-twin/actions/runs/20222495932\n")

last_status = None
start_time = time.time()

while True:
    try:
        response = requests.get(RUN_URL)
        run = response.json()
        
        status = run.get('status', 'unknown')
        conclusion = run.get('conclusion', 'N/A')
        
        elapsed = int(time.time() - start_time)
        
        if status != last_status:
            print(f"[{time.strftime('%H:%M:%S')}] Status: {status} / Conclusion: {conclusion} (elapsed: {elapsed}s)")
            last_status = status
        
        if status == 'completed':
            print(f"\n{'='*50}")
            print(f"BUILD COMPLETE!")
            print(f"{'='*50}")
            print(f"Conclusion: {conclusion}")
            print(f"Total time: {elapsed}s")
            print(f"Updated: {run.get('updated_at')}")
            
            if conclusion == 'success':
                print("\n[SUCCESS] Deployment успешен!")
                print("Kubernetes автоматически обновит pod.")
                print("Подождите 2-3 минуты для применения изменений.")
                print("\nNext steps:")
                print("1. Wait 3 minutes for pod rollout")
                print("2. Test bot: send message to @astra_VIK_bot")
                print("3. Verify: python test_webhook_now.py")
            else:
                print(f"\n[FAILED] Build failed: {conclusion}")
                print(f"Check logs: {run.get('html_url')}")
            break
        
        time.sleep(5)  # Check every 5 seconds
        
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user.")
        print(f"Last status: {last_status}")
        print(f"Check manually: {RUN_URL}")
        break
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(5)

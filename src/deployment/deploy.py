"""Deploy script for Modal."""
import os
import subprocess
import sys


def main() -> None:
    """Deploy to Modal. Usage: deploy_dev or deploy_prod."""
    from dotenv import load_dotenv

    load_dotenv()

    env = "production" if "prod" in (sys.argv[0] or "") else "develop"
    modal_project = os.environ.get("MODAL_PROJECT")
    deploy_args = ["modal", "deploy"]
    if modal_project:
        deploy_args.extend(["-e", modal_project])

    # Ensure ENVIRONMENT is set so modal_workers uses correct app name and secrets
    deploy_env = os.environ.copy()
    deploy_env["ENVIRONMENT"] = env

    if env in ("develop", "production"):
        subprocess.run([*deploy_args, "src/deployment/modal_app.py"], check=True, env=deploy_env)
        subprocess.run([*deploy_args, "src/deployment/modal_workers.py"], check=True, env=deploy_env)
    else:
        print(f"Unknown environment: {env}")
        sys.exit(1)


if __name__ == "__main__":
    main()


from pathlib import Path
from cybulde.utils.utils import get_logger, run_shell_command
from subprocess import CalledProcessError


DATA_UTIL_LOGGER = get_logger(Path(__file__).name)


# Return if DVD was initialized
def is_dvc_initialized() -> bool:
    return (Path().cwd() / ".dvc").exists()


# Function to initialize DVC
def initialize_dvc() -> None:
    # If DVC is initialized, prevents to initialize again
    if is_dvc_initialized():
        DATA_UTIL_LOGGER.info("DVC is already initialize")
        return
    
    DATA_UTIL_LOGGER.info("Initializing DVC")

    # Run shell commands to initialize DVC
    run_shell_command("dvc init")
    # DVC won't collect any analytics from out repository
    run_shell_command("dvc config core.analytics false")
    # DVC will automatically stage any change we made on our data
    run_shell_command("dvc config core.autostage true")
    # Add .dvc folder (automatically created when DVC is initialize) to our GitHub repository
    run_shell_command("git add .dvc")
    # Commit our changes
    run_shell_command("git commit -m 'Initialized DVC'")


# Function to initialize DVC Storage
def initialize_dvc_storage(dvc_remote_name: str, dvc_remote_url: str) -> None:
    # Check if DVC Storage was already initialize
    if not run_shell_command("dvc remote list"):
        DATA_UTIL_LOGGER.info("Initializing DVC storage...")
        # Initializing DVC remote repository
        run_shell_command(f"dvc remote add -d {dvc_remote_name} {dvc_remote_url}")
        # Add DVC config to GitHub again (That's because the above command change .dvc/config)
        run_shell_command("git add .dvc/config")
        # Commit changes
        run_shell_command(f"git commit -m 'Configured remote storage at: {dvc_remote_url}'")
    else:
        DATA_UTIL_LOGGER.info("DVC storage was already initialized...")


# Function to create a new version of our dataset
def commit_to_dvc(dvc_raw_data_folder: str, dvc_remote_name: str) -> None:
    # Get the currently data version
    current_version = run_shell_command("git tag --list | sort -t v -k 2 -g | tail -1 | sed 's/v//'")
    if not current_version:
        current_version = "0"
    next_version = f"v{int(current_version) + 1}"
    # Added new data to DVC start tracking
    run_shell_command(f"dvc add {dvc_raw_data_folder}")
    # Add DVC files to GitHub again (That's because the above command change them)
    run_shell_command("git add .")
    # Commit changes
    run_shell_command(f"git commit -m 'Updated version of the data from v{current_version} to {next_version}'")
    # Assign a git tag for our new version
    run_shell_command(f"git tag -a {next_version} -m 'Data version {next_version}'")
    # Push new dataset to our remote storage
    run_shell_command(f"dvc push {dvc_raw_data_folder}.dvc --remote {dvc_remote_name}")
    # Push our changes to GitHub
    run_shell_command("git push --follow-tags")
    run_shell_command("git push -f --tags")
    

# Function to version data
def make_new_data_version(dvc_raw_data_folder: str, dvc_remote_name: str) -> None:
    # Version data only if there is some changes
    try:
        status = run_shell_command(f"dvc status {dvc_raw_data_folder}.dvc")
        # Check if our dataset was changed. If changed, create a new version
        if status == "Data and pipelines are up to date.\n":
            DATA_UTIL_LOGGER.info("Data and pipelines are up to date.")
            return
        commit_to_dvc(dvc_raw_data_folder, dvc_remote_name)
    except CalledProcessError:
        commit_to_dvc(dvc_raw_data_folder, dvc_remote_name)



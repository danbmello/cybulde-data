
from pathlib import Path
from cybulde.utils.utils import get_logger, run_shell_command


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


@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Determine Context
echo Starting Svonnalytics Attributes Analysis Setup ...
SET "IS_POPULATED=false"
SET "IS_GIT=false"
SET "REPO_ROOT=%~dp0"

:: Check if app.py is in the same directory
IF EXIST "!REPO_ROOT!\app.py" (
    SET "IS_POPULATED=true"
)

:: If not populated, handle installation
IF NOT "!IS_POPULATED!"=="true" (
    echo ^> Application not found in current directory.
    SET "GIT_INSTALL_PATH=%USERPROFILE%\PortableGit"

    :CheckInstallation
    echo ^> Checking if installation exists ...
    SET "PREV_INSTALLATION_EXISTS=false"
    IF EXIST "svonnalytics_install_dir.txt" (
        SET "PREV_INSTALLATION_EXISTS=true"
        FOR /F "delims=" %%i IN (svonnalytics_install_dir.txt) DO SET "REPO_ROOT=%%i"
        cd /d !REPO_ROOT!
        SET "PATH=!GIT_INSTALL_PATH!\bin;%PATH%"
        echo ^> Found installation in !REPO_ROOT!
    )

    IF NOT "!PREV_INSTALLATION_EXISTS!"=="true" (
        echo ^> No previous installation found.

        :EnterInstallPath
        SET /P INSTALL_DIR="USER INPUT: Enter installation directory (default: %USERPROFILE%\Documents\Svonnalytics\AttributeAnalysis): "
        IF "!INSTALL_DIR!"=="" SET "INSTALL_DIR=%USERPROFILE%\Documents\Svonnalytics\AttributeAnalysis"
        IF NOT EXIST "!INSTALL_DIR!" mkdir "!INSTALL_DIR!"

        :: Check for spaces in path
        IF "!INSTALL_DIR: =!" NEQ "!INSTALL_DIR!" (
            echo ERROR: The path contains spaces. Please choose a different directory.
            SET INSTALL_DIR=
            GOTO EnterInstallPath
        )

        :: Check for Git and install if necessary
        git --version >nul 2>&1
        IF NOT !ERRORLEVEL! EQU 0 (
            echo ^> Git is not installed. Installing portable Git...
            SET "GIT_INSTALLER=PortableGit-2.43.0-64-bit.7z.exe"
            SET "GIT_URL=https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/!GIT_INSTALLER!"

            :: Download Portable Git
            curl -L "!GIT_URL!" -o ".\!GIT_INSTALLER!"
            IF !ERRORLEVEL! NEQ 0 (
                echo ERROR: Something went wrong while downloading Portable Git.
                pause
                exit /b !ERRORLEVEL!
            )

            :: Run the self-extracting archive
            :: You can specify a directory for extraction if needed
            "!GIT_INSTALLER!" -y -o"!GIT_INSTALL_PATH!"
            IF !ERRORLEVEL! NEQ 0 (
                echo ERROR: Something went wrong extracting Portable Git.
                pause
                exit /b !ERRORLEVEL!
            )
            DEL "!GIT_INSTALLER!"
            SET "PATH=!GIT_INSTALL_PATH!\bin;%PATH%"
        )

        :: Clone the repository
        git clone https://github.com/Svonn/FM-Svonnalytics-Attribute-Analysis.git "!INSTALL_DIR!"
        IF !ERRORLEVEL! NEQ 0 (
            echo ERROR: Something went wrong cloning the repository.
            pause
            exit /b !ERRORLEVEL!
        )

        :: Store installation path
        < nul set /p="!INSTALL_DIR!" > svonnalytics_install_dir.txt
        GOTO CheckInstallation
    )

    cd /d !REPO_ROOT!
)

echo ^> Switched to target directory and ensured a valid git installation exists

:: Check if current directory is a git repository
IF EXIST ".git" (
    SET "IS_GIT=true"
)

:: If it's a Git repository, update it
IF "!IS_GIT!"=="true" (
    echo > Updating repository...
    git pull
    IF !ERRORLEVEL! NEQ 0 (
        echo ERROR: Something went wrong while updating the repository.
        pause
        exit /b !ERRORLEVEL!
    )
) ELSE (
    echo WARNING: The current directory is not managed by Git. Updates must be done manually.
)
echo ^> Checking if the installation is complete...

:: Check if the path contains spaces
:: This will search for a space in the path
IF "%REPO_ROOT: =%" NEQ "!REPO_ROOT!" (
    echo ERROR: The script cannot run in a path with spaces. Please move this directory to a path without whitespaces!
    pause
    exit /b 1
)

:: Check if Miniconda is installed in the repository
IF NOT EXIST "!REPO_ROOT!\Miniconda3\Scripts\conda.exe" (
    echo ^> Miniconda not found, installing to: "!REPO_ROOT!\Miniconda3"
    :: Specify a path within the repository to download Miniconda installer
    SET "MINICONDA_INSTALLER=!REPO_ROOT!\Miniconda3Installer.exe"

    :: Check if Miniconda installer already exists
    IF NOT EXIST "!MINICONDA_INSTALLER!" (
        echo ^> Downloading Miniconda to: !MINICONDA_INSTALLER!
        :: Download Miniconda installer
        curl -Lk "https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe" > "!MINICONDA_INSTALLER!" || (
            echo Error downloading Miniconda installer.
            pause
            exit /b 1
        )
    ) ELSE (
        echo ^> Miniconda installer already exists, using the existing file
    )


    :: Install Miniconda
    start /wait "" "!MINICONDA_INSTALLER!" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=!REPO_ROOT!\Miniconda3
    IF !ERRORLEVEL! NEQ 0 (
        echo ERROR: Something went wrong while installing Miniconda.
        pause
        exit /b !ERRORLEVEL!
    )

    echo ^> Miniconda installation complete.
) ELSE (
    echo ^> Miniconda is already installed.
)

:: Refresh environment variables to recognize Miniconda installation
CALL "!REPO_ROOT!\Miniconda3\Scripts\activate.bat"

:: Set local path to use the repository's Miniconda installation
SET "PATH=!REPO_ROOT!\Miniconda3;!REPO_ROOT!\Miniconda3\Scripts;!REPO_ROOT!\Miniconda3\Library\bin;!PATH!"

:: Check if the environment is already created
FOR /F "tokens=*" %%i IN ('"!REPO_ROOT!\Miniconda3\Scripts\conda.exe" info --envs') DO (
    echo %%i | findstr /C:"svonnalytics_env" >nul 2>&1
    IF !ERRORLEVEL! EQU 0 (
        SET ENV_EXISTS=1
    )
)

IF NOT DEFINED ENV_EXISTS (
    echo ^> Creating conda environment 'svonnalytics_env'...
    "!REPO_ROOT!\Miniconda3\Scripts\conda.exe" create --name svonnalytics_env python=3.12 --yes
    IF !ERRORLEVEL! NEQ 0 (
        echo Error creating conda environment.
        pause
        exit /b !ERRORLEVEL!
    )
    echo ^> Environment 'svonnalytics_env' created.
) ELSE (
    echo ^> Conda environment 'svonnalytics_env' already exists.
)

:: Activate the environment
CALL "!REPO_ROOT!\Miniconda3\Scripts\activate.bat" svonnalytics_env

:: Install or update requirements from requirements.txt
echo ^> Installing or updating requirements from requirements.txt...
"!REPO_ROOT!\Miniconda3\Scripts\conda.exe" install --name svonnalytics_env -c conda-forge --file requirements.txt --yes
IF !ERRORLEVEL! NEQ 0 (
    echo Error installing requirements.
    pause
    exit /b !ERRORLEVEL!
)
echo ^> Requirements installed or updated.

:: Run the Dash app in a new window
echo ^> Starting Dash application...
start cmd /k "python app.py --path "!CUSTOMPATH!""

:: Wait for 5 seconds to allow the server to start
timeout /t 5 /nobreak >nul

:: Open the Dash app in the default browser
echo ^> Opening Dash application in the browser...
start http://127.0.0.1:8050/

:: Pause the script to keep the window open
pause

ENDLOCAL

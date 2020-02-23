//! Determines the data and executable directories used to read and write resources
//! based on the process environment context and/or optional command line arguments.
//! Also creates necessary directories within the data directory if they don't exist.

use std::{
    env,
    fs,
    path::PathBuf,
    process::Command
};

use crate::library;

pub struct Context {
    blender_executable: PathBuf,
    pub data_dir: PathBuf,
    ffmpeg_executable: PathBuf,
    pub runtime_dir: PathBuf
}

impl Context {
    pub fn initialize() -> Context {
        let runtime_dir = process_path::get_executable_path()
                                       .expect("The runtime directory (where also the executable lies) could not be determined.")
                                       .parent()
                                       .unwrap()
                                       .to_path_buf();

        let data_dir = match env::args().nth(1) {
            Some(path) => PathBuf::from(path),
            None => runtime_dir.to_path_buf()
        };

        for dir in &["imports", "upload", "visualizations"] {
            let required_dir = data_dir.join(dir);

            if required_dir.is_dir() { continue }

            if let Err(err) = fs::create_dir(required_dir) {
                panic!("Could not create the required '{}' directory inside the data directory {}, received error: {}", dir, data_dir.display(), err)
            }
        }

        // TODO: Override via argument
        let blender_executable = runtime_dir.join(library::BLENDER);
        let ffmpeg_executable = runtime_dir.join(library::FFMPEG);

        Context {
            blender_executable,
            data_dir,
            ffmpeg_executable,
            runtime_dir
        }
    }

    pub fn blender_script_with_env(&self, script: &str) -> Command {
        let mut command = Command::new(&self.blender_executable);

        command.env("ELMYRA_DATA_DIR", &self.data_dir);
        command.env("ELMYRA_FFMPEG_EXECUTABLE", &self.ffmpeg_executable);
        command.env("ELMYRA_RUNTIME_DIR", &self.runtime_dir);

        command.arg("--background");
        command.arg("--python").arg(self.runtime_dir.join(script));
        command.arg("--");

        command
    }
}
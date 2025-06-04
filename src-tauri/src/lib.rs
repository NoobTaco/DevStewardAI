// DevSteward AI - Tauri Library
// 
// This module provides the core Tauri integration for DevSteward AI,
// including Python process management and API bridge functionality.

pub mod python_bridge;
pub mod process_manager;
pub mod commands;
pub mod types;

#[cfg(test)]
mod tests;

// Re-export commonly used types and functions
pub use python_bridge::PythonBridge;
pub use process_manager::ProcessManager;
pub use types::*;
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .plugin(tauri_plugin_shell::init())
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }
      // Sidecar is automatically handled by the shell plugin if configured in tauri.conf.json
      // But we can also explicitly spawn it here if needed for more control.
      // For now, let's rely on the shell plugin which we need to add.
      
      // Actually, for a persistent sidecar like a server, we usually spawn it here.
      use tauri_plugin_shell::ShellExt;
      let sidecar_command = app.shell().sidecar("api").unwrap();
      let (mut _rx, _child) = sidecar_command.spawn().expect("Failed to spawn sidecar");
      
      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}

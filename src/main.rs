use eframe::egui;
use egui::{Style, Visuals};
use libmpv::{FileState, Mpv};
use std::sync::{Arc, Mutex};

fn main() -> Result<(), eframe::Error> {
    env_logger::init();

    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1280.0, 720.0])
            .with_active(true),
        ..Default::default()
    };

    eframe::run_native(
        "LiveTL",
        options,
        Box::new(|cc| {
            egui_extras::install_image_loaders(&cc.egui_ctx);
            let style = Style {
                visuals: Visuals::dark(),
                ..Style::default()
            };
            cc.egui_ctx.set_style(style);
            Box::new(App::new(&cc))
        }),
    )
}

impl eframe::App for App {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        let scale_factor = 1.25;
        ctx.set_zoom_factor(scale_factor);
        let mut state = self.state.lock().unwrap();
        egui::CentralPanel::default().show(ctx, |ui| {
            egui::SidePanel::left("left_panel")
                .resizable(false)
                .show_inside(ui, |ui| {
                    ui.horizontal(|ui| {
                        ui.label("Link: ");
                        ui.add(
                            egui::TextEdit::singleline(&mut state.stream_link)
                                .hint_text("https://www.youtube.com/watch?v=..."),
                        );
                        if ui.button("start").clicked() {
                            println!("{}", state.stream_link);
                            state.video_started = true;
                        }
                    });
                    ui.separator();
                });
            // create strip in remaining width with 16:9 ratio
            let height = ui.available_width() * (9.0 / 16.0);
            let margin = (ui.available_height() - height) / 2.0;

            egui_extras::StripBuilder::new(ui)
                .size(egui_extras::Size::exact(margin))
                .size(egui_extras::Size::exact(height))
                .size(egui_extras::Size::exact(margin))
                .vertical(|mut strip| {
                    strip.cell(|ui| {});
                    strip.cell(|ui| {
                        ui.horizontal_centered(|ui| {
                            ui.painter().rect_filled(
                                ui.available_rect_before_wrap(),
                                0.0,
                                egui::Color32::BLACK,
                            );
                            state.video_corners = [
                                ui.available_rect_before_wrap()
                                    .expand(scale_factor * ctx.pixels_per_point())
                                    .min,
                                ui.available_rect_before_wrap()
                                    .expand(scale_factor * ctx.pixels_per_point())
                                    .max,
                            ];
                        });
                    });
                    strip.cell(|ui| {});
                });
        });
    }
}

fn handle_video_player(state: Arc<Mutex<State>>) {
    let mpv = Mpv::new().expect("Failed to create mpv instance");

    mpv.set_property("ontop", "yes").unwrap();
    mpv.set_property("border", "no").unwrap();
    mpv.set_property("title-bar", "no").unwrap();

    let mut ev_ctx = mpv.create_event_context();
    ev_ctx.disable_deprecated_events().unwrap();

    loop {
        if let Some(ev) = ev_ctx.wait_event(0.1) {
            match ev {
                Ok(e) => println!("Event: {:?}", e),
                Err(e) => println!("Error: {:?}", e),
            }
        }

        let corners = state.lock().unwrap().video_corners;
        // convert x and y into pixels
        let x = corners[0].x as i32;
        let y = corners[0].y as i32;
        let width = (corners[1].x - corners[0].x) as i32;
        let height = (corners[1].y - corners[0].y) as i32;
        mpv.set_property("geometry", format!("{}x{}+{}+{}", width, height, x, y))
            .unwrap();

        if state.lock().unwrap().video_started {
            let stream_link = state.lock().unwrap().stream_link.clone();
            state.lock().unwrap().video_started = false;
            mpv.playlist_remove_current().unwrap_or_default();
            mpv.playlist_load_files(&[(&stream_link, FileState::AppendPlay, None)])
                .unwrap();
            println!("Added link");
        }
    }
}

struct State {
    ctx: Option<egui::Context>,
    stream_link: String,
    video_started: bool,
    video_corners: [egui::Pos2; 2],
}

impl State {
    fn new() -> Self {
        Self {
            ctx: None,
            stream_link: Default::default(),
            video_started: false,
            video_corners: Default::default(),
        }
    }
}

struct App {
    state: Arc<Mutex<State>>,
}

impl App {
    pub fn new(cc: &eframe::CreationContext) -> Self {
        let state = Arc::new(Mutex::new(State::new()));
        state.lock().unwrap().ctx = Some(cc.egui_ctx.clone());

        let state_clone = state.clone();
        std::thread::spawn(move || {
            handle_video_player(state_clone);
        });
        Self { state }
    }
}

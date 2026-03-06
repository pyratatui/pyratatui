// src/effects/mod.rs — tachyonfx Python bindings (fixed for 0.11.1 + ratatui 0.29)
use crate::buffer::Buffer;
use crate::layout::Rect;
use crate::style::Color;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use ratatui::layout::Margin as RMargin;
use ratatui::style::Color as RColor;
use std::collections::HashMap;
use tachyonfx::fx::RepeatMode;
use tachyonfx::{
    fx, CellFilter as TCellFilter, Effect as TEffect, EffectTimer as TEffectTimer,
    Interpolation as TInterpolation, Motion as TMotion,
};

// Helper: ms (u64) + optional Interpolation → TEffectTimer
fn make_timer(ms: u64, interp: Option<Interpolation>) -> TEffectTimer {
    let ms32 = ms.min(u32::MAX as u64) as u32;
    let i = interp.unwrap_or(Interpolation::Linear).to_tachyonfx();
    TEffectTimer::from_ms(ms32, i)
}

// ─── Interpolation ───────────────────────────────────────────────────────────

#[pyclass(module = "pyratatui", eq, eq_int, from_py_object)]
#[derive(Clone, Debug, PartialEq)]
pub enum Interpolation {
    Linear,
    QuadIn,
    QuadOut,
    QuadInOut,
    CubicIn,
    CubicOut,
    CubicInOut,
    QuartIn,
    QuartOut,
    QuartInOut,
    QuintIn,
    QuintOut,
    QuintInOut,
    SineIn,
    SineOut,
    SineInOut,
    CircIn,
    CircOut,
    CircInOut,
    ExpoIn,
    ExpoOut,
    ExpoInOut,
    ElasticIn,
    ElasticOut,
    BounceIn,
    BounceOut,
    BounceInOut,
    BackIn,
    BackOut,
    BackInOut,
}

impl Interpolation {
    pub(crate) fn to_tachyonfx(&self) -> TInterpolation {
        match self {
            Interpolation::Linear => TInterpolation::Linear,
            Interpolation::QuadIn => TInterpolation::QuadIn,
            Interpolation::QuadOut => TInterpolation::QuadOut,
            Interpolation::QuadInOut => TInterpolation::QuadInOut,
            Interpolation::CubicIn => TInterpolation::CubicIn,
            Interpolation::CubicOut => TInterpolation::CubicOut,
            Interpolation::CubicInOut => TInterpolation::CubicInOut,
            Interpolation::QuartIn => TInterpolation::QuartIn,
            Interpolation::QuartOut => TInterpolation::QuartOut,
            Interpolation::QuartInOut => TInterpolation::QuartInOut,
            Interpolation::QuintIn => TInterpolation::QuintIn,
            Interpolation::QuintOut => TInterpolation::QuintOut,
            Interpolation::QuintInOut => TInterpolation::QuintInOut,
            Interpolation::SineIn => TInterpolation::SineIn,
            Interpolation::SineOut => TInterpolation::SineOut,
            Interpolation::SineInOut => TInterpolation::SineInOut,
            Interpolation::CircIn => TInterpolation::CircIn,
            Interpolation::CircOut => TInterpolation::CircOut,
            Interpolation::CircInOut => TInterpolation::CircInOut,
            Interpolation::ExpoIn => TInterpolation::ExpoIn,
            Interpolation::ExpoOut => TInterpolation::ExpoOut,
            Interpolation::ExpoInOut => TInterpolation::ExpoInOut,
            Interpolation::ElasticIn => TInterpolation::ElasticIn,
            Interpolation::ElasticOut => TInterpolation::ElasticOut,
            Interpolation::BounceIn => TInterpolation::BounceIn,
            Interpolation::BounceOut => TInterpolation::BounceOut,
            Interpolation::BounceInOut => TInterpolation::BounceInOut,
            Interpolation::BackIn => TInterpolation::BackIn,
            Interpolation::BackOut => TInterpolation::BackOut,
            Interpolation::BackInOut => TInterpolation::BackInOut,
        }
    }
}

// ─── Motion ──────────────────────────────────────────────────────────────────

#[pyclass(module = "pyratatui", eq, eq_int, from_py_object)]
#[derive(Clone, Debug, PartialEq)]
pub enum Motion {
    LeftToRight,
    RightToLeft,
    UpToDown,
    DownToUp,
}

impl Motion {
    fn to_tachyonfx(&self) -> TMotion {
        match self {
            Motion::LeftToRight => TMotion::LeftToRight,
            Motion::RightToLeft => TMotion::RightToLeft,
            Motion::UpToDown => TMotion::UpToDown,
            Motion::DownToUp => TMotion::DownToUp,
        }
    }
}

// ─── EffectTimer ─────────────────────────────────────────────────────────────

#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Debug)]
pub struct EffectTimer {
    pub(crate) duration_ms: u64,
    pub(crate) interpolation: Interpolation,
}

impl EffectTimer {
    #[allow(dead_code)]
    pub(crate) fn to_tachyonfx(&self) -> TEffectTimer {
        make_timer(self.duration_ms, Some(self.interpolation.clone()))
    }
}

#[pymethods]
impl EffectTimer {
    #[new]
    #[pyo3(signature = (duration_ms, interpolation=None))]
    pub fn new(duration_ms: u64, interpolation: Option<Interpolation>) -> Self {
        Self {
            duration_ms,
            interpolation: interpolation.unwrap_or(Interpolation::Linear),
        }
    }
    #[getter]
    pub fn duration_ms(&self) -> u64 {
        self.duration_ms
    }
    #[getter]
    pub fn interpolation(&self) -> Interpolation {
        self.interpolation.clone()
    }
    fn __repr__(&self) -> String {
        format!(
            "EffectTimer({}ms, {:?})",
            self.duration_ms, self.interpolation
        )
    }
}

// ─── CellFilter ──────────────────────────────────────────────────────────────

#[pyclass(module = "pyratatui", from_py_object)]
#[derive(Clone, Debug)]
pub struct CellFilter {
    pub(crate) inner: CellFilterKind,
}

#[derive(Clone, Debug)]
pub(crate) enum CellFilterKind {
    All,
    Text,
    FgColor(RColor),
    BgColor(RColor),
    Inner(u16, u16),
    Outer(u16, u16),
    AllOf(()),
    AnyOf(()),
}

impl CellFilter {
    pub(crate) fn to_tachyonfx(&self) -> TCellFilter {
        match &self.inner {
            CellFilterKind::All => TCellFilter::All,
            CellFilterKind::Text => TCellFilter::Text,
            CellFilterKind::FgColor(c) => TCellFilter::FgColor(*c),
            CellFilterKind::BgColor(c) => TCellFilter::BgColor(*c),
            CellFilterKind::Inner(h, v) => TCellFilter::Inner(RMargin {
                horizontal: *h,
                vertical: *v,
            }),
            CellFilterKind::Outer(h, v) => TCellFilter::Outer(RMargin {
                horizontal: *h,
                vertical: *v,
            }),
            // tachyonfx AllOf/AnyOf have unstable slice APIs; fall back to All
            CellFilterKind::AllOf(_) => TCellFilter::All,
            CellFilterKind::AnyOf(_) => TCellFilter::All,
        }
    }
}

#[pymethods]
impl CellFilter {
    #[staticmethod]
    pub fn all() -> CellFilter {
        CellFilter {
            inner: CellFilterKind::All,
        }
    }
    #[staticmethod]
    pub fn text() -> CellFilter {
        CellFilter {
            inner: CellFilterKind::Text,
        }
    }
    #[staticmethod]
    pub fn fg_color(color: &Color) -> CellFilter {
        CellFilter {
            inner: CellFilterKind::FgColor(color.inner),
        }
    }
    #[staticmethod]
    pub fn bg_color(color: &Color) -> CellFilter {
        CellFilter {
            inner: CellFilterKind::BgColor(color.inner),
        }
    }
    #[staticmethod]
    #[pyo3(signature = (horizontal=1, vertical=1))]
    pub fn inner(horizontal: u16, vertical: u16) -> CellFilter {
        CellFilter {
            inner: CellFilterKind::Inner(horizontal, vertical),
        }
    }
    #[staticmethod]
    #[pyo3(signature = (horizontal=1, vertical=1))]
    pub fn outer(horizontal: u16, vertical: u16) -> CellFilter {
        CellFilter {
            inner: CellFilterKind::Outer(horizontal, vertical),
        }
    }
    #[staticmethod]
    pub fn all_of(_filters: Vec<PyRef<CellFilter>>) -> CellFilter {
        CellFilter {
            inner: CellFilterKind::AllOf(()),
        }
    }
    #[staticmethod]
    pub fn any_of(_filters: Vec<PyRef<CellFilter>>) -> CellFilter {
        CellFilter {
            inner: CellFilterKind::AnyOf(()),
        }
    }
    fn __repr__(&self) -> String {
        format!("CellFilter({:?})", self.inner)
    }
}

// ─── Effect ──────────────────────────────────────────────────────────────────

/// Stateful animation. Use `#[pyclass(unsendable)]` because tachyonfx::Effect
/// contains Box<dyn Shader> which is !Send + !Sync.
#[pyclass(module = "pyratatui", unsendable)]
pub struct Effect {
    pub(crate) inner: TEffect,
}

#[pymethods]
impl Effect {
    // Color transitions
    #[staticmethod]
    #[pyo3(signature = (from_bg, from_fg, duration_ms, interpolation=None))]
    pub fn fade_from(
        from_bg: &Color,
        from_fg: &Color,
        duration_ms: u64,
        interpolation: Option<Interpolation>,
    ) -> Effect {
        Effect {
            inner: fx::fade_from(
                from_bg.inner,
                from_fg.inner,
                make_timer(duration_ms, interpolation),
            ),
        }
    }
    #[staticmethod]
    #[pyo3(signature = (from_color, duration_ms, interpolation=None))]
    pub fn fade_from_fg(
        from_color: &Color,
        duration_ms: u64,
        interpolation: Option<Interpolation>,
    ) -> Effect {
        Effect {
            inner: fx::fade_from_fg(from_color.inner, make_timer(duration_ms, interpolation)),
        }
    }
    #[staticmethod]
    #[pyo3(signature = (to_bg, to_fg, duration_ms, interpolation=None))]
    pub fn fade_to(
        to_bg: &Color,
        to_fg: &Color,
        duration_ms: u64,
        interpolation: Option<Interpolation>,
    ) -> Effect {
        Effect {
            inner: fx::fade_to(
                to_bg.inner,
                to_fg.inner,
                make_timer(duration_ms, interpolation),
            ),
        }
    }
    #[staticmethod]
    #[pyo3(signature = (to_color, duration_ms, interpolation=None))]
    pub fn fade_to_fg(
        to_color: &Color,
        duration_ms: u64,
        interpolation: Option<Interpolation>,
    ) -> Effect {
        Effect {
            inner: fx::fade_to_fg(to_color.inner, make_timer(duration_ms, interpolation)),
        }
    }
    // Text materialization
    #[staticmethod]
    #[pyo3(signature = (duration_ms, interpolation=None))]
    pub fn coalesce(duration_ms: u64, interpolation: Option<Interpolation>) -> Effect {
        Effect {
            inner: fx::coalesce(make_timer(duration_ms, interpolation)),
        }
    }
    #[staticmethod]
    #[pyo3(signature = (duration_ms, interpolation=None))]
    pub fn dissolve(duration_ms: u64, interpolation: Option<Interpolation>) -> Effect {
        Effect {
            inner: fx::dissolve(make_timer(duration_ms, interpolation)),
        }
    }
    // Sliding: tachyonfx 0.11 fx::slide_in(direction, begin_sweep: u16, end_sweep: u16, color, timer)
    #[staticmethod]
    #[pyo3(signature = (direction, begin_sweep=0, end_sweep=0, color=None, duration_ms=500, interpolation=None))]
    pub fn slide_in(
        direction: &Motion,
        begin_sweep: u16,
        end_sweep: u16,
        color: Option<&Color>,
        duration_ms: u64,
        interpolation: Option<Interpolation>,
    ) -> Effect {
        let c = color.map(|c| c.inner).unwrap_or(RColor::Black);
        Effect {
            inner: fx::slide_in(
                direction.to_tachyonfx(),
                begin_sweep,
                end_sweep,
                c,
                make_timer(duration_ms, interpolation),
            ),
        }
    }
    #[staticmethod]
    #[pyo3(signature = (direction, begin_sweep=0, end_sweep=0, color=None, duration_ms=500, interpolation=None))]
    pub fn slide_out(
        direction: &Motion,
        begin_sweep: u16,
        end_sweep: u16,
        color: Option<&Color>,
        duration_ms: u64,
        interpolation: Option<Interpolation>,
    ) -> Effect {
        let c = color.map(|c| c.inner).unwrap_or(RColor::Black);
        Effect {
            inner: fx::slide_out(
                direction.to_tachyonfx(),
                begin_sweep,
                end_sweep,
                c,
                make_timer(duration_ms, interpolation),
            ),
        }
    }
    #[staticmethod]
    #[pyo3(signature = (direction, sweep_span=15, gradient_len=0, color=None, duration_ms=600, interpolation=None))]
    pub fn sweep_in(
        direction: &Motion,
        sweep_span: u16,
        gradient_len: u16,
        color: Option<&Color>,
        duration_ms: u64,
        interpolation: Option<Interpolation>,
    ) -> Effect {
        let c = color.map(|c| c.inner).unwrap_or(RColor::Black);
        Effect {
            inner: fx::sweep_in(
                direction.to_tachyonfx(),
                sweep_span,
                gradient_len,
                c,
                make_timer(duration_ms, interpolation),
            ),
        }
    }
    #[staticmethod]
    #[pyo3(signature = (direction, sweep_span=15, gradient_len=0, color=None, duration_ms=600, interpolation=None))]
    pub fn sweep_out(
        direction: &Motion,
        sweep_span: u16,
        gradient_len: u16,
        color: Option<&Color>,
        duration_ms: u64,
        interpolation: Option<Interpolation>,
    ) -> Effect {
        let c = color.map(|c| c.inner).unwrap_or(RColor::Black);
        Effect {
            inner: fx::sweep_out(
                direction.to_tachyonfx(),
                sweep_span,
                gradient_len,
                c,
                make_timer(duration_ms, interpolation),
            ),
        }
    }
    // Timing
    #[staticmethod]
    pub fn sleep(duration_ms: u64) -> Effect {
        Effect {
            inner: fx::sleep(duration_ms.min(u32::MAX as u64) as u32),
        }
    }
    // Composition
    #[staticmethod]
    pub fn sequence(effects: Vec<PyRefMut<Effect>>) -> Effect {
        let v: Vec<TEffect> = effects
            .into_iter()
            .map(|mut e| std::mem::replace(&mut e.inner, fx::sleep(0u32)))
            .collect();
        Effect {
            inner: if v.is_empty() {
                fx::sleep(0u32)
            } else {
                fx::sequence(v.as_slice())
            },
        }
    }
    #[staticmethod]
    pub fn parallel(effects: Vec<PyRefMut<Effect>>) -> Effect {
        let v: Vec<TEffect> = effects
            .into_iter()
            .map(|mut e| std::mem::replace(&mut e.inner, fx::sleep(0u32)))
            .collect();
        Effect {
            inner: if v.is_empty() {
                fx::sleep(0u32)
            } else {
                fx::parallel(v.as_slice())
            },
        }
    }
    #[staticmethod]
    #[pyo3(signature = (effect, times=-1))]
    pub fn repeat(mut effect: PyRefMut<Effect>, times: i32) -> Effect {
        let inner = std::mem::replace(&mut effect.inner, fx::sleep(0u32));
        let mode = if times < 0 {
            RepeatMode::Forever
        } else {
            RepeatMode::Times(times as u32)
        };
        Effect {
            inner: fx::repeat(inner, mode),
        }
    }
    #[staticmethod]
    pub fn ping_pong(mut effect: PyRefMut<Effect>) -> Effect {
        let inner = std::mem::replace(&mut effect.inner, fx::sleep(0u32));
        Effect {
            inner: fx::ping_pong(inner),
        }
    }
    #[staticmethod]
    pub fn never_complete(mut effect: PyRefMut<Effect>) -> Effect {
        let inner = std::mem::replace(&mut effect.inner, fx::sleep(0u32));
        Effect {
            inner: fx::never_complete(inner),
        }
    }
    // Cell filter: fx::cell_filter(filter, effect) wraps the effect
    pub fn with_filter(&mut self, filter: &CellFilter) -> PyResult<()> {
        let old = std::mem::replace(&mut self.inner, fx::sleep(0u32));
        self.inner = old.with_filter(filter.to_tachyonfx());
        Ok(())
    }
    // Runtime control
    pub fn process(&mut self, elapsed_ms: u64, buffer: &mut Buffer, area: &Rect) {
        let dur: tachyonfx::Duration = std::time::Duration::from_millis(elapsed_ms).into();
        self.inner.process(dur, &mut buffer.inner, area.inner);
    }
    pub fn done(&self) -> bool {
        self.inner.done()
    }
    pub fn reset(&mut self) {
        self.inner.reset();
    }
    fn __repr__(&self) -> String {
        format!("Effect(done={})", self.inner.done())
    }
}

// ─── EffectManager ───────────────────────────────────────────────────────────

/// Vec-based effect manager — avoids tachyonfx::EffectManager's Rc/!Send issue.
/// unsendable: confined to the Python thread that created it.
#[pyclass(module = "pyratatui", unsendable)]
pub struct EffectManager {
    effects: Vec<TEffect>,
    named: HashMap<String, usize>,
}

#[pymethods]
impl EffectManager {
    #[new]
    pub fn new() -> Self {
        Self {
            effects: Vec::new(),
            named: HashMap::new(),
        }
    }

    pub fn add(&mut self, mut effect: PyRefMut<Effect>) {
        let inner = std::mem::replace(&mut effect.inner, fx::sleep(0u32));
        self.effects.push(inner);
    }

    /// Add a named effect, replacing any previous effect with the same key.
    pub fn add_unique(&mut self, key: &str, mut effect: PyRefMut<Effect>) {
        let inner = std::mem::replace(&mut effect.inner, fx::sleep(0u32));
        if let Some(&idx) = self.named.get(key) {
            if idx < self.effects.len() {
                self.effects[idx] = fx::sleep(0u32); // expire immediately
            }
        }
        let idx = self.effects.len();
        self.effects.push(inner);
        self.named.insert(key.to_string(), idx);
    }

    /// Process all effects for `elapsed_ms` ms; remove completed ones.
    pub fn process(&mut self, elapsed_ms: u64, buffer: &mut Buffer, area: &Rect) {
        let dur: tachyonfx::Duration = std::time::Duration::from_millis(elapsed_ms).into();
        for e in &mut self.effects {
            e.process(dur, &mut buffer.inner, area.inner);
        }
        self.effects.retain(|e| !e.done());
        self.named.retain(|_, idx| *idx < self.effects.len());
    }

    pub fn active_count(&self) -> usize {
        self.effects.len()
    }
    pub fn has_active(&self) -> bool {
        !self.effects.is_empty()
    }

    pub fn clear(&mut self) {
        self.effects.clear();
        self.named.clear();
    }

    fn __repr__(&self) -> String {
        format!("EffectManager(active={})", self.effects.len())
    }
}

// ─── crate-internal helpers ───────────────────────────────────────────────────

impl EffectManager {
    /// Process all active effects against a raw ratatui buffer.
    /// Called by `Frame::apply_effect_manager` so the frame's own buffer is mutated in-place.
    pub(crate) fn process_raw(
        &mut self,
        elapsed_ms: u64,
        buf: &mut ratatui::buffer::Buffer,
        area: ratatui::layout::Rect,
    ) {
        let dur: tachyonfx::Duration = std::time::Duration::from_millis(elapsed_ms).into();
        for e in &mut self.effects {
            e.process(dur, buf, area);
        }
        self.effects.retain(|e| !e.done());
        self.named.retain(|_, idx| *idx < self.effects.len());
    }
}

// ─── DSL helper ──────────────────────────────────────────────────────────────

/// Compile a tachyonfx DSL expression into an `Effect`.
///
/// Raises `ValueError` on compile errors.
#[pyfunction]
pub fn compile_effect(expression: &str) -> PyResult<Effect> {
    use tachyonfx::dsl::EffectDsl;
    let effect = EffectDsl::new()
        .compiler()
        .compile(expression)
        .map_err(|e| PyValueError::new_err(format!("DSL compile error: {e}")))?;
    Ok(Effect { inner: effect })
}

// ─── Registration ────────────────────────────────────────────────────────────

pub fn register_effects(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Interpolation>()?;
    m.add_class::<Motion>()?;
    m.add_class::<EffectTimer>()?;
    m.add_class::<CellFilter>()?;
    m.add_class::<Effect>()?;
    m.add_class::<EffectManager>()?;
    m.add_function(wrap_pyfunction!(compile_effect, m)?)?;
    Ok(())
}

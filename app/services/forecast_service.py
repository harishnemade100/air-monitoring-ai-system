"""Charts for forecasts and trends (Plotly)."""
import pandas as pd
import plotly.graph_objects as go

from utils.color_utils import aqi_color, aqi_health_label

# US AQI bands drawn behind charts
_BANDS = [(0, 50, "#00e400"), (50, 100, "#ffff00"), (100, 150, "#ff7e00"),
          (150, 200, "#ff0000"), (200, 300, "#8f3f97"), (300, 500, "#7e0023")]


def _now_line(fig, now):
    if now is not None:
        fig.add_vline(x=now, line_dash="dash", line_color="gray")
        fig.add_annotation(x=now, y=1, yref="paper", text="Now", showarrow=False, yanchor="bottom")


def plot_aqi_trend(hourly: pd.DataFrame, show_india: bool = True):
    """Real hourly AQI: past days + forecast, with health bands."""
    fig = go.Figure()
    top = max(150, (hourly["US AQI"].max() or 0) + 20)
    for lo, hi, colour in _BANDS:
        if lo < top:
            fig.add_hrect(y0=lo, y1=min(hi, top), fillcolor=colour, opacity=0.08, line_width=0)
    fig.add_trace(go.Scatter(
        x=hourly["datetime"], y=hourly["US AQI"], mode="lines+markers", name="US AQI",
        marker=dict(color=[aqi_color(v) for v in hourly["US AQI"]], size=5), line=dict(color="#1f77b4"),
        text=[aqi_health_label(v) for v in hourly["US AQI"]],
        hovertemplate="%{x|%d %b %H:%M}<br>US AQI: %{y}<br>%{text}<extra></extra>",
    ))
    if show_india and "India AQI" in hourly:
        fig.add_trace(go.Scatter(
            x=hourly["datetime"], y=hourly["India AQI"], mode="lines", name="India AQI (CPCB, 24h)",
            line=dict(color="#ff7f0e", dash="dot"),
            hovertemplate="%{x|%d %b %H:%M}<br>India AQI: %{y}<extra></extra>",
        ))
    _now_line(fig, hourly.attrs.get("now"))
    fig.update_layout(height=380, hovermode="x unified", yaxis_title="AQI", xaxis_title="",
                      yaxis_range=[0, top], legend=dict(orientation="h", y=-0.15), margin=dict(t=30))
    return fig


def plot_pollutants(hourly: pd.DataFrame, pollutants: list[str]):
    """Pollutant concentrations over time (µg/m³)."""
    fig = go.Figure()
    for p in pollutants:
        if p in hourly:
            fig.add_trace(go.Scatter(x=hourly["datetime"], y=hourly[p], mode="lines", name=p,
                                     hovertemplate=f"%{{x|%d %b %H:%M}}<br>{p}: %{{y:.1f}} µg/m³<extra></extra>"))
    _now_line(fig, hourly.attrs.get("now"))
    fig.update_layout(height=360, hovermode="x unified", yaxis_title="µg/m³", xaxis_title="",
                      legend=dict(orientation="h", y=-0.15), margin=dict(t=30))
    return fig


def plot_weather_forecast(weather_df: pd.DataFrame):
    """Temperature line + humidity bars (next 5 days)."""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=weather_df["datetime"], y=weather_df["Humidity"], name="Humidity (%)",
                         marker_color="rgba(31,119,180,0.25)", yaxis="y2",
                         hovertemplate="Humidity: %{y}%<extra></extra>"))
    fig.add_trace(go.Scatter(x=weather_df["datetime"], y=weather_df["Temp"], name="Temperature (°C)",
                             mode="lines+markers", line=dict(color="#ff7f0e"),
                             hovertemplate="%{x|%d %b %H:%M}<br>Temp: %{y:.1f} °C<extra></extra>"))
    fig.update_layout(
        height=360, hovermode="x unified", margin=dict(t=30), legend=dict(orientation="h", y=-0.15),
        yaxis=dict(title="°C"), yaxis2=dict(title="%", overlaying="y", side="right", range=[0, 100]),
    )
    return fig


def plot_station_bars(df_towers: pd.DataFrame):
    """Station-wise AQI as coloured bars (replaces the old pie chart, which summed AQI values)."""
    df = df_towers.dropna(subset=["AQI"]).sort_values("AQI").copy()
    short = df["Station"].str.split(",").str[0].str.slice(0, 32)
    if "Source" in df:
        short = short + df["Source"].map(lambda s: " (est.)" if s == "Model estimate" else "")
    df["Label"] = short
    fig = go.Figure(go.Bar(
        x=df["AQI"], y=df["Label"], orientation="h", customdata=df["Station"],
        marker_color=[aqi_color(v) for v in df["AQI"]],
        text=df["AQI"], textposition="outside",
        hovertemplate="%{customdata}<br>AQI: %{x}<extra></extra>",
    ))
    fig.update_layout(height=max(300, 28 * len(df) + 80), xaxis_title="US AQI", yaxis_title="",
                      yaxis=dict(type="category"),
                      margin=dict(l=10, r=30, t=30))
    return fig


def plot_city_comparison(df: pd.DataFrame, highlight: str | None = None):
    df = df.sort_values("US AQI")
    colours = [aqi_color(v) for v in df["US AQI"]]
    fig = go.Figure(go.Bar(
        x=df["US AQI"], y=df["City"], orientation="h", marker_color=colours,
        marker_line_width=[3 if c == highlight else 0 for c in df["City"]], marker_line_color="black",
        text=df["US AQI"].round(0).astype(int), textposition="outside",
        hovertemplate="%{y}<br>US AQI: %{x}<extra></extra>",
    ))
    fig.update_layout(height=max(350, 30 * len(df) + 80), xaxis_title="US AQI (now)", yaxis_title="",
                      margin=dict(l=10, r=30, t=30))
    return fig

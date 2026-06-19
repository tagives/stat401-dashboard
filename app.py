from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# ---------- Load data from CSVs ----------
q1_pdf = pd.read_csv("q1_pdf.csv")
q2_pdf = pd.read_csv("q2_pdf.csv")
q3_pdf = pd.read_csv("q3_pdf.csv")
q3_kw_pdf = pd.read_csv("q3_kw_pdf.csv")
q4_pdf = pd.read_csv("q4_pdf.csv")
q5_pdf = pd.read_csv("q5_pdf.csv")
q6_pdf = pd.read_csv("q6_pdf.csv")

# ---------- Create Dash app ----------
app = Dash(__name__)
server = app.server  # needed for Render and gunicorn

app.layout = html.Div([
    html.H1("TBMM – Deprem, Konut ve Mali Politika Dashboard",
            style={"textAlign": "center"}),

    dcc.Tabs(
        id="tabs",
        value="q1",
        children=[
            dcc.Tab(label="Q1: Sosyal vs Afet Konut", value="q1"),
            dcc.Tab(label="Q2: Bakanlık vs KDB", value="q2"),
            dcc.Tab(label="Q3: Bakanlıklara Soru & Anahtar Kelimeler", value="q3"),
            dcc.Tab(label="Q4: İllere Göre Araştırma Önergeleri", value="q4"),
            dcc.Tab(label="Q5: İdari Para Cezaları", value="q5"),
            dcc.Tab(label="Q6: Vergi / Borç Düzenlemeleri", value="q6"),
        ]
    ),

    html.Div(id="tab-content", style={"marginTop": "20px"})
])

# ---------- Your callback ----------
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def render_tab(tab):
    if tab == "q1":
        fig = px.bar(
            q1_pdf,
            x="year",
            y=["sosyal_konut", "afet_konut"],
            barmode="group",
            title="Q1 – Sosyal Konut vs Afet Konut (Yıllara Göre)",
            labels={"value": "Yasa Sayısı", "variable": "Kategori", "year": "Yıl"}
        )
        fig_ratio = px.line(
            q1_pdf,
            x="year",
            y="ratio_sosyal_to_afet",
            markers=True,
            title="Sosyal / Afet Konut Oranı"
        )
        return html.Div([
            dcc.Graph(figure=fig),
            dcc.Graph(figure=fig_ratio),
        ])

    if tab == "q2":
        fig = px.line(
            q2_pdf,
            x="year",
            y=["bakanlik_refs", "kdb_refs"],
            markers=True,
            title="Q2 – Bakanlık vs Kentsel Dönüşüm Başkanlığı Atıfları",
            labels={"value": "Atıf Sayısı", "variable": "Kurum", "year": "Yıl"}
        )
        return dcc.Graph(figure=fig)

    if tab == "q3":
        fig_min = px.bar(
            q3_pdf,
            x="ministry_name",
            y=["total_eq_questions", "unanswered_eq_questions"],
            barmode="group",
            title="Q3 – Depremle İlgili Yazılı Soru Önergeleri (Bakanlığa Göre)",
            labels={"value": "Önerge Sayısı", "variable": "Tür", "ministry_name": "Bakanlık"}
        )
        fig_kw = px.bar(
            q3_kw_pdf.sort_values("count", ascending=True).tail(20),
            x="count",
            y="word",
            orientation="h",
            title=(
                "Cevaplanmamış Önergelerde En Sık Kelimeler\n"
                "(Çevre, Şehircilik ve İklim Değişikliği Bakanlığı)"
            ),
            labels={"count": "Frekans", "word": "Anahtar Kelime"}
        )
        return html.Div([
            dcc.Graph(figure=fig_min),
            dcc.Graph(figure=fig_kw),
        ])

    if tab == "q4":
        top_prov = q4_pdf.sort_values("total_motions", ascending=False).head(15)
        fig = px.bar(
            top_prov,
            x="province",
            y=["stray_motions", "agri_motions", "eqprep_motions"],
            barmode="group",
            title=(
                "Q4 – İllere Göre Araştırma Önergeleri "
                "(Sokak Hayvanları / Tarım / Deprem Hazırlığı)"
            ),
            labels={"value": "Araştırma Önergesi Sayısı", "variable": "Konu", "province": "İl"}
        )
        return dcc.Graph(figure=fig)

    if tab == "q5":
        fig = px.line(
            q5_pdf,
            x="year",
            y="max_penalty_tl",
            markers=True,
            title="Q5 – Hazır Beton / Teknik İhlaller İçin Azami İdari Para Cezası",
            labels={"year": "Yıl", "max_penalty_tl": "Azami Ceza (TL)"}
        )
        fig2 = px.bar(
            q5_pdf,
            x="year",
            y="num_penalty_clauses",
            title="İlgili Ceza Hükmü Sayısı",
            labels={"year": "Yıl", "num_penalty_clauses": "Ceza Maddesi Sayısı"}
        )
        return html.Div([
            dcc.Graph(figure=fig),
            dcc.Graph(figure=fig2),
        ])

    if tab == "q6":
        fig = px.bar(
            q6_pdf,
            x="year",
            y=[
                "laws_with_tax_exemption",
                "laws_with_debt_restructuring",
                "laws_with_deferral",
                "laws_with_writeoff",
            ],
            barmode="group",
            title="Q6 – Afet Bölgesine Yönelik Vergi / Borç Düzenlemeleri (Yıllara Göre)",
            labels={"value": "Yasa Sayısı", "variable": "Düzenleme Türü", "year": "Yıl"}
        )
        return dcc.Graph(figure=fig)

    return html.P("Tab seçin.")


if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=8050)

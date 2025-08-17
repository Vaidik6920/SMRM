from typing import List
import streamlit as st

def generate_custom_html_table(data: List[dict], columns: List[str], show_footer=True):
    style = """
    <style>
        table.custom-table {
            border-collapse: collapse;
            width: 100%;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            margin: 20px 0;
        }

        table.custom-table th {
            background-color: #f59e0b;
            color: white;
            text-align: center;
            padding: 10px;
            font-weight: bold;
            font-size: 15px;
            border-bottom: 2px solid #333;
        }

        table.custom-table thead tr:nth-child(2) th {
            background-color: #fff4e5;
            color: #333;
            font-size: 14px;
            border-bottom: 1px solid #ccc;
        }

        table.custom-table td {
            padding: 10px;
            text-align: center;
            font-size: 14px;
            vertical-align: middle;
            border-bottom: 1px solid #eee;
        }

        table.custom-table td.platform-cell {
            background-color: #f5f5f5;
        }

        .gold { color: #DAA520; font-weight: bold; }
        .silver { color: #A9A9A9; font-weight: bold; }
        .bronze { color: #CD7F32; font-weight: bold; }
        .needs-effort { color: #F08080; font-weight: bold; }
        .na { font-style: italic; font-size: 12px; color: #555; }
    </style>
    """

    html = f"{style}<table class='custom-table'><thead><tr>"
    for col in columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"

    for row in data:
        html += "<tr>"
        for col in columns:
            cell_value = row[col]
            cell_class = "platform-cell" if col.lower() == "platform" else ""
            html += f"<td class='{cell_class}'>{cell_value}</td>"
        html += "</tr>"

    html += "</tbody></table>"

    if show_footer:
        html += '<p class="na">NA* - There was no activity during the time period</p>'

    st.markdown(html, unsafe_allow_html=True)

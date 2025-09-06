import sqlite3
import pandas as pd

DB_FILE = "licitaciones.db"
HTML_FILE = "index.html"

def create_html_page():
    """
    Reads data from the SQLite database and generates a static HTML file.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_FILE)
        
        # Use pandas to read data from a SQL query into a DataFrame
        # Querying the most recent 100 RFCs, ordered by closing date
        query = "SELECT codigo_externo, nombre, estado, fecha_cierre FROM rfcs ORDER BY fecha_cierre DESC LIMIT 500"
        df = pd.read_sql_query(query, conn)
        
        # Close the connection
        conn.close()

        # Convert the DataFrame to an HTML table
        # 'escape=False' allows rendering links, 'index=False' hides the DataFrame index
        # 'classes' adds CSS classes for styling
        html_table = df.to_html(escape=False, index=False, justify="left", classes="styled-table")

        # Basic HTML and CSS template
        html_content = f"""
        <html>
        <head>
            <title>Últimas Licitaciones - Mercado Público</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    margin: 40px auto;
                    max-width: 900px;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                }}
                h1 {{
                    color: #0056b3;
                }}
                .styled-table {{
                    border-collapse: collapse;
                    margin: 25px 0;
                    font-size: 0.9em;
                    width: 100%;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                }}
                .styled-table thead tr {{
                    background-color: #0056b3;
                    color: #ffffff;
                    text-align: left;
                }}
                .styled-table th, .styled-table td {{
                    padding: 12px 15px;
                }}
                .styled-table tbody tr {{
                    border-bottom: 1px solid #dddddd;
                }}
                .styled-table tbody tr:nth-of-type(even) {{
                    background-color: #f3f3f3;
                }}
                .styled-table tbody tr:last-of-type {{
                    border-bottom: 2px solid #0056b3;
                }}
            </style>
        </head>
        <body>
            <h1>Últimas 100 Licitaciones Publicadas</h1>
            {html_table}
        </body>
        </html>
        """

        # Write the HTML content to a file
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"Successfully generated '{HTML_FILE}'")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_html_page()
